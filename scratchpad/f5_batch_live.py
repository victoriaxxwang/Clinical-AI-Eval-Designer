"""Option-1 B3 (Option A) — live BEFORE/AFTER on 4 representative batch cases.

Generalizes f5_harness.py's run_live to LOOP a set of cases. For each case, for
each engine arm (frozen / wide-net), it:
  1. reads the ALREADY-COMMITTED take-2 grounded context
     (scratchpad/f5_batch/<id>_<arm>_context.txt) so the spec reasons over the
     exact bytes we committed at e9b3ab7 (reproducible; no re-retrieval variance),
  2. generates the full 8-field spec via app.py's byte-faithful generate_spec,
  3. runs critic_panel.run_panel on it.

The 4 Option-A cases span all three take-2 tiers:
  diabetic_retinopathy_fundus     (EXACT recovery)
  crohns_endoscopy_video_cnn      (EXACT recovery)
  nsclc_lung_ct_cnn               (PARENT-broadening: lung cancer -> Lung Neoplasms)
  melanoma_dermoscopy_transformer (MISFIRE: malignancy -> Neoplasms)

Outputs (scratchpad/f5_batch/):
  <id>_<arm>_spec.md      full 8-field spec per arm
  <id>_<arm>_panel.json   critic panel per arm
  f5_batch_live_summary.json   roll-up

Key read from .streamlit/secrets.toml, NEVER printed. Meant to run in the
background under caffeinate. Frozen engine.py is never imported for retrieval
here (contexts are read from disk) but the tripwire is still asserted start+end.
"""

import hashlib
import json
import os
import re
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BATCH = os.path.join(HERE, "f5_batch")

# --- Tripwire: the frozen engine must be byte-for-byte unchanged. ------------
FROZEN_MD5 = "2e6d49cdaa3106b6c29ee66b5df37e58"
with open(os.path.join(REPO, "engine.py"), "rb") as fh:
    actual = hashlib.md5(fh.read()).hexdigest()
assert actual == FROZEN_MD5, f"TRIPWIRE FAIL: engine.py md5 {actual} != {FROZEN_MD5}"
print(f"[tripwire] engine.py md5 OK ({actual})", flush=True)

OPTION_A_IDS = [
    "diabetic_retinopathy_fundus",
    "crohns_endoscopy_video_cnn",
    "nsclc_lung_ct_cnn",
    "melanoma_dermoscopy_transformer",
]
ARMS = ["frozen", "widenet"]

with open(os.path.join(HERE, "f5_batch_cases.json")) as fh:
    _raw = json.load(fh)
    _cases = _raw["cases"] if isinstance(_raw, dict) else _raw
    ALL_CASES = {c["id"]: c for c in _cases}


def _install_streamlit_stub():
    """Let app.py import with all Streamlit UI calls as no-ops, so we can reuse
    its real SYSTEM_PROMPT / generate_spec / build_user_message byte-for-byte."""
    class _Stub:
        def __call__(self, *a, **k):
            return _Stub()

        def __getattr__(self, _):
            return _Stub()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def __bool__(self):
            return False

        def __iter__(self):
            return iter([_Stub(), _Stub(), _Stub(), _Stub()])

        def __getitem__(self, _):
            return _Stub()

        def __setitem__(self, k, v):
            pass

        def __contains__(self, _):
            return False

    st = types.ModuleType("streamlit")
    st.__getattr__ = lambda name: _Stub()  # type: ignore[attr-defined]
    st.session_state = {}
    st.secrets = _Stub()
    st.columns = lambda spec, **k: [_Stub() for _ in range(spec if isinstance(spec, int) else len(spec))]
    st.tabs = lambda labels, **k: [_Stub() for _ in labels]
    sys.modules["streamlit"] = st
    return st


def _read_key():
    """Read ANTHROPIC_API_KEY from .streamlit/secrets.toml. Never printed."""
    path = os.path.join(REPO, ".streamlit", "secrets.toml")
    with open(path) as fh:
        for line in fh:
            m = re.match(r'\s*ANTHROPIC_API_KEY\s*=\s*"([^"]+)"', line)
            if m:
                return m.group(1)
    raise RuntimeError("ANTHROPIC_API_KEY not found in .streamlit/secrets.toml")


def _read_context(case_id, arm):
    path = os.path.join(BATCH, f"{case_id}_{arm}_context.txt")
    with open(path) as fh:
        return fh.read()


def main(effort="medium"):
    import anthropic  # noqa: F401
    _install_streamlit_stub()
    sys.path.insert(0, REPO)
    import app          # reuses real SYSTEM_PROMPT / generate_spec / build_user_message
    import critic_panel

    client = anthropic.Anthropic(api_key=_read_key())
    summary = {"batch": "B3_optionA", "effort": effort, "cases": {}}

    for cid in OPTION_A_IDS:
        case = ALL_CASES[cid]
        print(f"\n################ CASE {cid}  (oracle: {case['mesh_heading_oracle']}) ################", flush=True)
        summary["cases"][cid] = {"oracle": case["mesh_heading_oracle"], "arms": {}}
        for arm in ARMS:
            ctx = _read_context(cid, arm)
            user_message = app.wrap_with_context(
                app.build_user_message(case["model_desc"], case["use_case"],
                                       case["population"], case.get("setting", ""),
                                       case.get("claim", "")),
                ctx,
            )
            print(f"\n--- {cid} / {arm.upper()} : generating spec (effort={effort}) ---", flush=True)
            spec, final = app.generate_spec(client, user_message, effort, use_web_search=False)
            refusal = (final is not None and getattr(final, "stop_reason", None) == "refusal")
            spec_path = os.path.join(BATCH, f"{cid}_{arm}_spec.md")
            with open(spec_path, "w") as fh:
                fh.write(spec or "")
            print(f"    spec chars: {len(spec or '')}  refusal={refusal}", flush=True)

            print(f"--- {cid} / {arm.upper()} : convening critic panel ---", flush=True)
            parsed, pfinal, praw = critic_panel.run_panel(client, ctx, spec or "", effort=effort)
            panel_path = os.path.join(BATCH, f"{cid}_{arm}_panel.json")
            with open(panel_path, "w") as fh:
                json.dump(parsed, fh, indent=2)
            blockers = parsed.get("fix_before_submission") if isinstance(parsed, dict) else []
            audit = parsed.get("grounding_audit") if isinstance(parsed, dict) else None
            summary["cases"][cid]["arms"][arm] = {
                "spec_chars": len(spec or ""),
                "spec_refusal": refusal,
                "spec_file": os.path.basename(spec_path),
                "panel_blockers": len(blockers or []),
                "panel_file": os.path.basename(panel_path),
                "grounding_audit_flags": (len(audit) if isinstance(audit, list) else None),
            }
            print(f"    panel blockers (fix_before_submission): {len(blockers or [])}", flush=True)

    with open(os.path.join(BATCH, "f5_batch_live_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("\n================ B3 Option A DONE ================", flush=True)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
    # re-check tripwire at the end
    with open(os.path.join(REPO, "engine.py"), "rb") as fh:
        end = hashlib.md5(fh.read()).hexdigest()
    assert end == FROZEN_MD5, f"TRIPWIRE FAIL AT END: {end}"
    print(f"\n[tripwire] engine.py md5 still OK ({end})", flush=True)
