"""Option-1 F3 probe — does the wide-net engine surface MORE THAN ONE disease on
comorbidity write-ups, and what does the current naive 'first candidate that
resolves wins' logic pick vs the intended PRIMARY target?

For each of 2 comorbidity topics x 2 phrasings (widenet engine only — this is a
wide-net feature; frozen barely surfaces on mechanism_first anyway):
  1. widenet.build_queries -> mesh_candidates (ordered) + mesh_new_bares
  2. NAIVE pick = normalize_mesh(full ordered list) -> the heading the engine
     currently returns (first candidate that resolves).
  3. ENUMERATE = resolve EACH candidate individually to list every distinct
     disease heading the wide-net surfaced (this is the disambiguation fork F3
     must handle). Cached by candidate string so each MeSH term is looked up once.
Records per case: naive pick, full set of surfaced diseases, and whether the
naive pick == primary_oracle. Saved to f3_probe_results.json. NO API key.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experimental"))
import engine_widenet as W  # noqa: E402

with open(os.path.join(REPO, "engine.py"), "rb") as fh:
    md5 = hashlib.md5(fh.read()).hexdigest()
assert md5 == "2e6d49cdaa3106b6c29ee66b5df37e58", f"FROZEN ENGINE CHANGED: {md5}"

with open(os.path.join(HERE, "option1_multidisease_topics.json")) as fh:
    TOPICS = json.load(fh)["topics"]

# resolve a single candidate, cached (term -> preferred heading or None).
_cache = {}
def resolve_one(cand, is_new_bare):
    key = (cand, is_new_bare)
    if key in _cache:
        return _cache[key]
    nb = {cand} if is_new_bare else set()
    r = W.normalize_mesh([cand], with_children=False, new_bares=nb)
    val = r["preferred"] if r else None
    _cache[key] = val
    return val

results = []
for topic in TOPICS:
    primary = topic["primary_oracle"]
    secondary = topic["secondary_oracle"]
    for phrasing in ("control", "mechanism_first"):
        p = topic["phrasings"][phrasing]
        q = W.build_queries(p["model_desc"], p["use_case"], p["population"], p["setting"])
        cands = q["mesh_candidates"]
        new_bares = set(q.get("mesh_new_bares") or [])

        # naive pick = first candidate in order that resolves (what engine returns today)
        naive = W.normalize_mesh(cands, with_children=False, new_bares=new_bares)
        naive_pick = naive["preferred"] if naive else None
        naive_from = naive["input"] if naive else None

        # enumerate every distinct disease the wide-net surfaced, in candidate order
        surfaced = []  # (candidate, heading)
        seen_headings = set()
        for c in cands:
            h = resolve_one(c, c in new_bares)
            if h and h not in seen_headings:
                seen_headings.add(h)
                surfaced.append({"candidate": c, "heading": h})

        rec = {
            "topic": topic["id"], "phrasing": phrasing,
            "primary_oracle": primary, "secondary_oracle": secondary,
            "use_case": p["use_case"],
            "naive_pick": naive_pick, "naive_from_candidate": naive_from,
            "naive_is_primary": naive_pick == primary,
            "n_diseases_surfaced": len(surfaced),
            "diseases_surfaced": surfaced,
            "mesh_candidates": cands, "mesh_new_bares": sorted(new_bares),
        }
        results.append(rec)
        headings = " | ".join(f"{s['heading']}<-{s['candidate']!r}" for s in surfaced)
        print(f"\n[{topic['id']} / {phrasing}]")
        print(f"  use_case: {p['use_case']!r}")
        print(f"  primary target : {primary!r}   (secondary: {secondary!r})")
        print(f"  # diseases surfaced: {len(surfaced)}")
        print(f"  surfaced: {headings}")
        print(f"  NAIVE pick (first-resolve): {naive_pick!r} from {naive_from!r}  "
              f"=> is_primary={naive_pick == primary}")

out = os.path.join(HERE, "f3_probe_results.json")
with open(out, "w") as fh:
    json.dump(results, fh, indent=2)

print("\n================ F3 PROBE SUMMARY ================")
for r in results:
    fork = "FORK (>1 disease)" if r["n_diseases_surfaced"] > 1 else "single"
    verdict = "OK" if r["naive_is_primary"] else "MISPICK"
    print(f"  {r['topic']:16s} {r['phrasing']:15s}  {fork:18s}  "
          f"naive={r['naive_pick']!r:24s} [{verdict}]")
print(f"\nfrozen engine md5 (post-run): {md5}")
print(f"results -> {out}")
