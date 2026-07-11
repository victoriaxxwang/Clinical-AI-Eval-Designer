"""Option-1 F5 BATCH — B2 retrieval sweep (NO API key, FREE).

Generalizes f5_harness.py's single-case F5a retrieval diff to loop over the 10
Claude-Science cases in f5_batch_cases.json. For each case it builds BOTH grounded
contexts live from the public registries (frozen engine.py vs the self-contained
wide-net twin experimental/engine_widenet.py), saves them, and records the
objective metrics that answer two questions BEFORE we spend the API key:

  1) DISEASE RECOVERY — did each arm surface the oracle disease (MeSH-normalized)?
     gate_pass = frozen MISSES the disease AND wide-net SURFACES it (the demo win).
  2) FDA GAP — are the two arms' openFDA sections byte-identical? (they should be:
     wide-net only widens the literature/trial path, never the FDA product-code
     path). We also record literature-section identity to show where the arms DO
     diverge (literature) vs do NOT (FDA).

The frozen engine is never touched; tripwire md5 is asserted at start and end.

Outputs (scratchpad/f5_batch/):
  <id>_frozen_context.txt / <id>_widenet_context.txt   (per case, both arms)
  f5_batch_retrieval_summary.json                       (machine-readable metrics)
  f5_batch_retrieval_table.md                           (human-readable table)
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "f5_batch")
os.makedirs(OUT, exist_ok=True)

# --- Tripwire: the frozen engine must be byte-for-byte unchanged. ------------
FROZEN_MD5 = "2e6d49cdaa3106b6c29ee66b5df37e58"
with open(os.path.join(REPO, "engine.py"), "rb") as fh:
    actual = hashlib.md5(fh.read()).hexdigest()
assert actual == FROZEN_MD5, f"TRIPWIRE FAIL: engine.py md5 {actual} != {FROZEN_MD5}"
print(f"[tripwire] engine.py md5 OK ({actual})")

sys.path.insert(0, REPO)
import engine  # frozen  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "experimental"))
import engine_widenet  # wide-net  # noqa: E402

ARMS = [("frozen", engine), ("widenet", engine_widenet)]

with open(os.path.join(HERE, "f5_batch_cases.json")) as fh:
    BATCH = json.load(fh)
CASES = BATCH["cases"]


def _meta_line(context, label):
    for line in context.splitlines():
        s = line.strip()
        if s.startswith(f"- {label}:"):
            return s[len(f"- {label}:"):].strip()
    return None


def parse_sections(context):
    """Return an ordered {section_title: body} dict split on '### ' headers."""
    sections, cur, buf = {}, None, []
    for line in context.splitlines():
        if line.startswith("### "):
            if cur is not None:
                sections[cur] = "\n".join(buf).strip()
            cur, buf = line[4:].strip(), []
        else:
            buf.append(line)
    if cur is not None:
        sections[cur] = "\n".join(buf).strip()
    return sections


def _blob(context, needle):
    secs = parse_sections(context)
    return "\n\n".join(v for k, v in secs.items() if needle.lower() in k.lower())


def build_context(eng, case):
    ctx, statuses, ts = eng.build_grounded_context(
        case["model_desc"], case["use_case"], case["population"],
        case.get("optional_url", ""), case.get("setting", ""),
        case.get("intervention_type", "device"),
    )
    return ctx, statuses, ts


def run():
    rows = []
    for case in CASES:
        oracle = case["mesh_heading_oracle"]
        print(f"\n================ {case['id']}  |  oracle: {oracle} ================")
        arm_data = {}
        contexts = {}
        for name, eng in ARMS:
            ctx, statuses, _ts = build_context(eng, case)
            contexts[name] = ctx
            with open(os.path.join(OUT, f"{case['id']}_{name}_context.txt"), "w") as fh:
                fh.write(ctx)
            mesh = _meta_line(ctx, "MeSH normalization")
            query = _meta_line(ctx, "Literature/trials query")
            surfaced = bool(mesh) and oracle.lower() in (mesh or "").lower()
            n_ok = sum(1 for s in statuses if s.startswith("✅"))
            arm_data[name] = {
                "mesh_normalization": mesh,
                "query": query,
                "surfaced_oracle_disease": surfaced,
                "context_chars": len(ctx),
                "registry_hits_ok": n_ok,
            }
            print(f"  --- {name.upper()} ---")
            print(f"    MeSH  : {mesh}")
            print(f"    query : {query}")
            print(f"    surfaced '{oracle}'? -> {surfaced}")

        f_surf = arm_data["frozen"]["surfaced_oracle_disease"]
        w_surf = arm_data["widenet"]["surfaced_oracle_disease"]
        gate = (not f_surf) and w_surf
        fda_identical = hashlib.md5(_blob(contexts["frozen"], "openFDA").encode()).hexdigest() \
            == hashlib.md5(_blob(contexts["widenet"], "openFDA").encode()).hexdigest()
        lit_identical = hashlib.md5(_blob(contexts["frozen"], "Literature").encode()).hexdigest() \
            == hashlib.md5(_blob(contexts["widenet"], "Literature").encode()).hexdigest()
        print(f"  => gate_pass={gate}  fda_identical={fda_identical}  lit_identical={lit_identical}")
        rows.append({
            "id": case["id"],
            "oracle": oracle,
            "disease_in_text": case.get("_disease_in_text", ""),
            "frozen_surfaced": f_surf,
            "widenet_surfaced": w_surf,
            "gate_pass": gate,
            "fda_identical": fda_identical,
            "lit_identical": lit_identical,
            "arms": arm_data,
        })

    # ---- aggregate ----
    n = len(rows)
    agg = {
        "n_cases": n,
        "frozen_surfaced": sum(r["frozen_surfaced"] for r in rows),
        "widenet_surfaced": sum(r["widenet_surfaced"] for r in rows),
        "gate_pass": sum(r["gate_pass"] for r in rows),
        "fda_identical": sum(r["fda_identical"] for r in rows),
        "lit_diverged": sum(not r["lit_identical"] for r in rows),
    }
    summary = {"aggregate": agg, "cases": rows}
    with open(os.path.join(OUT, "f5_batch_retrieval_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)

    # ---- markdown table ----
    lines = [
        "# F5 batch — B2 retrieval sweep (frozen vs wide-net, no API key)",
        "",
        f"10 Claude-Science cases. **frozen surfaced disease: {agg['frozen_surfaced']}/{n}** · "
        f"**wide-net surfaced disease: {agg['widenet_surfaced']}/{n}** · "
        f"**gate pass (frozen misses ∧ wide-net surfaces): {agg['gate_pass']}/{n}** · "
        f"**FDA sections identical between arms: {agg['fda_identical']}/{n}** · "
        f"**literature diverged: {agg['lit_diverged']}/{n}**.",
        "",
        "| Case | Oracle disease | Frozen surfaced | Wide-net surfaced | Gate pass | FDA identical | Lit diverged |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['id']} | {r['oracle']} | {'✅' if r['frozen_surfaced'] else '❌'} | "
            f"{'✅' if r['widenet_surfaced'] else '❌'} | {'✅' if r['gate_pass'] else '—'} | "
            f"{'=' if r['fda_identical'] else '≠'} | {'✅' if not r['lit_identical'] else '—'} |")
    lines += [
        "",
        "**Reading:** *Gate pass* = the heart-failure demo condition reproduced "
        "(frozen misses the disease, wide-net recovers it). *FDA identical* = the two "
        "arms returned byte-identical openFDA sections (wide-net never touches the FDA "
        "product-code path — the documented Phase-2 bound). *Lit diverged* = wide-net "
        "changed the literature the downstream spec/panel would reason over.",
    ]
    with open(os.path.join(OUT, "f5_batch_retrieval_table.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")

    print("\n================ AGGREGATE ================")
    print(json.dumps(agg, indent=2))
    print(f"\nwrote {OUT}/f5_batch_retrieval_summary.json + _table.md")


if __name__ == "__main__":
    run()
    with open(os.path.join(REPO, "engine.py"), "rb") as fh:
        end = hashlib.md5(fh.read()).hexdigest()
    assert end == FROZEN_MD5, f"TRIPWIRE FAIL AT END: {end}"
    print(f"\n[tripwire] engine.py md5 still OK ({end})")
