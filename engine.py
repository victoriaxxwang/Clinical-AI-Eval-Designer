"""
Core Deterministic Engine
=========================

The Phase-1 retrieval layer, deliberately kept free of any Streamlit / UI code so
it can be unit-tested and reused by future Phase-2 agents. Everything here is a
pure function of its inputs plus deterministic public-API calls: same input →
same query → same records.

Public API:
    build_queries(model_desc, use_case, population, setting="", mesh=None) -> dict
    normalize_mesh(candidates)  -> {descriptor_id, preferred, synonyms, input} | None
    search_clinicaltrials(term) -> (text, status)
    search_openfda(keyword)        -> (text, status)  # device classification + 510(k)
    search_openfda_safety(keyword) -> (text, status)  # PMA + MAUDE adverse events + recalls
    search_openfda_drug(keyword)   -> (text, status)  # Drugs@FDA + SPL labeling + FAERS
    search_pubmed(term)         -> (text, status)
    search_europepmc(term)      -> (text, status)
    search_literature(term, bool_term=None) -> (text, status)  # EuropePMC + OpenAlex + S2, merged
    crossref_verify(doi)        -> True | False | None
    coverage_gaps_note()        -> str
    fetch_url_text(url)         -> (text, status|None)
    build_grounded_context(model_desc, use_case, population, optional_url="", setting="",
                           intervention_type="device")
        -> (context_text, statuses, retrieval_timestamp)
        # the Phase-1 "source records" half of the bundle, plus the UTC snapshot time.
        # intervention_type routes the FDA search: "device" (default) → classification/
        # 510(k)/PMA/MAUDE/recall; "drug" → Drugs@FDA/label/FAERS; "both" → all.
"""

import datetime
import time
from html.parser import HTMLParser

import requests

HTTP_TIMEOUT = 12  # seconds per registry call

# The assembled grounding context is a snapshot handed to the model. The cap is
# generous (~5k tokens) because each section is already independently bounded
# (CT ≤ 6 studies, openFDA per-term budget, literature capped); the ceiling only
# guards a pathological reference-URL. Larger than the old 9000 so a wide-but-
# legitimate sweep (all sections + metadata + coverage note) is never truncated.
CONTEXT_CAP = 20000

# MeSH normalization: the condition term is expanded to at most this many terms
# (canonical MeSH heading + top entry-term synonyms) in the literature/trial query.
# Bounded so the OR-group stays small and every AND-ed method term still matters.
MESH_MAX_TERMS = 5

# Polite-pool identification for Crossref (asks for a UA with contact info).
_CROSSREF_UA = ("ClinicalAIEvalDesigner/1.0 "
                "(+https://github.com/victoriaxxwang/clinical-ai-eval-designer)")

# OpenAlex/Crossref "polite pool" contact — a noreply address is the convention
# for identifying an automated client and getting the faster, rate-limited pool.
_POLITE_MAILTO = "clinical-ai-eval-designer@users.noreply.github.com"

# Filler words stripped from queries so registry searches focus on real signal.
_STOP = {
    "the", "a", "an", "and", "or", "of", "for", "to", "in", "on", "with", "from",
    "that", "were", "was", "is", "are", "be", "by", "using", "use", "used",
    "routine", "unrelated", "reasons", "reason", "originally", "performed",
    "detect", "detects", "detection", "quantify", "quantifies", "predict",
    "predicts", "model", "models", "algorithm", "tool", "based", "via", "e.g",
    "patients", "patient", "adults", "adult",
    # action verbs — never a good device keyword
    "infer", "infers", "inferred", "classify", "classifies", "estimate",
    "estimates", "flag", "flags", "identify", "identifies", "measure",
    "measures", "assess", "assesses", "predicting", "detecting",
    # generic, non-distinctive nouns — poor device/modality keywords
    "color", "colour", "image", "images", "photograph", "photographs",
    "scan", "scans", "data", "system", "software", "signal", "signals",
    "device", "devices",
}


# Recognized imaging / sensor / device modalities. When one of these appears in
# the model description it is the best openFDA device keyword, so it is preferred
# over a generic anatomy/finding word. Domain-agnostic: covers the common
# modalities across specialties, not any single disease.
_MODALITY = {
    "photoplethysmography", "ppg", "ecg", "ekg", "electrocardiogram", "eeg",
    "emg", "ct", "mri", "ultrasound", "echocardiography", "echocardiogram",
    "fundus", "oct", "dermoscopy", "spirometry", "oximeter", "oximetry",
    "accelerometer", "wearable", "optical", "sensor", "radiograph", "radiography",
    "mammography", "mammogram", "endoscopy", "colonoscopy", "histopathology",
    "pathology", "capnography", "electrode", "patch", "biosensor",
}


def _clean(text, limit):
    return " ".join((text or "").split())[:limit]


def _keywords(text, n):
    """Deterministic keyword extraction: lowercase, de-punctuate, drop stopwords
    and short tokens, de-dup preserving order, keep the first ``n``."""
    out, seen = [], set()
    normalized = (text or "").replace("-", " ").replace("/", " ")
    for raw in normalized.split():
        t = raw.strip(".,;:()[]{}\"'").lower()
        if len(t) <= 2 or t in _STOP or t in seen:
            continue
        seen.add(t)
        out.append(t)
        if len(out) >= n:
            break
    return out


def _mesh_candidates(use_case, model_desc, anchor_tokens=(), bare_tokens=None,
                     max_candidates=5):
    """Ordered list of condition phrases to try against MeSH, most-specific first.

    MeSH headings are often multi-word ("Myocardial Infarction", "Lung Neoplasms",
    "Stress, Psychological", "Diabetic Retinopathy"), so the candidates are ANCHORED
    on the condition tokens and paired with an adjacent qualifier to form a bigram —
    "stress" + "psychological" → "psychological stress" (resolves to Stress,
    Psychological), where the bare word "stress" is ambiguous and resolves to nothing.
    Anchoring on the condition — rather than taking every consecutive word pair — also
    avoids junk bigrams like "daily life" accidentally resolving to an unrelated
    heading (Activities of Daily Living).

    ``anchor_tokens`` are the words a bigram must touch (the shared concept, or the
    model's clinical terms when the use case is too terse to name the condition, e.g.
    "DR screening"). ``bare_tokens`` — the single-word fallbacks tried after the
    bigrams — are kept NARROW (shared / use_case only, defaulting to ``anchor_tokens``)
    so generic model words like "lead" or "skin" can't resolve to an organ/substance
    heading. use_case bigrams are tried before model bigrams (declared indication
    first). Kept pure/offline: the lookup itself is ``normalize_mesh``. Returns ``[]``
    (→ no lookup) when there is nothing to anchor on."""
    anchor = {t for t in (anchor_tokens or []) if t}
    bare = [t for t in (bare_tokens if bare_tokens is not None else anchor_tokens) if t]
    if not anchor and not bare:
        return []
    uc = _keywords(use_case, 8)
    md = _keywords(model_desc, 8)
    cands = []

    def add(x):
        if x and len(x) > 2 and x not in cands:
            cands.append(x)

    # condition-anchored bigrams (a condition token + its adjacent qualifier),
    # use_case first (declared indication), then model description (precise phrase).
    for seq in (uc, md):
        for a, b in zip(seq, seq[1:]):
            if a in anchor or b in anchor:
                add(f"{a} {b}")
    for t in bare:                             # then the bare condition tokens
        add(t)
    return cands[:max_candidates]


def build_queries(model_desc, use_case, population="", setting="", mesh=None):
    """Route each registry to a focused, deterministic query.

    - ClinicalTrials.gov / PubMed: the top few disease + modality keywords
      (filler removed). Kept deliberately short — every extra term is AND-ed by
      these APIs, so more terms means *lower* recall, not higher precision.
    - openFDA: a single strongest device keyword (token match works far better
      than a full phrase against `device_name`).
    - `population` is intentionally NOT used as a retrieval filter: qualifiers
      like "untrained general adults" over-constrain the search to zero hits.
      Population drives the model's subgroup reasoning instead (passed in the
      prompt), which is where it actually belongs.
    - `setting` (the deployment context, e.g. "consumer wellness app") IS used —
      but only for openFDA, not literature. The setting is the strongest signal
      for the *regulatory class*: "consumer wellness" → the openFDA "wellness"
      device_name → the General-Wellness product code (PWC), which is the correct
      primary regulatory bucket for a non-diagnostic consumer tool. Kept out of
      the literature query (like population, it over-constrains ranked search).
    - `mesh` (optional): a resolved MeSH heading from ``normalize_mesh``. When given,
      the literature/trial query is rebuilt around the canonical heading + its
      synonyms (see the expansion block below); when None, queries are unchanged.
      The dict always also returns ``mesh_candidates`` (what to look up) and
      ``lit_bow`` (the relevance-provider query form).
    """
    # The condition/target vs the method/modality. The condition is what the model
    # and the use case SHARE (e.g. "stress"); the method/modality is what is
    # DISTINCTIVE to the model description (e.g. "photoplethysmography"). A good
    # literature query needs BOTH — the old "top-4 of use_case+model" filled up on
    # use-case filler ("continuous passive daily") and dropped the real subject.
    model_kws = _keywords(model_desc, 12)   # cap raised so modality terms survive
    uc_kws = _keywords(use_case, 8)
    model_set, uc_set = set(model_kws), set(uc_kws)
    shared = [k for k in uc_kws if k in model_set]          # the condition/target
    distinctive = [k for k in model_kws if k not in uc_set]  # the method/modality

    # Literature / trials query = condition first, then method. Capped at 4 tokens:
    # each extra term is AND-ed by these APIs, so more terms means *lower* recall.
    ordered = []
    for k in shared + distinctive + uc_kws + model_kws:  # fallback chain → never empty
        if k and k not in ordered:
            ordered.append(k)
        if len(ordered) >= 4:
            break
    query = _clean(" ".join(ordered), 200)

    # openFDA device keyword: prefer a recognized modality among the distinctive
    # terms (a PPG stress model → "photoplethysmography", not "stress"). `fda` is
    # the single best keyword (back-compat); `fda_terms` is a small multi-term
    # sweep so the regulatory *landscape* is retrieved, not one narrow record —
    # all terms derived from the input (disease-agnostic, nothing hardcoded).
    device = (
        next((k for k in distinctive if k in _MODALITY), "")
        or (distinctive[0] if distinctive else "")
        or (model_kws[0] if model_kws else "")
        or (uc_kws[0] if uc_kws else "")
    )
    modality_terms = [k for k in distinctive if k in _MODALITY]
    # Setting keywords ("consumer wellness" → "consumer", "wellness") drive the
    # REGULATORY CLASS more than any device term: "wellness" surfaces the
    # General-Wellness product code (PWC), the correct bucket for a non-diagnostic
    # consumer tool. Given high priority (right after the device) so they aren't
    # crowded out of the capped sweep. Disease-agnostic — derived from the input.
    setting_kws = _keywords(setting, 3)
    fda_terms = []
    # device modality first, then SETTING (regulatory class), then the CONDITION
    # (shared term — surfaces the condition's own device class, e.g. "stress" →
    # biofeedback code), then the remaining modality/distinctive terms.
    for k in [device] + setting_kws + shared + modality_terms + distinctive:
        if k and k not in fda_terms:
            fda_terms.append(k)
        if len(fda_terms) >= 5:
            break

    # Drug/biologic keyword sweep — used only when the intervention type includes a
    # drug/biologic (see build_grounded_context). The best drug-name candidates are
    # the DISTINCTIVE non-modality terms ("AI for warfarin dosing" → "warfarin"),
    # then the shared condition; a recognized device modality is never a drug name,
    # so it is excluded. Precise drug-name normalization (RxNorm-style) is out of
    # scope here — this is a deterministic first pass, same spirit as fda_terms.
    drug_terms = []
    for k in distinctive + shared + model_kws + uc_kws:
        if k in _MODALITY:
            continue
        if k and k not in drug_terms:
            drug_terms.append(k)
        if len(drug_terms) >= 4:
            break

    # MeSH-expanded literature/trial query. build_queries stays PURE — the network
    # lookup happens in build_grounded_context, which resolves ``mesh`` and re-calls
    # this with it. When ``mesh`` is None (no heading resolved, or lookup skipped) the
    # queries are byte-for-byte today's behavior, so retrieval never gets worse.
    #   - lit_query (ct/pubmed/Europe PMC): a boolean OR of the canonical heading +
    #     synonyms, AND-ed with the distinctive method term(s). Understood by the
    #     boolean-capable engines (CT.gov Essie, PubMed ATM, Europe PMC).
    #   - lit_bow (OpenAlex / Semantic Scholar): a plain relevance bag — canonical
    #     heading + method — since those engines rank rather than parse booleans.
    lit_query = query
    lit_bow = query
    if mesh and mesh.get("preferred"):
        cond_terms, seen = [], set()
        for t in [mesh["preferred"]] + list(mesh.get("synonyms") or []):
            if t and t.lower() not in seen:
                seen.add(t.lower())
                cond_terms.append(t)
            if len(cond_terms) >= MESH_MAX_TERMS:
                break
        # method = the distinctive specificity terms (recognized modality first),
        # AND-ed so the synonym expansion widens the CONDITION without losing focus.
        method = [k for k in distinctive if k in _MODALITY]
        method += [k for k in distinctive if k not in method]
        method = method[:2]
        cond_or = " OR ".join(f'"{t}"' for t in cond_terms)
        lit_query = f"({cond_or}) AND {' AND '.join(method)}" if method else cond_or
        lit_bow = _clean(" ".join([mesh["preferred"]] + method), 200)

    # Condition anchor for MeSH: prefer the shared concept; when the model and use
    # case share nothing (a terse use_case like "DR screening"), anchor bigrams on
    # the model's non-modality clinical terms so the real condition ("diabetic
    # retinopathy", "atrial fibrillation") is still found. Bare-token fallback stays
    # narrow (shared / use_case) so generic model words can't mis-resolve.
    non_modality_distinctive = [k for k in distinctive if k not in _MODALITY]
    mesh_anchor = shared or non_modality_distinctive
    mesh_bare = shared or uc_kws

    return {
        "ct": lit_query,
        "pubmed": lit_query,
        "fda": device,
        "fda_terms": fda_terms or ([device] if device else []),
        "drug_terms": drug_terms or ([device] if device else []),
        "lit_bow": lit_bow,
        "mesh_candidates": _mesh_candidates(use_case, model_desc, mesh_anchor, mesh_bare),
    }


def _eutils_mesh_get(endpoint, params):
    """GET one NCBI E-utilities MeSH endpoint, respecting the un-keyed 3 req/sec
    rate limit: a short pre-call delay keeps a multi-candidate sweep under the cap,
    and a single retry recovers from a transient 429 (throttle) instead of losing the
    candidate. Raises ``requests.RequestException`` if it still fails, so the caller
    degrades gracefully to raw keywords. (One condition lookup per generation, so the
    added delay is ~1s against a ~90s run.)"""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{endpoint}.fcgi"
    for attempt in range(2):
        time.sleep(0.34)  # ≤ 3 requests/second (un-keyed E-utilities limit)
        r = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
        if r.status_code == 429 and attempt == 0:
            time.sleep(0.75)
            continue
        r.raise_for_status()
        return r
    raise requests.HTTPError("NCBI E-utilities rate-limited (429) after one retry")


def normalize_mesh(candidates):
    """Map a clinical CONDITION to its canonical NLM MeSH heading + entry-term
    synonyms, so the literature/trial search covers the concept regardless of the
    wording the user typed ("heart attack" → "Myocardial Infarction" + synonyms;
    "lung cancer" → "Lung Neoplasms"). This is the one query-changing breadth item:
    it normalizes the CONDITION only (not device/drug keywords — those aren't MeSH's
    job), leaving every other retrieval path untouched.

    ``candidates`` is the ordered phrase list from ``_mesh_candidates`` (bigrams
    first). Each is resolved via NCBI E-utilities against the MeSH database with a
    FIELD-QUALIFIED query — ``"{term}"[MeSH Terms]`` — which matches the controlled
    vocabulary EXACTLY (entry-term synonyms included). That exact-match is what makes
    this safe: a real heading resolves cleanly, while an ambiguous or non-MeSH token
    (bare "stress", "MI", "afib") resolves to nothing and is skipped rather than
    mis-mapped to a garbage heading (an unqualified search ranks "stress" onto
    "Protein Aggregation" — exactly what we must avoid). The first candidate that
    resolves wins, so the result is deterministic.

    Returns ``{"descriptor_id", "preferred", "synonyms": [...], "input"}`` or None
    when nothing resolves / the lookup is unreachable. None means "use the raw
    keywords" — this normalization can only ADD precision, never make the query
    worse. Only two HTTP calls per generation (one esearch + one esummary) on the
    first hit, so it is well within NCBI's un-keyed rate limit.
    """
    for cand in (candidates or []):
        cand = (cand or "").strip()
        if len(cand) <= 2:
            continue
        try:
            r = _eutils_mesh_get("esearch", {"db": "mesh", "retmode": "json",
                                             "term": f'"{cand}"[MeSH Terms]', "retmax": 1})
            ids = r.json().get("esearchresult", {}).get("idlist", []) or []
            if not ids:
                continue  # not an exact MeSH term → try the next candidate
            r2 = _eutils_mesh_get("esummary", {"db": "mesh", "id": ids[0], "retmode": "json"})
            item = (r2.json().get("result", {}) or {}).get(ids[0], {}) or {}
            terms = [t for t in (item.get("ds_meshterms") or []) if t]
            descriptor = item.get("ds_meshui", "") or ""
            # Accept only main headings (D…) and supplementary concept records (C…),
            # which are real conditions. Reject qualifiers/subheadings (Q…, e.g.
            # "screening" maps to the subheading "diagnosis") and anything else — a
            # subheading is never a condition and would misground the query.
            if not terms or descriptor[:1] not in ("D", "C"):
                continue
            preferred = terms[0]
            synonyms, seen = [], {preferred.lower()}
            for t in terms[1:]:
                if t.lower() in seen:
                    continue
                seen.add(t.lower())
                synonyms.append(t)
                if len(synonyms) >= MESH_MAX_TERMS - 1:
                    break
            return {"descriptor_id": descriptor, "preferred": preferred,
                    "synonyms": synonyms, "input": cand}
        except (requests.RequestException, ValueError):
            # network error or malformed JSON → try the next candidate, else give up
            continue
    return None


def search_clinicaltrials(term, max_studies=6):
    if not term:
        return "", "⚠️ ClinicalTrials.gov: empty query"
    try:
        r = requests.get(
            "https://clinicaltrials.gov/api/v2/studies",
            params={"query.term": term, "pageSize": max_studies},
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        studies = r.json().get("studies", [])
        if not studies:
            return "", "⚠️ ClinicalTrials.gov: no matching studies"
        lines = []
        for s in studies:
            ps = s.get("protocolSection", {})
            idm = ps.get("identificationModule", {})
            dm = ps.get("designModule", {})
            design = dm.get("designInfo", {})
            primary = "; ".join(
                o.get("measure", "")
                for o in ps.get("outcomesModule", {}).get("primaryOutcomes", []) or []
            )
            lines.append(
                f"- {idm.get('nctId','')} | {idm.get('briefTitle','')} "
                f"| status={ps.get('statusModule',{}).get('overallStatus','')} "
                f"| type={dm.get('studyType','')} phases={', '.join(dm.get('phases',[]) or [])} "
                f"| n={dm.get('enrollmentInfo',{}).get('count','')} "
                f"| allocation={design.get('allocation','')} "
                f"masking={design.get('maskingInfo',{}).get('masking','')} "
                f"| primary_outcomes={_clean(primary, 300)}"
            )
        return "\n".join(lines), f"✅ ClinicalTrials.gov: {len(studies)} studies"
    except requests.Timeout:
        return "", "❌ ClinicalTrials.gov: timed out"
    except requests.RequestException:
        return "", "❌ ClinicalTrials.gov: request failed"


def search_openfda(keyword, max_results=3, per_term=3):
    """Query openFDA device classification + 510(k). `keyword` may be a single
    string or a list of terms; a list sweeps the regulatory landscape (each term
    can surface a different product code) instead of one narrow record. Records
    are de-duplicated by product code / K-number so overlapping terms don't repeat.

    Every term is queried against BOTH endpoints, but each term contributes at
    most `per_term` records. This per-term fairness is deliberate: a broad,
    generic term (e.g. "consumer") must not consume the whole budget and starve a
    later, more specific term (e.g. "wellness" → the General-Wellness code, or
    "stress" → the biofeedback code). It also bounds the section size so a wide
    sweep can't crowd the other registries out of the length-limited context.
    """
    terms = [keyword] if isinstance(keyword, str) else list(keyword or [])
    terms = [t for t in terms if t]
    if not terms:
        return "", "⚠️ openFDA: empty query"
    endpoints = (
        ("classification", "CLASSIFICATION", "product_code",
         lambda x: f"| product_code={x.get('product_code','')} | class={x.get('device_class','')} "
                   f"| regulation={x.get('regulation_number','')} | panel={x.get('medical_specialty_description','')}"),
        ("510k", "510(k)", "k_number",
         lambda x: f"| k_number={x.get('k_number','')} | decision={x.get('decision_description','')} "
                   f"| date={x.get('decision_date','')} | applicant={x.get('applicant','')}"),
    )
    out, ok, seen = [], False, set()
    # term-outer / endpoint-inner, with a per-term budget so every priority term
    # is represented (device + setting + condition all get queried).
    for term in terms:
        term_count = 0
        for endpoint, label, key, fields in endpoints:
            if term_count >= per_term:
                break
            try:
                r = requests.get(
                    f"https://api.fda.gov/device/{endpoint}.json",
                    params={"search": f"device_name:{term}", "limit": max_results},
                    timeout=HTTP_TIMEOUT,
                )
                if r.ok:
                    ok = True
                    for res in r.json().get("results", []):
                        if term_count >= per_term:
                            break
                        dedup = res.get(key, "") or res.get("device_name", "")
                        if dedup in seen:
                            continue
                        seen.add(dedup)
                        out.append(f"- {label} | {res.get('device_name','')} {fields(res)}")
                        term_count += 1
                elif r.status_code == 404:
                    ok = True  # openFDA returns 404 for a valid query with zero results
            except requests.RequestException:
                pass
    if out:
        return "\n".join(out), f"✅ openFDA: {len(out)} device records"
    if ok:
        return "", "⚠️ openFDA: no matching device records"
    return "", "❌ openFDA: request failed"


def search_openfda_safety(keyword, max_results=5, per_endpoint=2):
    """Query openFDA's POST-MARKET + Class III device endpoints — the safety half
    of the regulatory landscape that classification/510(k) (``search_openfda``)
    does not cover:

      - PMA    (``/device/pma.json``)         — Class III premarket approvals, the
                                                highest-risk (most-scrutinized) pathway.
      - MAUDE  (``/device/event.json``)       — adverse-event reports: the real-world
                                                malfunction / injury signal a validation
                                                spec's post-deployment monitoring needs.
      - Recall (``/device/enforcement.json``) — recall / enforcement actions.

    ``keyword`` may be a single term or a list (the ``fda_terms`` sweep). Records are
    de-duplicated by each endpoint's natural key (PMA number / MDR report number /
    recall number). The loop is endpoint-outer / term-inner with a ``per_endpoint``
    cap so (a) every endpoint is represented — PMA is usually sparse (few devices are
    Class III), so a shared budget would let 510(k)-style noise starve MAUDE/recall —
    and (b) the section stays bounded (≤ 3 × per_endpoint records) under the context
    cap. Each call is its own try/except so one endpoint's outage never blanks the
    section; it fails only if EVERY endpoint is unreachable. These records feed the
    spec's safety / post-market-surveillance reasoning, never its efficacy claims.
    """
    terms = [keyword] if isinstance(keyword, str) else list(keyword or [])
    terms = [t for t in terms if t]
    if not terms:
        return "", "⚠️ openFDA safety: empty query"
    endpoints = (
        ("pma", "PMA", "generic_name", "pma_number",
         lambda x: x.get("trade_name") or x.get("generic_name")
                   or (x.get("openfda", {}) or {}).get("device_name", "") or "",
         lambda x: f"| pma_number={x.get('pma_number','')} "
                   f"| supplement={x.get('supplement_number','')} "
                   f"| decision={x.get('decision_code','')} | date={x.get('decision_date','')} "
                   f"| product_code={x.get('product_code','')} | applicant={x.get('applicant','')}"),
        ("event", "MAUDE", "device.generic_name", "report_number",
         lambda x: (((x.get("device") or [{}]) or [{}])[0].get("generic_name")
                    or ((x.get("device") or [{}]) or [{}])[0].get("brand_name") or ""),
         lambda x: f"| event_type={x.get('event_type','')} "
                   f"| date_received={x.get('date_received','')} "
                   f"| report_number={x.get('report_number','')}"),
        ("enforcement", "Recall", "product_description", "recall_number",
         lambda x: x.get("product_description", "") or "",
         lambda x: f"| classification={x.get('classification','')} "
                   f"| status={x.get('status','')} "
                   f"| reason={_clean(x.get('reason_for_recall',''), 160)} "
                   f"| firm={x.get('recalling_firm','')} "
                   f"| date={x.get('recall_initiation_date','')} "
                   f"| recall_number={x.get('recall_number','')}"),
    )
    out, ok, seen = [], False, set()
    for endpoint, label, field, key, name_fn, fields in endpoints:
        ep_count = 0
        for term in terms:
            if ep_count >= per_endpoint:
                break
            try:
                r = requests.get(
                    f"https://api.fda.gov/device/{endpoint}.json",
                    params={"search": f"{field}:{term}", "limit": max_results},
                    timeout=HTTP_TIMEOUT,
                )
                if r.ok:
                    ok = True
                    for res in r.json().get("results", []):
                        if ep_count >= per_endpoint:
                            break
                        ident = res.get(key, "")
                        dedup = f"{label}:{ident}"
                        if not ident or dedup in seen:
                            continue
                        seen.add(dedup)
                        out.append(f"- {label} | {_clean(name_fn(res), 120)} {fields(res)}")
                        ep_count += 1
                elif r.status_code == 404:
                    ok = True  # openFDA returns 404 for a valid query with zero results
            except requests.RequestException:
                pass
    if out:
        return "\n".join(out), f"✅ openFDA safety: {len(out)} PMA/MAUDE/recall records"
    if ok:
        return "", "⚠️ openFDA safety: no matching PMA/MAUDE/recall records"
    return "", "❌ openFDA safety: request failed"


def search_openfda_drug(keyword, max_results=5, per_endpoint=2):
    """Query openFDA's DRUG / BIOLOGIC endpoints — the drug analog of the device
    classification/PMA/MAUDE sweep, used when the clinical AI's intervention IS (or
    acts on) a drug or biologic rather than a device:

      - Drugs@FDA (``/drug/drugsfda.json``) — approved products (NDA/BLA/ANDA
                                              application, sponsor, marketing status):
                                              the approval-pathway anchor.
      - SPL label (``/drug/label.json``)    — Structured Product Labeling: the approved
                                              indication + any boxed warning (the on-label
                                              claim and its known, labeled risks).
      - FAERS     (``/drug/event.json``)    — FDA Adverse Event Reporting System: the
                                              post-market adverse-event signal (the drug
                                              analog of MAUDE) for monitoring reasoning.

    Same contract as ``search_openfda_safety`` — ``keyword`` is a term or list (the
    ``drug_terms`` sweep); records are de-duplicated by each endpoint's natural key
    (application number / SPL id / safety-report id); the loop is endpoint-outer /
    term-inner with a ``per_endpoint`` cap so a chatty FAERS can't starve the sparser
    Drugs@FDA/label; and each call is its own try/except so one endpoint's outage never
    blanks the section — it fails only if EVERY endpoint is unreachable. These records
    feed the spec's regulatory, labeling, and safety reasoning, never an efficacy claim
    on their own. NOTE the base path is ``/drug/`` (not ``/device/``); the drug ``event``
    endpoint is FAERS, distinct from the device ``event`` endpoint (MAUDE).
    """
    terms = [keyword] if isinstance(keyword, str) else list(keyword or [])
    terms = [t for t in terms if t]
    if not terms:
        return "", "⚠️ openFDA drug: empty query"
    endpoints = (
        ("drugsfda", "Drugs@FDA", "openfda.generic_name", "application_number",
         lambda x: (((x.get("openfda", {}) or {}).get("brand_name") or [""])[0]
                    or ((x.get("openfda", {}) or {}).get("generic_name") or [""])[0]
                    or (((x.get("products") or [{}]) or [{}])[0].get("brand_name", "")) or ""),
         lambda x: f"| application={x.get('application_number','')} "
                   f"| sponsor={x.get('sponsor_name','')} "
                   f"| status={(((x.get('products') or [{}]) or [{}])[0].get('marketing_status',''))} "
                   f"| route={(((x.get('products') or [{}]) or [{}])[0].get('route',''))} "
                   f"| substance={(((x.get('openfda', {}) or {}).get('substance_name') or [''])[0])}"),
        ("label", "SPL label", "openfda.generic_name", "id",
         lambda x: (((x.get("openfda", {}) or {}).get("brand_name") or [""])[0]
                    or ((x.get("openfda", {}) or {}).get("generic_name") or [""])[0] or ""),
         lambda x: f"| indications={_clean(((x.get('indications_and_usage') or ['']) or [''])[0], 160)} "
                   f"| boxed_warning={'YES' if x.get('boxed_warning') else 'no'} "
                   f"| application={(((x.get('openfda', {}) or {}).get('application_number') or [''])[0])} "
                   f"| spl_id={x.get('id','')}"),
        ("event", "FAERS", "patient.drug.openfda.generic_name", "safetyreportid",
         # A FAERS report often lists several drugs (suspect + concomitant); show the
         # whole set, not just drug[0], so the queried drug is actually visible and it
         # is clear the record is a co-report — displaying one arbitrary drug name
         # (which may be a concomitant, not the searched one) would misgrounds the spec.
         lambda x: "; ".join(
             d.get("medicinalproduct", "")
             for d in (((x.get("patient", {}) or {}).get("drug")) or [])
             if d.get("medicinalproduct")) or "",
         lambda x: f"| serious={x.get('serious','')} "
                   f"| reactions={_clean('; '.join(r.get('reactionmeddrapt', '') for r in (((x.get('patient', {}) or {}).get('reaction')) or [])), 120)} "
                   f"| date={x.get('receivedate','')} "
                   f"| safetyreport={x.get('safetyreportid','')}"),
    )
    out, ok, seen = [], False, set()
    for endpoint, label, field, key, name_fn, fields in endpoints:
        ep_count = 0
        for term in terms:
            if ep_count >= per_endpoint:
                break
            try:
                r = requests.get(
                    f"https://api.fda.gov/drug/{endpoint}.json",
                    params={"search": f"{field}:{term}", "limit": max_results},
                    timeout=HTTP_TIMEOUT,
                )
                if r.ok:
                    ok = True
                    for res in r.json().get("results", []):
                        if ep_count >= per_endpoint:
                            break
                        ident = res.get(key, "")
                        dedup = f"{label}:{ident}"
                        if not ident or dedup in seen:
                            continue
                        seen.add(dedup)
                        out.append(f"- {label} | {_clean(name_fn(res), 120)} {fields(res)}")
                        ep_count += 1
                elif r.status_code == 404:
                    ok = True  # openFDA returns 404 for a valid query with zero results
            except requests.RequestException:
                pass
    if out:
        return "\n".join(out), f"✅ openFDA drug: {len(out)} Drugs@FDA/label/FAERS records"
    if ok:
        return "", "⚠️ openFDA drug: no matching Drugs@FDA/label/FAERS records"
    return "", "❌ openFDA drug: request failed"


def search_pubmed(term, max_results=15):
    if not term:
        return "", "⚠️ PubMed: empty query"
    try:
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pubmed", "term": term, "retmode": "json",
                    "retmax": max_results, "sort": "relevance"},
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return "", "⚠️ PubMed: no matching articles"
        r2 = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
            timeout=HTTP_TIMEOUT,
        )
        r2.raise_for_status()
        result = r2.json().get("result", {})
        lines = []
        for pid in result.get("uids", []):
            item = result.get(pid, {})
            journal = item.get("fulljournalname") or item.get("source", "")
            year = (item.get("pubdate", "") or "")[:4]
            lines.append(f"- PMID {pid} | {_clean(item.get('title',''), 250)} | {journal} {year}")
        return "\n".join(lines), f"✅ PubMed: {len(lines)} articles"
    except requests.Timeout:
        return "", "❌ PubMed: timed out"
    except requests.RequestException:
        return "", "❌ PubMed: request failed"


def crossref_verify(doi):
    """Check that a DOI actually resolves in Crossref's registry.

    Returns True (resolves), False (Crossref explicitly reports it unknown — a 404),
    or None (Crossref unreachable / any other response). None means "can't tell", so
    the caller keeps the citation rather than punishing infra flakiness — only a
    definitive 404 is treated as "this DOI does not resolve". Uses the lightweight
    ``/works/{doi}/agency`` endpoint (registration-agency lookup) to avoid pulling
    full metadata just to confirm existence.
    """
    if not doi:
        return None
    try:
        r = requests.get(
            f"https://api.crossref.org/works/{doi}/agency",
            timeout=HTTP_TIMEOUT,
            headers={"User-Agent": _CROSSREF_UA},
        )
        if r.status_code == 404:
            return False
        if r.ok:
            return True
        return None
    except requests.RequestException:
        return None


def _normalize_doi(doi):
    """Canonicalize a DOI so the same paper from different providers dedupes to one
    key: strip any resolver prefix (OpenAlex returns the full ``https://doi.org/…``
    URL; Europe PMC / Semantic Scholar return the bare DOI) and lowercase (DOIs are
    case-insensitive). Returns '' for a falsy input."""
    if not doi:
        return ""
    d = str(doi).strip().lower()
    for p in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/",
              "http://dx.doi.org/", "doi:"):
        if d.startswith(p):
            d = d[len(p):]
            break
    return d


# --- Literature providers: each returns a list of uniform record dicts ---------
# A record is {pmid, doi, title, journal, year, source_db, alt_id}. Keeping the
# providers as pure record-returning functions (rather than pre-formatted text) is
# what lets search_literature() MERGE and de-duplicate across them by DOI/PMID —
# the honest version of "we searched more databases". Each may raise a
# requests.RequestException; the aggregator catches it per-provider so one outage
# never blanks the whole literature section.

def _europepmc_records(term, max_results=15):
    """Europe PMC — returns PMID + DOI (+ PMCID) in one call and indexes preprints
    (medRxiv/bioRxiv) and PMC, so its coverage is a superset of MEDLINE."""
    r = requests.get(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        params={"query": term, "format": "json", "pageSize": max_results,
                "resultType": "lite"},
        timeout=HTTP_TIMEOUT,
    )
    r.raise_for_status()
    results = r.json().get("resultList", {}).get("result", []) or []
    recs = []
    for it in results:
        recs.append({
            "pmid": it.get("pmid", "") or "",
            "doi": it.get("doi", "") or "",
            "title": it.get("title", "") or "",
            "journal": it.get("journalTitle", "") or it.get("source", "") or "",
            "year": it.get("pubYear", "") or "",
            "source_db": "Europe PMC",
            "alt_id": f"{it.get('source','')}:{it.get('id','')}",
        })
    return recs


def _openalex_records(term, max_results=15):
    """OpenAlex — a free, key-less index of ~250M works. Returns a DOI (as a full
    ``https://doi.org/…`` URL, normalized on merge) and often a PMID, so it both
    widens coverage and cross-confirms papers the other providers already found."""
    r = requests.get(
        "https://api.openalex.org/works",
        params={"search": term, "per_page": max_results, "mailto": _POLITE_MAILTO},
        timeout=HTTP_TIMEOUT,
    )
    r.raise_for_status()
    results = r.json().get("results", []) or []
    recs = []
    for it in results:
        pmid_raw = ((it.get("ids") or {}).get("pmid") or "")
        pmid = pmid_raw.rstrip("/").rsplit("/", 1)[-1] if pmid_raw else ""
        src = ((it.get("primary_location") or {}).get("source") or {})
        recs.append({
            "pmid": pmid,
            "doi": it.get("doi", "") or "",
            "title": it.get("title") or it.get("display_name") or "",
            "journal": src.get("display_name", "") or "",
            "year": str(it.get("publication_year") or ""),
            "source_db": "OpenAlex",
            "alt_id": it.get("id", "") or "",
        })
    return recs


def _semanticscholar_records(term, max_results=15):
    """Semantic Scholar — free (key-less, but rate-limited) academic graph. Its
    ``externalIds`` carry DOI + PubMed, adding coverage of CS/engineering venues the
    biomedical indexes miss. Rate-limit 429s surface as a RequestException, which the
    aggregator treats as an unreachable provider (never a hard failure)."""
    r = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query": term, "limit": max_results,
                "fields": "title,year,venue,externalIds"},
        timeout=HTTP_TIMEOUT,
    )
    r.raise_for_status()
    results = r.json().get("data", []) or []
    recs = []
    for it in results:
        ext = it.get("externalIds") or {}
        recs.append({
            "pmid": str(ext.get("PubMed") or ""),
            "doi": ext.get("DOI") or "",
            "title": it.get("title") or "",
            "journal": it.get("venue") or "",
            "year": str(it.get("year") or ""),
            "source_db": "Semantic Scholar",
            "alt_id": f"S2:{it.get('paperId','')}",
        })
    return recs


def _format_literature(records, verify=False):
    """Render merged literature records → the bundle's text lines. Shared by the
    single-provider ``search_europepmc`` and the multi-provider ``search_literature``
    so the Crossref-verify semantics live in exactly one place.

    When ``verify`` is set, each DOI is checked against Crossref: a DOI Crossref
    definitively reports as non-existent (404) is dropped from that citation (the
    paper is kept — its PMID still resolves), a confirmed DOI is marked ``✓Crossref``,
    and a DOI we can't check (Crossref unreachable) is kept unmarked — so a Crossref
    outage degrades to "unverified", never to "no citations". Each record carries a
    ``sources`` list; a paper found by more than one provider is tagged with all of
    them (independent corroboration). Returns ``(text, doi_count, verified_count)``.
    """
    lines, doi_count, verified_count = [], 0, 0
    for rec in records:
        pmid = rec.get("pmid", "") or ""
        doi = rec.get("doi", "") or ""
        doi_part = ""
        if doi:
            checked = crossref_verify(doi) if verify else None
            if verify and checked is False:
                doi_part = ""  # Crossref says this DOI does not resolve — drop it
            else:
                doi_count += 1
                mark = " ✓Crossref" if checked is True else ""
                if checked is True:
                    verified_count += 1
                doi_part = f" | DOI {doi}{mark}"
        ident = f"PMID {pmid}" if pmid else (rec.get("alt_id", "") or "unknown")
        srcs = "+".join(rec.get("sources", []) or [])
        src_tag = f" [{srcs}]" if srcs else ""
        lines.append(
            f"- {ident}{doi_part} | {_clean(rec.get('title', ''), 250)} "
            f"| {rec.get('journal', '')} {rec.get('year', '')}{src_tag}"
        )
    return "\n".join(lines), doi_count, verified_count


def search_europepmc(term, max_results=15, verify=False):
    """Single-provider Europe PMC search (kept for back-compat and targeted tests).
    Most callers should use ``search_literature`` instead, which merges Europe PMC
    with OpenAlex + Semantic Scholar. Per Lesson 2 in COMPARISON.md the literature
    target is "K on-topic resolvable IDs", not an exact set."""
    if not term:
        return "", "⚠️ Europe PMC: empty query"
    try:
        records = _europepmc_records(term, max_results=max_results)
    except requests.Timeout:
        return "", "❌ Europe PMC: timed out"
    except requests.RequestException:
        return "", "❌ Europe PMC: request failed"
    if not records:
        return "", "⚠️ Europe PMC: no matching articles"
    for rec in records:
        rec["sources"] = [rec.get("source_db", "Europe PMC")]
    text, doi_count, verified_count = _format_literature(records, verify)
    if verify:
        status = (f"✅ Europe PMC: {len(records)} articles "
                  f"({doi_count} with DOI, {verified_count} Crossref-verified)")
    else:
        status = f"✅ Europe PMC: {len(records)} articles ({doi_count} with DOI)"
    return text, status


def search_literature(term, max_results=15, verify=False, bool_term=None):
    """The literature entry point: query Europe PMC + OpenAlex + Semantic Scholar,
    MERGE their results de-duplicated by normalized DOI (else PMID), and format the
    union. This is the honest "search more databases" — three free indexes with
    different coverage (biomedical, general scholarly, CS/engineering) cross-confirm
    each other, and a paper found by several is tagged with all of them.

    ``bool_term`` (optional) is a boolean-syntax query (a MeSH synonym OR-group from
    ``build_queries``); it is sent to Europe PMC, which parses AND/OR/quoted phrases,
    while OpenAlex and Semantic Scholar — relevance rankers that don't parse booleans
    — get the plain ``term`` bag. When ``bool_term`` is None every provider gets
    ``term`` (today's behavior), so callers that don't normalize are unaffected.

    Providers are interleaved round-robin so each is represented before the
    ``max_results`` cap (otherwise a provider that always returns a full page would
    crowd the others out). Each provider is queried independently; one that raises
    (network error, or a Semantic Scholar 429) is recorded as unreachable and the
    merge proceeds with whoever answered — the section only fails if ALL do. When
    ``verify`` is set the MERGED set is Crossref-checked (see ``_format_literature``).
    """
    if not term:
        return "", "⚠️ Literature: empty query"
    boolq = bool_term or term
    providers = [
        ("Europe PMC", _europepmc_records, boolq),
        ("OpenAlex", _openalex_records, term),
        ("Semantic Scholar", _semanticscholar_records, term),
    ]
    answered, failed = [], []
    for name, fn, provider_term in providers:
        try:
            answered.append((name, fn(provider_term, max_results=max_results)))
        except requests.RequestException:
            failed.append(name)
    if not answered:
        return "", "❌ Literature: all providers unreachable (" + ", ".join(failed) + ")"

    # Round-robin interleave + de-dup by normalized DOI, then PMID.
    merged, by_doi, by_pmid = [], {}, {}
    lists = [recs for _, recs in answered]
    depth = max((len(l) for l in lists), default=0)
    for i in range(depth):
        for recs in lists:
            if i >= len(recs):
                continue
            rec = recs[i]
            ndoi = _normalize_doi(rec.get("doi"))
            pmid = (rec.get("pmid") or "").strip()
            existing = (by_doi.get(ndoi) if ndoi else None) or \
                       (by_pmid.get(pmid) if pmid else None)
            if existing is not None:
                # Enrich the kept record with any identifier this provider adds,
                # and note the corroborating source.
                if ndoi and not existing["doi"]:
                    existing["doi"] = ndoi
                    by_doi[ndoi] = existing
                if pmid and not existing["pmid"]:
                    existing["pmid"] = pmid
                    by_pmid[pmid] = existing
                if rec["source_db"] not in existing["sources"]:
                    existing["sources"].append(rec["source_db"])
                continue
            newrec = {
                "pmid": pmid, "doi": ndoi,
                "title": rec.get("title", ""), "journal": rec.get("journal", ""),
                "year": rec.get("year", ""), "alt_id": rec.get("alt_id", ""),
                "sources": [rec["source_db"]],
            }
            merged.append(newrec)
            if ndoi:
                by_doi[ndoi] = newrec
            if pmid:
                by_pmid[pmid] = newrec
            if len(merged) >= max_results:
                break
        if len(merged) >= max_results:
            break

    if not merged:
        return "", "⚠️ Literature: no matching articles"

    text, doi_count, verified_count = _format_literature(merged, verify)
    prov_names = ", ".join(n for n, _ in answered)
    status = (f"✅ Literature: {len(merged)} articles from {prov_names} "
              f"({doi_count} with DOI"
              + (f", {verified_count} Crossref-verified" if verify else "") + ")")
    if failed:
        status += f" [unreachable: {', '.join(failed)}]"
    return text, status


class _TextExtractor(HTMLParser):
    """Minimal HTML → text extractor (stdlib only; skips script/style)."""

    def __init__(self):
        super().__init__()
        self._skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            t = data.strip()
            if t:
                self.parts.append(t)


def fetch_url_text(url, max_chars=4000):
    url = (url or "").strip()
    if not url:
        return "", None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        r = requests.get(url, timeout=HTTP_TIMEOUT,
                         headers={"User-Agent": "Mozilla/5.0 (ClinicalAIEvalDesigner)"})
        r.raise_for_status()
        parser = _TextExtractor()
        parser.feed(r.text)
        text = _clean(" ".join(parser.parts), max_chars)
        if not text:
            return "", "⚠️ Reference URL: no readable text extracted"
        return text, f"✅ Reference URL: {len(text)} chars extracted"
    except requests.Timeout:
        return "", "❌ Reference URL: timed out"
    except requests.RequestException:
        return "", "❌ Reference URL: fetch failed"


# Literature/regulatory sources with NO free public API — this pipeline genuinely
# cannot reach them, so the bundle says so out loud instead of implying the search
# was exhaustive. A comprehensive systematic review needs licensed / manual access
# to these; naming them is what makes the "evidence floor, not ceiling" claim honest.
_UNREACHABLE_DBS = [
    "Embase", "PsycINFO", "Cochrane Library (CENTRAL)", "Scopus",
    "Web of Science", "CINAHL",
]


def coverage_gaps_note(intervention_type="device"):
    """A plain-language disclosure of what this pipeline did NOT search, so the
    generated spec (and any regulator reading the bundle) knows the boundaries of
    its evidence base rather than mistaking a keyword sweep for a full review.

    ``intervention_type`` keeps the disclosure truthful per-run: the FDA drug/biologic
    pathways (Drugs@FDA / SPL labeling / FAERS) are only searched when the intervention
    is a drug/biologic, so they are credited as "searched" for a drug/both run and
    listed as a gap for a device-only run."""
    it = (intervention_type or "device").lower()
    drug_searched = it in ("drug", "drug/biologic", "biologic", "both")
    searched = ("ClinicalTrials.gov, openFDA (device classification, 510(k), PMA, MAUDE "
                "adverse events, recalls")
    if drug_searched:
        searched += ", plus the drug/biologic pathways Drugs@FDA, SPL labeling, and FAERS"
    searched += ("), the merged literature indexes Europe PMC / OpenAlex / Semantic Scholar "
                 "(PubMed fallback), and Crossref (DOI verification)")
    not_queried = "non-US regulators (EMA, MHRA, PMDA)"
    if not drug_searched:
        not_queried = ("FDA drug/biologic pathways (Drugs@FDA, SPL labeling, FAERS) and "
                       + not_queried)
    return (
        "This spec was grounded ONLY in sources that expose a free, public API: "
        + searched + ". It deliberately does NOT include:\n"
        "- Licensed databases with no public API (institutional / manual retrieval "
        "required): " + ", ".join(_UNREACHABLE_DBS) + ".\n"
        "- " + not_queried + " — not queried by this pipeline.\n"
        "Absence of a record above is NOT evidence of absence. Treat the retrieved "
        "evidence as a floor for expert review, not a complete landscape."
    )


def build_grounded_context(model_desc, use_case, population, optional_url="", setting="",
                           intervention_type="device"):
    """Query every registry (+ optional URL) and assemble the Phase-1 source
    records — the half of the Phase-1 output bundle the Phase-2 critics verify
    the draft against.

    ``intervention_type`` routes the FDA search deterministically:
      - "device" (default) → openFDA device classification/510(k) + PMA/MAUDE/recall.
      - "drug"             → openFDA Drugs@FDA/SPL labeling/FAERS.
      - "both"             → all of the above (an AI-SaMD that acts on a drug).
    An explicit selector (rather than inferring the pathway from free text) keeps the
    input→output mapping auditable — the regulatory pathway is declared, not guessed.

    The condition is MeSH-normalized (``normalize_mesh``) before the literature/trial
    search so the same clinical concept is retrieved regardless of the wording typed;
    the resolved heading is recorded in the Retrieval Metadata for auditability, and a
    non-resolving term silently falls back to the raw keywords.

    Returns ``(context_text, statuses, retrieval_timestamp)``. The timestamp is the
    UTC instant the evidence was pulled: registries update over time, so the
    regulator-grade guarantee is not "re-running gives the same rows" but "this
    snapshot, taken at this time, is frozen and travels with the spec." A reader
    cites the snapshot, not a live re-query. The metadata + coverage-gaps sections
    are ALWAYS emitted (even when little is retrieved) so every bundle is
    self-describing and honest about what was and was not searched.
    """
    it = (intervention_type or "device").lower()
    want_device = it in ("device", "both")
    want_drug = it in ("drug", "drug/biologic", "biologic", "both")

    retrieval_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    q = build_queries(model_desc, use_case, population, setting)
    # MeSH-normalize the CONDITION (the one network step that changes the query
    # itself): resolve the typed wording to the canonical NLM heading + synonyms,
    # then rebuild the literature/trial query around it. None (ambiguous / non-MeSH
    # / lookup down) leaves the raw-keyword query untouched, so retrieval is never
    # worse than before normalization.
    mesh = normalize_mesh(q.get("mesh_candidates"))
    if mesh:
        q = build_queries(model_desc, use_case, population, setting, mesh=mesh)
    ct_text, ct_status = search_clinicaltrials(q["ct"])

    # openFDA DEVICE pathway (classification/510(k) + PMA/MAUDE/recall post-market
    # safety) — only when the intervention is a device (the default). PMA is the
    # highest-risk pathway; MAUDE/recall are the safety signal 510(k) alone misses.
    fda_text = fda_status = safety_text = safety_status = None
    if want_device:
        fda_text, fda_status = search_openfda(q.get("fda_terms") or q["fda"])
        safety_text, safety_status = search_openfda_safety(q.get("fda_terms") or q["fda"])

    # openFDA DRUG/BIOLOGIC pathway (Drugs@FDA approvals / SPL labeling / FAERS adverse
    # events) — only when the intervention is (or acts on) a drug/biologic.
    drug_text = drug_status = None
    if want_drug:
        drug_text, drug_status = search_openfda_drug(q.get("drug_terms") or q["fda"])

    # Literature: Europe PMC + OpenAlex + Semantic Scholar, merged and de-duplicated
    # (DOIs Crossref-verified). PubMed E-utilities are a last-ditch fallback if all
    # three merge-providers return nothing usable, so the literature section is never
    # empty just because the modern indexes hiccupped together.
    lit_text, lit_status = search_literature(
        q.get("lit_bow") or q["pubmed"], verify=True, bool_term=q["pubmed"])
    if not lit_text:
        pm_text, pm_status = search_pubmed(q["pubmed"])
        if pm_text:
            lit_text, lit_status = pm_text, pm_status
    url_text, url_status = fetch_url_text(optional_url)

    meta_lines = [
        "### Retrieval Metadata",
        f"- Retrieved (UTC): {retrieval_timestamp}",
        f"- Intervention type: {it}",
        f"- Literature/trials query: {q['pubmed']!r}",
    ]
    if mesh:
        meta_lines.append(
            f"- MeSH normalization: {mesh['input']!r} → \"{mesh['preferred']}\" "
            f"({mesh['descriptor_id']}) + {len(mesh.get('synonyms') or [])} synonyms")
    else:
        meta_lines.append("- MeSH normalization: none (condition not an exact MeSH "
                          "heading, or lookup unavailable) — raw keywords used")
    if want_device:
        meta_lines.append(f"- openFDA device terms: {q.get('fda_terms')}")
    if want_drug:
        meta_lines.append(f"- openFDA drug terms: {q.get('drug_terms')}")
    sections = ["\n".join(meta_lines)]

    if ct_text:
        sections.append("### ClinicalTrials.gov (study designs, endpoints, enrollment)\n" + ct_text)
    if want_device and fda_text:
        sections.append("### openFDA (device classification / 510(k) precedents)\n" + fda_text)
    if want_device and safety_text:
        sections.append("### openFDA post-market & Class III (PMA / MAUDE adverse events / recalls)\n"
                        + safety_text)
    if want_drug and drug_text:
        sections.append("### openFDA drug/biologic (Drugs@FDA approvals / SPL labeling / FAERS "
                        "adverse events)\n" + drug_text)
    if lit_text:
        sections.append("### Literature (Europe PMC + OpenAlex + Semantic Scholar / PubMed "
                        "— PMID + DOI, merged & de-duplicated)\n" + lit_text)
    if url_text:
        sections.append("### Reference document (user-provided URL)\n" + url_text)
    sections.append("### Coverage & Retrieval Gaps\n" + coverage_gaps_note(it))

    # Ordered so the DEFAULT device run stays [ct, classification, safety, literature]
    # (existing index-based tests depend on that shape); drug/both extend it.
    statuses = [ct_status]
    if want_device:
        statuses += [fda_status, safety_status]
    if want_drug:
        statuses.append(drug_status)
    statuses.append(lit_status)
    if url_status:
        statuses.append(url_status)

    return "\n\n".join(sections)[:CONTEXT_CAP], statuses, retrieval_timestamp
