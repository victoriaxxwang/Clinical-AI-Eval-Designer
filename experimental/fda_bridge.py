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

import requests

HTTP_TIMEOUT = 15
FDA_BASE = "https://api.fda.gov/device"

# device_name signals that mark a code as the AI / diagnostic / imaging analog we
# want (as opposed to a treatment/stimulator/assay that merely shares the disease
# word). Ranking preference, not a hard filter -- a disease with only a treatment
# code still returns it, just scored lower.
DIAGNOSTIC_SIGNAL = [
    "detection", "detect", "diagnostic", "diagnosis", "diagnose",
    "computer-aided", "computer-assisted", "computer aided", "computer assisted",
    "cad", "software", "imaging", "image", "analysis", "analyzer",
    "optical", "screening", "screen", "classifier", "classification",
    "radiolog", "assist", "quantitat", "lesion", "monitor",
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


def disease_to_fda(disease, top_codes=3, per_code=3):
    """Main entry. Returns (text, status, meta).

    text   : formatted FDA section (drop-in for a grounded context), or "".
    status : "✅/⚠️/❌ FDA(disease-aware): ..." line.
    meta   : {"disease", "ranked_codes":[(code,name,specialty,score)], "predicates":{code:[...]}}
             -- lets the F4 scorer compute precision/recall without re-parsing text.
    """
    disease = (disease or "").strip()
    if not disease:
        return "", "⚠️ FDA(disease-aware): empty disease", {"disease": "", "ranked_codes": [], "predicates": {}}

    codes = _classification_codes(disease)
    if not codes:
        return "", "⚠️ FDA(disease-aware): no product code for '%s'" % disease, {
            "disease": disease, "ranked_codes": [], "predicates": {}}

    ranked = sorted(
        ((pc, dn, spec, _score_code(dn)) for pc, (dn, spec) in codes.items()),
        key=lambda t: t[3],
        reverse=True,
    )
    chosen = ranked[:top_codes]

    lines, predicates, any_pred = [], {}, False
    for pc, dn, spec, score in chosen:
        lines.append("- CODE %s | %s | panel=%s | rank=%d" % (pc, dn, spec or "?", score))
        preds = _predicates_for_code(pc, limit=per_code)
        predicates[pc] = preds
        for p in preds:
            any_pred = True
            lines.append(
                "    predicate %s | %s | date=%s | applicant=%s"
                % (p["k_number"], p["device_name"], p["decision_date"], p["applicant"])
            )
    meta = {"disease": disease, "ranked_codes": chosen, "predicates": predicates}
    text = "\n".join(lines)
    n_codes = len(chosen)
    n_pred = sum(len(v) for v in predicates.values())
    if any_pred:
        status = "✅ FDA(disease-aware): %d code(s), %d predicate device(s) for '%s'" % (
            n_codes, n_pred, disease)
    else:
        status = "⚠️ FDA(disease-aware): %d code(s) but no cleared predicates for '%s'" % (
            n_codes, disease)
    return text, status, meta


if __name__ == "__main__":
    for d in ["diabetic retinopathy", "melanoma", "ischemic stroke", "tuberculosis"]:
        txt, st, meta = disease_to_fda(d)
        print("\n==== %s ====" % d)
        print(st)
        print(txt)
