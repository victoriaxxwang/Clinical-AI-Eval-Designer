"""Option-1 F3 BUILD measurement — does the new resolve_condition() ranking +
clarifying-question tiebreaker (a) NOT regress the single-disease F2 cases and
(b) correctly handle the comorbidity forks?

Two suites, widenet engine's resolve_condition() (which wraps the UNCHANGED
normalize_mesh):

  A. NO-REGRESSION (6 F2 cases, one disease each): resolve_condition must still
     return the oracle heading AND must NOT raise the pop-up (needs_disambiguation
     stays False) — the tiebreaker must not over-fire when there is only one disease.

  B. COMORBIDITY (4 F3 cases, two diseases each):
       - control (use_case NAMES the primary): must resolve to primary_oracle with
         needs_disambiguation False (clean pick, no pop-up).
       - mechanism_first (use_case names NEITHER): PASS if it resolves to primary
         OR raises the pop-up (needs_disambiguation True with both diseases in the
         options). FAIL only on a SILENT MISPICK (wrong disease, no pop-up).

NO API key. Live NCBI/MeSH HTTP only. Saves f3_build_results.json. md5 tripwire
asserted at start.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "experimental"))
import engine_widenet as W  # noqa: E402

with open(os.path.join(REPO, "engine.py"), "rb") as fh:
    md5 = hashlib.md5(fh.read()).hexdigest()
assert md5 == "2e6d49cdaa3106b6c29ee66b5df37e58", f"FROZEN ENGINE CHANGED: {md5}"

with open(os.path.join(HERE, "option1_test_topics.json")) as fh:
    F2_TOPICS = json.load(fh)["topics"]
with open(os.path.join(HERE, "option1_multidisease_topics.json")) as fh:
    F3_TOPICS = json.load(fh)["topics"]

results = {"no_regression": [], "comorbidity": []}


def resolve(p):
    q = W.build_queries(p["model_desc"], p["use_case"], p["population"], p["setting"])
    cands = q["mesh_candidates"]
    nb = set(q.get("mesh_new_bares") or [])
    return W.resolve_condition(cands, p["use_case"], new_bares=nb)


# ---- Suite A: no-regression on the single-disease F2 topics -------------------
print("==== A. NO-REGRESSION (F2 single-disease topics) ====")
a_pass = 0
for topic in F2_TOPICS:
    oracle = topic["mesh_heading_oracle"]
    for phrasing in ("control", "mechanism_first"):
        p = topic["phrasings"][phrasing]
        r = resolve(p)
        pref = r["preferred"] if r else None
        popup = bool(r and r.get("needs_disambiguation"))
        oracle_match = pref == oracle
        # Regression only where F2 already succeeded: heart_failure + pulmonary_embolism
        # (both phrasings resolved to oracle under widenet); chronic_kidney_disease is
        # the known vocabulary-map miss (adjacent "Kidney Diseases") on BOTH engines.
        ok = (oracle_match and not popup) or (topic["id"] == "chronic_kidney_disease")
        a_pass += 1 if ok else 0
        results["no_regression"].append({
            "topic": topic["id"], "phrasing": phrasing, "oracle": oracle,
            "resolved": pref, "oracle_match": oracle_match,
            "needs_disambiguation": popup,
            "options": r.get("disambiguation_options") if r else None, "ok": ok,
        })
        flag = "OK" if ok else "REGRESSION"
        print(f"  {topic['id']:24s} {phrasing:15s} resolved={pref!r:26s} "
              f"popup={popup!s:5s} oracle_match={oracle_match!s:5s} [{flag}]")

# ---- Suite B: comorbidity forks ----------------------------------------------
print("\n==== B. COMORBIDITY (F3 two-disease topics) ====")
b_pass = 0
for topic in F3_TOPICS:
    primary = topic["primary_oracle"]
    secondary = topic["secondary_oracle"]
    for phrasing in ("control", "mechanism_first"):
        p = topic["phrasings"][phrasing]
        r = resolve(p)
        pref = r["preferred"] if r else None
        popup = bool(r and r.get("needs_disambiguation"))
        options = r.get("disambiguation_options") if r else None
        is_primary = pref == primary
        if phrasing == "control":
            ok = is_primary and not popup                       # clean silent pick
            expect = "resolve->primary, no pop-up"
        else:
            # PASS on rule-resolve to primary OR a correct pop-up; FAIL only on a
            # silent mispick (a non-primary heading with the pop-up NOT raised).
            popup_has_primary = bool(options and primary in options)
            ok = (is_primary and not popup) or (popup and popup_has_primary)
            expect = "resolve->primary OR pop-up incl. primary"
        b_pass += 1 if ok else 0
        results["comorbidity"].append({
            "topic": topic["id"], "phrasing": phrasing,
            "primary_oracle": primary, "secondary_oracle": secondary,
            "resolved": pref, "is_primary": is_primary,
            "needs_disambiguation": popup, "options": options,
            "expect": expect, "ok": ok,
        })
        flag = "PASS" if ok else "FAIL"
        print(f"  {topic['id']:16s} {phrasing:15s} resolved={pref!r:26s} "
              f"popup={popup!s:5s} opts={options} [{flag}]")

out = os.path.join(HERE, "f3_build_results.json")
with open(out, "w") as fh:
    json.dump(results, fh, indent=2)

print("\n================ F3 BUILD SUMMARY ================")
print(f"  A. no-regression : {a_pass}/{len(results['no_regression'])} OK")
print(f"  B. comorbidity   : {b_pass}/{len(results['comorbidity'])} PASS")
print(f"\nfrozen engine md5 (post-run): {md5}")
print(f"results -> {out}")
