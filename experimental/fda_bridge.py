"""FDA disease->product-code bridge (Option 3: hybrid auto + diagnostic ranking).

Standalone, self-contained module. Imports ONLY stdlib + requests. Imports nothing
from engine.py (frozen) or engine_widenet.py. This is the disease-aware FDA path that
completes wide-net's third citation type (FDA predicate devices), the one the generic
`search_openfda(device_name:<device-keyword>)` path cannot reach because it never sees
the disease.

Pipeline (all free; openFDA needs no key):
  1. disease term -> candidate FDA product codes, via the CLASSIFICATION endpoint,
     searching both `device_name` and `definition` for the disease phrase.
  2. RANK the candidate codes: prefer codes whose device_name names a diagnostic /
     detection / imaging / software signal (the AI-diagnostic analog we want), so
     e.g. diabetic-retinopathy prefers PIB ("Diabetic Retinopathy Detection Device")
     over OXW (an electrical stimulator that merely shares the disease word).
  3. top-N codes -> real cleared devices, via the 510(k) endpoint
     (`product_code:<CODE>`), which also returns De Novo (DEN...) grants.

Output text + status mirror engine.search_openfda's shape so this is a drop-in for the
FDA section of a grounded context. Residual off-target codes degrade safely: cite-or-flag
downstream quarantines non-analogous predicates (proven in B3).
"""

import re
import requests

HTTP_TIMEOUT = 15
FDA_BASE = "https://api.fda.gov/device"

# --- Second search axis (F3b) -------------------------------------------------
# Known AI / CAD / triage software product codes (SaMD). Their code NAMES are
# generic ("Computer-Assisted Detection", "Radiological Computer-Assisted Triage
# And Notification Software"), so a disease-name search on the classification
# endpoint never reaches them -- yet the actual devices filed under them DO name
# the disease/anatomy ("AVIEW Lung Nodule CAD", "Rapid NCCT Stroke"). Used as a
# keep-filter for the device-name axis. Extensible; seeded from F5-verified codes.
SAMD_CODES = {"OEB", "MYN", "QFM", "QAS", "LLZ", "POK", "QBS", "QDQ", "QIH", "QFR", "DQK"}

# Generic medical words that make a single-token device_name search too broad to
# be disease-specific; dropped from the anatomy-token list.
_STOP_TOKENS = {
    "disease", "diseases", "syndrome", "disorder", "disorders", "chronic",
    "acute", "primary", "secondary", "type", "malignant", "benign", "cell",
    "cells", "injury", "failure", "system", "device",
}

# device_name signals that mark a code as the AI / diagnostic / imaging analog we
# want (as opposed to a treatment/stimulator/assay that merely shares the disease
# word). Ranking preference, not a hard filter -- a disease with only a treatment
# code still returns it, just scored lower.
DIAGNOSTIC_SIGNAL = [
    "detection", "detect", "diagnostic", "diagnosis", "diagnose",
    "computer-aided", "computer-assisted", "computer aided", "computer assisted",
    "cad", "software", "imaging", "image", "analysis", "analyzer",
    "optical", "screening", "screen", "classifier", "classification",
    "radiolog", "quantitat", "lesion", "monitor",
]
# device_name signals that mark a code as an off-target device TYPE for an
# imaging/AI-diagnostic use case (treatment / hardware / consumable). Down-weighted.
OFFTARGET_SIGNAL = [
    "stimulator", "shock wave", "shockwave", "sealant", "catheter", "exerciser",
    "implanted", "implant", "surgical", "laser", "electrosurgical", "ablation",
    "prosthesis", "stent", "suture", "reduction", "treatment of", "therapy",
]


def _score_code(device_name):
    """Higher = more likely the diagnostic/AI analog we want to cite as a predicate."""
    dn = (device_name or "").lower()
    score = 0
    for sig in DIAGNOSTIC_SIGNAL:
        if sig in dn:
            score += 2
    for sig in OFFTARGET_SIGNAL:
        if sig in dn:
            score -= 3
    return score


def _disease_variants(disease):
    """A MeSH heading may be comma-inverted ("Carcinoma, Non-Small-Cell Lung") or
    carry a trailing qualifier ("Diabetes Mellitus, Type 2"). Expand into an ordered,
    de-duplicated list of query phrases so the natural-language form is tried:
    the de-inverted phrase FIRST ("Non-Small-Cell Lung Carcinoma"), then the raw
    heading, then the head noun before the comma. `disease_to_fda` searches each in
    order and stops at the first that yields product codes -- so a specific phrase
    wins before we fall back to a broad head noun (avoids "Carcinoma" -> bladder).
    """
    d = disease.strip()
    if not d:
        return []
    out = []
    if "," in d:
        head, _, tail = d.partition(",")
        head, tail = head.strip(), tail.strip()
        # de-inverted natural form: "<tail> <head>"  (Non-Small-Cell Lung Carcinoma)
        deinv = ("%s %s" % (tail, head)).strip()
        if deinv:
            out.append(deinv)
        out.append(d)          # raw heading
        if head:
            out.append(head)   # broad head noun, last resort
    else:
        out.append(d)
    # de-dup, preserve order
    seen, uniq = set(), []
    for p in out:
        k = p.lower()
        if k and k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


def _codes_for_phrase(phrase):
    """One phrase -> {product_code: (device_name, medical_specialty)} via classification."""
    quoted = '"%s"' % phrase.replace('"', "")
    codes = {}
    for search in ("device_name:%s" % quoted, "definition:%s" % quoted):
        try:
            r = requests.get(
                FDA_BASE + "/classification.json",
                params={"search": search, "limit": 15},
                timeout=HTTP_TIMEOUT,
            )
        except requests.RequestException:
            continue
        if not r.ok:
            continue  # 404 = valid query, zero results
        for res in r.json().get("results", []):
            pc = res.get("product_code")
            if pc and pc not in codes:
                codes[pc] = (
                    res.get("device_name", ""),
                    res.get("medical_specialty_description", ""),
                )
    return codes


def _classification_codes(disease):
    """disease -> {product_code: (device_name, medical_specialty)} candidates.

    Tries each phrase variant (de-inverted, raw, head noun) in order and returns the
    FIRST that yields any codes -- so a precise phrase beats a broad head noun.
    """
    for phrase in _disease_variants(disease):
        codes = _codes_for_phrase(phrase)
        if codes:
            return codes
    return {}


def _predicates_for_code(product_code, limit=3):
    """product_code -> up to `limit` real cleared 510(k)/De Novo devices."""
    out = []
    try:
        r = requests.get(
            FDA_BASE + "/510k.json",
            params={"search": "product_code:%s" % product_code, "limit": limit},
            timeout=HTTP_TIMEOUT,
        )
    except requests.RequestException:
        return out
    if r.ok:
        for k in r.json().get("results", []):
            out.append({
                "k_number": k.get("k_number", ""),
                "device_name": k.get("device_name", ""),
                "decision_date": k.get("decision_date", ""),
                "applicant": k.get("applicant", ""),
            })
    return out


def _anatomy_tokens(disease):
    """Meaningful single words from the disease phrase (>=4 chars, minus generic
    medical stopwords). Lets the device-name axis catch anatomy-named AI devices
    ("lung" -> "AVIEW Lung Nodule CAD") that a full-phrase search would miss."""
    out, seen = [], set()
    for t in re.findall(r"[A-Za-z]{4,}", disease or ""):
        k = t.lower()
        if k in _STOP_TOKENS or k in seen:
            continue
        seen.add(k)
        out.append(t)
    return out


def _devices_by_name(term, limit=10):
    """term -> cleared 510(k)/De Novo devices whose device_name contains `term`.
    Includes product_code so the caller can see which (often generic) code the
    device sits under -- the whole point of the second axis."""
    quoted = '"%s"' % term.replace('"', "")
    out = []
    try:
        r = requests.get(
            FDA_BASE + "/510k.json",
            params={"search": "device_name:%s" % quoted, "limit": limit},
            timeout=HTTP_TIMEOUT,
        )
    except requests.RequestException:
        return out
    if r.ok:
        for k in r.json().get("results", []):
            out.append({
                "k_number": k.get("k_number", ""),
                "device_name": k.get("device_name", ""),
                "decision_date": k.get("decision_date", ""),
                "applicant": k.get("applicant", ""),
                "product_code": k.get("product_code", ""),
            })
    return out


def _second_axis(disease, limit_per_term=10, keep=6):
    """Device-NAME axis: find AI/CAD/triage devices whose NAME contains the disease
    or an anatomy token, even when their product code is generically named
    (OEB/MYN/QAS...) and thus invisible to the classification search. Keeps only
    devices that look like the AI analog -- under a known SaMD code OR carrying a
    diagnostic signal in the name -- so a raw "lung" search doesn't drag in every
    lung device. De-dupes by k_number; ranks SaMD-coded + diagnostic first."""
    # de-dup the search terms (phrase variants + anatomy tokens), preserve order
    seen_t, terms = set(), []
    for t in _disease_variants(disease) + _anatomy_tokens(disease):
        k = t.lower()
        if k not in seen_t:
            seen_t.add(k)
            terms.append(t)

    by_k = {}
    for term in terms:
        for d in _devices_by_name(term, limit=limit_per_term):
            kn = d["k_number"]
            if not kn or kn in by_k:
                continue
            # Keep a device if it sits under a known AI/CAD/triage code, OR its name
            # carries a diagnostic signal AND it was cleared in the AI-SaMD era
            # (>=2015) -- the date floor drops pre-AI namesakes like a 1986
            # "Computer Assisted Diabetic Instruction" device.
            is_samd = d["product_code"] in SAMD_CODES
            recent = (d["decision_date"][:4] >= "2015") if d["decision_date"] else False
            if is_samd or (_score_code(d["device_name"]) > 0 and recent):
                d["match_term"] = term
                by_k[kn] = d
    devices = list(by_k.values())
    devices.sort(
        key=lambda d: (
            d["product_code"] in SAMD_CODES,
            _score_code(d["device_name"]),
            d["decision_date"],
        ),
        reverse=True,
    )
    return devices[:keep]


def disease_to_fda(disease, top_codes=3, per_code=3):
    """Main entry. Returns (text, status, meta).

    text   : formatted FDA section (drop-in for a grounded context), or "".
    status : "✅/⚠️/❌ FDA(disease-aware): ..." line.
    meta   : {"disease",
              "ranked_codes":[(code,name,specialty,score)],   # axis 1: classification codes
              "predicates":{code:[...]},                       # axis 1: 510(k)s under those codes
              "name_axis_devices":[{...}]}                     # axis 2: devices named for the disease
             -- lets the F4/F4b scorer compute precision/recall without re-parsing text.
    """
    disease = (disease or "").strip()
    if not disease:
        return "", "⚠️ FDA(disease-aware): empty disease", {
            "disease": "", "ranked_codes": [], "predicates": {}, "name_axis_devices": []}

    # Axis 1 (F3): disease -> classification product codes -> cleared predicates.
    codes = _classification_codes(disease)
    ranked = sorted(
        ((pc, dn, spec, _score_code(dn)) for pc, (dn, spec) in codes.items()),
        key=lambda t: t[3],
        reverse=True,
    )
    chosen = ranked[:top_codes]
    predicates = {}
    for pc, dn, spec, score in chosen:
        predicates[pc] = _predicates_for_code(pc, limit=per_code)

    # Axis 2 (F3b): direct device-name search -> generic-coded AI/CAD/triage devices
    # that name the disease/anatomy (the false-negative fix from F5).
    name_devices = _second_axis(disease)

    meta = {
        "disease": disease,
        "ranked_codes": chosen,
        "predicates": predicates,
        "name_axis_devices": name_devices,
    }

    lines = []
    if chosen:
        lines.append("Disease-code axis (classification -> 510(k)):")
        for pc, dn, spec, score in chosen:
            lines.append("- CODE %s | %s | panel=%s | rank=%d" % (pc, dn, spec or "?", score))
            for p in predicates[pc]:
                lines.append(
                    "    predicate %s | %s | date=%s | applicant=%s"
                    % (p["k_number"], p["device_name"], p["decision_date"], p["applicant"])
                )
    if name_devices:
        lines.append("Device-name axis (AI/CAD/triage devices naming the disease/anatomy):")
        for d in name_devices:
            lines.append(
                "- %s | %s | code=%s | date=%s | applicant=%s"
                % (d["k_number"], d["device_name"], d["product_code"],
                   d["decision_date"], d["applicant"])
            )
    text = "\n".join(lines)

    n_code_pred = sum(len(v) for v in predicates.values())
    n_name = len(name_devices)
    if n_code_pred or n_name:
        status = "✅ FDA(disease-aware): %d code-axis predicate(s) + %d name-axis device(s) for '%s'" % (
            n_code_pred, n_name, disease)
    elif chosen:
        status = "⚠️ FDA(disease-aware): %d code(s) but no cleared predicates for '%s'" % (
            len(chosen), disease)
    else:
        status = "⚠️ FDA(disease-aware): no product code or named device for '%s'" % disease
    return text, status, meta


if __name__ == "__main__":
    for d in ["diabetic retinopathy", "melanoma", "ischemic stroke", "tuberculosis"]:
        txt, st, meta = disease_to_fda(d)
        print("\n==== %s ====" % d)
        print(st)
        print(txt)
