"""Option-1 F2 — frozen engine.py vs experimental/engine_widenet.py, retrieval-only.

For each of 3 topics x 2 phrasings (6 cases), and each engine:
  1. build_queries(model_desc, use_case, population, setting)  -> mesh_candidates + mesh_new_bares
  2. LIVE normalize_mesh(candidates, new_bares=...) against NCBI E-utilities MeSH
Records, per case:
  (a) ENTERED  = did a surface phrase for the disease appear in mesh_candidates at all
  (b) RESOLVED = did normalize_mesh return a heading, and does it == mesh_heading_oracle
The ONLY difference between the two engines is the new-bares logic in _mesh_candidates;
normalize_mesh (the live resolver) is identical, so any delta is attributable to surfacing.

NO API key used. All calls are public NCBI/MeSH HTTP. Results saved to f2_results.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# frozen engine (repo root) first, then the experimental copy on a separate name.
sys.path.insert(0, REPO)
import engine  # frozen
sys.path.insert(0, os.path.join(REPO, "experimental"))
import engine_widenet  # wide-net

ENGINES = [("frozen", engine), ("widenet", engine_widenet)]

# Per-topic surface phrases: the lay/bigram/unigram forms that COUNT as "the disease
# entered the lookup" if present in mesh_candidates. The oracle is the exact heading
# normalize_mesh must return for a RESOLVED-to-oracle hit.
SURFACE = {
    "heart_failure": ["heart failure", "failure"],
    "chronic_kidney_disease": ["chronic kidney", "kidney disease", "renal", "kidney"],
    "pulmonary_embolism": ["pulmonary embolism", "embolism"],
}

with open(os.path.join(HERE, "option1_test_topics.json")) as fh:
    TOPICS = json.load(fh)["topics"]

# md5 tripwire guard inside the run (paranoia: fail loud if frozen engine changed).
import hashlib
with open(os.path.join(REPO, "engine.py"), "rb") as fh:
    md5 = hashlib.md5(fh.read()).hexdigest()
assert md5 == "2e6d49cdaa3106b6c29ee66b5df37e58", f"FROZEN ENGINE CHANGED: {md5}"

results = []
for topic in TOPICS:
    tid = topic["id"]
    oracle = topic["mesh_heading_oracle"]
    surface = SURFACE[tid]
    for phrasing in ("control", "mechanism_first"):
        p = topic["phrasings"][phrasing]
        for ename, eng in ENGINES:
            q = eng.build_queries(p["model_desc"], p["use_case"],
                                  p["population"], p["setting"])
            cands = q["mesh_candidates"]
            new_bares = set(q.get("mesh_new_bares") or [])
            present = [s for s in surface if s in cands]
            entered = bool(present)
            resolved = eng.normalize_mesh(cands, with_children=False, new_bares=new_bares)
            pref = resolved["preferred"] if resolved else None
            matched_input = resolved["input"] if resolved else None
            oracle_match = bool(resolved) and pref == oracle
            rec = {
                "topic": tid, "phrasing": phrasing, "engine": ename,
                "oracle": oracle,
                "entered": entered, "present_phrases": present,
                "resolved_preferred": pref, "resolved_from_candidate": matched_input,
                "oracle_match": oracle_match,
                "n_candidates": len(cands), "mesh_candidates": cands,
                "mesh_new_bares": sorted(new_bares),
            }
            results.append(rec)
            print(f"[{tid:24s} {phrasing:15s} {ename:8s}] "
                  f"entered={entered!s:5s} resolved={pref!r} "
                  f"oracle_match={oracle_match}")

out = os.path.join(HERE, "f2_results.json")
with open(out, "w") as fh:
    json.dump(results, fh, indent=2)

# ---- compact summary: per topic/phrasing, frozen vs widenet ------------------
def cell(r):
    if not r:
        return "?"
    if r["oracle_match"]:
        return "ORACLE"
    if r["resolved_preferred"]:
        return f"->{r['resolved_preferred']}"
    if r["entered"]:
        return "entered/unresolved"
    return "absent"

idx = {(r["topic"], r["phrasing"], r["engine"]): r for r in results}
print("\n================ F2 SUMMARY (frozen -> widenet) ================")
tot = {"frozen": 0, "widenet": 0}
for topic in TOPICS:
    tid = topic["id"]
    print(f"\n{tid}  (oracle: {topic['mesh_heading_oracle']})")
    for phrasing in ("control", "mechanism_first"):
        f = idx.get((tid, phrasing, "frozen"))
        w = idx.get((tid, phrasing, "widenet"))
        tot["frozen"] += 1 if (f and f["oracle_match"]) else 0
        tot["widenet"] += 1 if (w and w["oracle_match"]) else 0
        print(f"  {phrasing:15s}  frozen: {cell(f):22s}  |  widenet: {cell(w)}")
print(f"\nORACLE-MATCH TOTALS (of 6):  frozen={tot['frozen']}  widenet={tot['widenet']}")
print(f"\nfrozen engine md5 (post-run): {md5}")
print(f"results -> {out}")
