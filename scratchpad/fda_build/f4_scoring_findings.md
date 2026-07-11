# FDA fix — F4 free retrieval scoring (10 demo diseases, no API cost)

*Date 2026-07-11. Ran `experimental/fda_bridge.py` (Option 3 hybrid) on all 10 batch
diseases, TWO ways: given the CORRECT disease (bridge ceiling) and given wide-net's
ACTUAL recovered disease (real end-to-end). Raw: `f4_scoring.json`. Tripwire clean.
No engine.py touched; fda_bridge is a standalone module.*

## Scoring method (per the precision/recall rule, not raw counts)

Hard golden (diseases with a crisp, well-known AI-diagnostic FDA code):
`Diabetic Retinopathy → PIB`, `Melanoma → OYD`. **Recall = did the bridge surface the
golden code in its chosen top-N?** Both = **HIT (2/2).** For the other 8 diseases no
authoritative single golden code exists (their FDA device codes are treatment/lab, not
imaging-AI), so those are judged qualitatively by device-type match.

## Results given the CORRECT disease (the bridge's ceiling)

| Disease | Top code | Verdict |
|---|---|---|
| **Diabetic retinopathy** | **PIB** — Diabetic Retinopathy Detection Device → **EyeArt, IDx-DR, AEYE-DS** | ✅ **GOLD** (golden HIT; real AI predicates) |
| **Melanoma** | **OYD** — Optical Diagnostic Device For Melanoma Detection | ✅ right code (golden HIT; De Novo, 0 legacy 510(k)s) |
| Acute kidney injury | PIG — Acute Kidney Injury Test System (4 preds) | 🟡 disease-correct, lab not the RNN |
| COPD | PRI — Procalcitonin Assay (3 preds) | 🟡 disease-adjacent biomarker |
| T2DM | OYC — Insulin infusion pump (4 preds) | 🟡 disease-correct, treatment |
| TB (chest X-ray) | PEU — TB nucleic-acid test (2 preds) | 🟡 disease-correct, wrong modality (lab, not imaging) |
| Ischemic stroke | POL — Thrombectomy device (6 preds) | 🟡 disease-correct, treatment not diagnostic |
| Major depression | QGH — ECT device (rank −3, 6 preds) | 🟡 correctly down-ranked; only option is treatment |
| NSCLC | NSD — Bladder-cancer FISH test | 🔴 miss (falls back to generic "Carcinoma") |
| Crohn's | (none) | ⚪ honestly empty — no Crohn-specific FDA device exists |

**Ceiling tally: 2 GOLD diagnostic hits, 6 disease-correct-but-off-type/modality,
1 honest-empty, 1 wrong.** The ranking is doing its job (ECT down-weighted to −3;
PIB/OYD lifted to +4/+8), but most diseases simply have no imaging-AI FDA code — the
disease-specific codes that exist are treatment or lab devices.

## Results given WIDE-NET'S RECOVERED disease (the REAL end-to-end result)

Wide-net recovers only 4/10 diseases cleanly, which shrinks coverage further:

| Disease | Recovered to | FDA bridge result |
|---|---|---|
| **Diabetic retinopathy** | Diabetic Retinopathy ✅ | **PIB → EyeArt / IDx-DR / AEYE-DS** ✅ **the one clean showcase win** |
| Ischemic stroke | Ischemic Stroke ✅ | POL thrombectomy (disease-correct, treatment) |
| TB | Tuberculosis, Pulmonary ✅ | PEU TB test (disease-correct, lab) |
| Crohn's | Crohn Disease ✅ | (none) |
| NSCLC / COPD / T2DM | parent-broadened | None / off-target |
| Melanoma / AKI | misfired recovery | off-target (melanoma→Neoplasms→light-chain probe) |
| MDD | no recovery | (none) |

## Honest headline

- **On diabetic retinopathy — very likely THE demo case — this is transformative:**
  today's FDA citations ("surgical lasers + a bacti plate") become **EyeArt, IDx-DR,
  AEYE-DS** — the real FDA-cleared autonomous-AI DR systems (IDx-DR was the first ever
  FDA-authorized autonomous diagnostic AI). A gorgeous, verifiable before/after.
- **It is NOT a broad win.** Elsewhere it finds disease-related-but-wrong-device-type
  records or nothing, because (1) most disease-specific FDA *device* codes are
  treatment/lab, not imaging AI, and (2) wide-net only recovers 4/10 diseases cleanly.
- **It degrades safely.** Off-target predicates are exactly what cite-or-flag
  quarantined in B3 (melanoma) — the panel flags "not an analogous predicate." So
  wiring it in cannot produce a confidently-wrong FDA claim; worst case is a flagged,
  hedged, or empty FDA section — same safety property the rest of the system has.

## Decision this drives (F5 go/no-go)

Two legitimate choices, deadline 2 days out:
- **GO (scoped):** wire the bridge into wide-net (behind the existing toggle; frozen
  baseline untouched; snapshot engine_widenet first), so DR shows the gorgeous
  predicates and everything else degrades safely. Cost: a small paid downstream check
  (~2 cases, F6). Payoff: the single most impressive, most verifiable upgrade to the
  demo. Risk: low, contained behind the toggle with the cite-or-flag safety net.
- **SHIP AS-IS:** the toggle demo already works and is banked; FDA stays a documented
  known-gap. Zero added risk; lose the DR FDA showcase.
