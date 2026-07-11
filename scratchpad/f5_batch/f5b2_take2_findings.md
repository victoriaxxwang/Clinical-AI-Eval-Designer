# F5 batch — B2 retrieval sweep, TAKE 2 ("buried-but-present" cases)

*Free retrieval-only sweep (no API key). The take-1 cases (see `f5b2_findings.md`)
had the disease name **entirely absent** from engine-visible text, so wide-net had
nothing to normalize (0/10). This take-2 batch regenerated all 10 cases so the
disease is **named exactly once, in its standard clinical name, buried in a
non-opening clause** of `model_desc` — recreating the heart-failure demo condition
(disease present-but-buried). Each of 10 cases run through BOTH engines (frozen
`engine.py` vs wide-net `experimental/engine_widenet.py`). Tripwire
`2e6d49cdaa3106b6c29ee66b5df37e58` clean at start and end. Raw per-arm contexts in
`scratchpad/f5_batch/<id>_<arm>_context.txt`; metrics in
`f5_batch_retrieval_summary.json` (authoritative) + `_table.md`.*

## Headline numbers (take-2)

| Metric | Take-1 (absent) | **Take-2 (buried-but-present)** |
|---|---|---|
| Frozen surfaced the oracle disease | 0 / 10 | **0 / 10** |
| Wide-net surfaced the oracle disease | 0 / 10 | **4 / 10** |
| Gate pass (frozen misses ∧ wide-net recovers) | 0 / 10 | **4 / 10** |
| FDA sections byte-identical between arms | 10 / 10 | **10 / 10** |
| Literature query diverged between arms | 10 / 10 | **9 / 10** |

**The wide-net win REPRODUCED beyond the n=1 heart-failure case.** Once the disease
is present in the text (even buried in the last clause), wide-net reads it,
MeSH-normalizes it, and rebuilds the literature query around the real condition —
exactly as it did on heart failure. Frozen never surfaces the disease (0/10), so
every wide-net recovery is a clean gate pass.

## The result splits into 3 tiers — root-caused

Wide-net's candidate extractor **prefers 2-word medical phrases**. That single
design choice explains all three tiers: it nails short standard disease names,
and degrades predictably on long compound names.

### ✅ EXACT recovery (4) — short standard 2-word names
| Case | Oracle | Wide-net normalized to |
|---|---|---|
| ischemic_stroke_ct_ensemble | Ischemic Stroke | **Ischemic Stroke** (D000083242) |
| tb_chest_xray_densenet | Tuberculosis, Pulmonary | **Tuberculosis, Pulmonary** (D014397) |
| diabetic_retinopathy_fundus | Diabetic Retinopathy | **Diabetic Retinopathy** (D003930) |
| crohns_endoscopy_video_cnn | Crohn Disease | **Crohn Disease** (D003424) |

### 🟡 PARENT / too-broad (3) — 3–4-word compound names, dropped a modifier
| Case | Oracle | Wide-net normalized to | What happened |
|---|---|---|---|
| nsclc_lung_ct_cnn | Carcinoma, Non-Small-Cell Lung | Lung Neoplasms (D008175) | grabbed the 2-word "lung cancer", lost "non-small cell" |
| copd_exacerbation_survival | Pulmonary Disease, Chronic Obstructive | Lung Diseases (D008171) | grabbed "pulmonary disease", lost "chronic obstructive" |
| t2dm_incident_risk_ehr | Diabetes Mellitus, Type 2 | Diabetes Mellitus (D003920) | grabbed "diabetes mellitus", dropped "type 2" |

These are **not wrong** — they are true MeSH ancestors of the oracle. They just
retrieve a broader literature slice than the ideal. Still a real improvement over
frozen's ML-buzzword query.

### 🔴 MISFIRE / miss (3) — extractor grabbed a competing earlier bigram, or nothing
| Case | Oracle | Wide-net normalized to | What happened |
|---|---|---|---|
| melanoma_dermoscopy_transformer | Melanoma | Neoplasms (D009369) | "melanoma" is 1 word; extractor preferred the earlier 2-word "malignancy" phrase |
| aki_rnn_inpatient | Acute Kidney Injury | Wounds and Injuries (D014947) | grabbed the earlier 2-word "...injury" bigram instead of the 3-word disease |
| mdd_relapse_multimodal | Depressive Disorder, Major | none | no clean 2-word medical bigram matched; fell back to raw keywords |

## Root cause (one sentence)

Wide-net recovers a **present** disease cleanly only for **short standard 2-word
names**; on **3–4-word compound names** it degrades to a MeSH **parent** (drops a
modifier) or grabs a **competing earlier 2-word medical bigram** — because its
candidate extractor prefers 2-word medical phrases.

## Two documented boundaries now (both honest Phase-2 bounds, NOT regressions)

1. **(B1, take-1) Disease ABSENT from visible text → no recovery.** Wide-net reads
   and normalizes; it does not *infer* an unnamed disease from mechanism
   (KDIGO → AKI, PHQ-9 → depression). Different, bigger problem.
2. **(B2, take-2) Disease PRESENT but a long compound name → parent-broadening or
   mis-grab.** Clean recovery is scoped to short standard 2-word names.

## What this DOES establish

- **The wide-net advantage is real and reproducible** (4/10 clean gate passes,
  n=10, beyond the n=1 heart-failure demo) — for the in-scope case shape.
- **The FDA bound is universal** — openFDA sections byte-identical 10/10 in BOTH
  take-1 and take-2. Wide-net never touches the FDA product-code path; the FDA gap
  is a shared blind spot needing a separate indication→product-code bridge, not
  something the frozen-vs-widenet A/B can see.

## Known next improvement (Option C — logged, NOT done)

Editing wide-net's extractor to grab the **full trailing disease phrase** (not just
the best 2-word bigram) could lift 4/10 → ~8/10 (fix the 🟡 parent tier and the AKI
mis-grab). Deferred: it is engine surgery + a re-test cycle, deadline-risky, and
the honest "4/10 + two documented boundaries" story is more credible than an
engineered 8/10.

## Decision this drives (B3)

The 4/10 gate pass is enough to measure **downstream value** on the paid live
spec+panel run (B3). Option A = 4 representative cases spanning all three tiers
(diabetic_retinopathy + crohns = exact; nsclc = parent; melanoma = misfire) × 2
engines ≈ 16 Claude calls. Question B3 answers: does the retrieval difference change
the synthesized spec and sharpen the critic panel, and does cite-or-flag safely
catch the misfire? If valuable → Option B (all 10).
