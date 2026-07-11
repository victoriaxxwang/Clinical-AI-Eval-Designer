# FDA fix — F4b re-scoring with the SECOND axis (device-name), free, no API cost

*Date 2026-07-11. Ran the upgraded two-axis `fda_bridge.disease_to_fda` on all 10
demo diseases, both ways (oracle disease = ceiling; wide-net's recovered disease =
real end-to-end). Raw: `f4b_scoring.json`. Tripwire `2e6d49...` clean; engine.py
untouched. Two precision fixes applied during the run: (1) a >=2015 date floor for
name-signal-only devices — drops pre-AI namesakes (a 1986 "Computer Assisted
Diabetic Instruction" device); (2) removed bare "assist" from the diagnostic-signal
list — it was catching organ-**assist** hardware ("KIDNEY ASSIST-transport");
"computer-assisted" remains its own signal, so no real CAD device is lost.*

## What the second axis is

F3 (axis 1) searched FDA **classification codes** whose NAME/definition contains the
disease. That misses the reality (F5 finding) that most clinical-AI devices sit under
**generically-named** codes (OEB "Computer-Assisted Detection", QAS "Radiological
Computer-Assisted Triage"). F3b (axis 2) searches the **510(k) device NAMES directly**
for the disease + anatomy tokens, then keeps a device only if it is (a) under a known
AI/CAD/triage code OR (b) carries a diagnostic signal in its name AND was cleared
>=2015. This reaches the AI devices axis 1 could never see.

## Before/after at the CEILING (oracle disease)

| Disease | F3 code-axis (before) | F3b name-axis adds | Net verdict |
|---|---|---|---|
| **Diabetic retinopathy** | PIB → EyeArt/IDx-DR/AEYE-DS ✅ GOLD | (nothing new) | ✅ GOLD held |
| **Ischemic stroke** | POL thrombectomy (off-**type**) | **Brainomix 360, Methinks CTA/NCCT, Rapid NCCT Stroke** (5 real, QAS) + 1 MRI-scanner noise | ✅ **BIG WIN**: off-type → real triage AI |
| **NSCLC** | NSD **bladder-FISH (WRONG)** | **syngo.CT Lung CAD (OEB), Lung Vision System (LLZ)** | ✅ **WIN**: wrong → real lung CAD |
| Melanoma | OYD (right code, De Novo, 0 legacy 510k) | (nothing) | ⚪ code right, no 510(k) predicate |
| Tuberculosis | PEU TB lab test | (nothing) | 🟡 lab, off-modality |
| T2DM | OYC insulin pump | Accu-Chek glucose monitor (right disease, off-type) | 🟡 off-type |
| COPD | PRI procalcitonin | 1 hydrocephalus device (noise via generic word "obstructive") | 🟡 + minor noise |
| AKI | PIG AKI test | (organ-transport noise **removed** by the assist fix) | 🟡 lab |
| Crohn's | (none) | (none) | ⚪ honestly empty |
| MDD | QGH ECT (down-ranked) | (nothing) | 🟡 treatment |

## Before/after END-TO-END (wide-net's recovered disease) — the number that matters

The second axis also **rescues cases the code axis loses to parent-broadening**,
because the anatomy token survives broadening:

- **NSCLC** recovers to the vague "Lung Neoplasms" → code axis returns **nothing**, but
  the **"Lung" token still finds syngo.CT Lung CAD + Lung Vision System**. Real lung CAD,
  end-to-end.
- **Ischemic stroke** recovers exactly → **5 real stroke-triage AI** end-to-end.
- **Diabetic retinopathy** → PIB gold via code axis.
- COPD recovers to "Lung Diseases" → lung CAD (right-organ, off-type for a survival model).
- T2DM → glucose monitor (right disease, off-type).

**End-to-end clean/strong showcase cases went from 1 (DR only) → 3 (DR, stroke, NSCLC).**
The single most important change: NSCLC and stroke moved from **confidently-wrong /
off-type** to **real, citable AI predicates**.

## Residual noise (bounded, cite-or-flag territory)

Three low-grade items remain, all the kind B3 proved cite-or-flag quarantines:
- Stroke list includes 1 MRI scanner (matched "ischemic" + "software" in its name).
- COPD matches a hydrocephalus device on the generic word "obstructive".
- T2DM matches a glucose monitor (right disease, wrong device type).

None is confidently-wrong in a way that survives the downstream panel; worst case is a
flagged or hedged FDA row. No golden was harmed by the precision fixes (DR/melanoma
code-axis rankings unchanged; Lung CAD kept via "cad"; stroke kept via QAS code).

## Revised F5 recommendation → GO (scoped)

The second axis turns FDA from a **1-case showcase (DR)** into a **3-case imaging-AI
showcase (DR + stroke + NSCLC)** and removes the two worst outcomes (NSCLC wrong-answer,
stroke false-negative). It degrades safely everywhere else. This is now a clear,
credible, verifiable upgrade — recommend **GO**: wire behind the existing wide-net
toggle (snapshot engine_widenet first, frozen engine.py untouched), then a small paid
downstream check (~2 cases). Shipping as-is remains legitimate given the 2-day deadline,
but the payoff/risk ratio now clearly favors GO.
