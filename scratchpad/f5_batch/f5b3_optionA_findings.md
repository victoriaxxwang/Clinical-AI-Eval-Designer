# F5 batch — B3 Option A findings (live spec + critic panel, 4 cases × 2 engines)

*The paid downstream run. For each of 4 representative take-2 cases (spanning all
three retrieval tiers), both grounded contexts (frozen `engine.py` vs wide-net
`experimental/engine_widenet.py`, read from the committed take-2 context files at
e9b3ab7) were run through app.py's byte-faithful `generate_spec` (Fable 5, medium
effort) and `critic_panel.run_panel`. 16/16 Claude calls succeeded, **zero
refusals**, tripwire `2e6d49cdaa3106b6c29ee66b5df37e58` clean start+end. Raw
outputs: `<id>_<arm>_{spec.md,panel.json}`; roll-up `f5_batch_live_summary.json`.*

## The 4 cases (one per tier, melanoma = the safety test)

| Case | Tier (B2) | Wide-net grounded to |
|---|---|---|
| diabetic_retinopathy_fundus | EXACT | Diabetic Retinopathy (D003930) ✅ |
| crohns_endoscopy_video_cnn | EXACT | Crohn Disease (D003424) ✅ |
| nsclc_lung_ct_cnn | PARENT | Lung Neoplasms (D008175) — dropped "non-small cell" |
| melanoma_dermoscopy_transformer | MISFIRE | Neoplasms (D009369) — generic cancer |

## Three-layer verdict (n=4)

### Layer 1 — Retrieval: wide-net grounds to better citations
| Case | Frozen cites (NCT/PMID/K) | Wide-net cites (NCT/PMID/K) |
|---|---|---|
| diabetic_retinopathy | 0 / 8 / 6 | 0 / 6 / 4 (on-target DR) |
| crohns | 2 / 5 / 3 | 2 / 7 / 3 |
| nsclc | 1 / 2 / 5 | **4 / 5 / 3** |
| melanoma | 0 / 6 / 4 | 6 / 3 / 5 (**generic-oncology, off-target**) |

On the on-target cases wide-net pulls more, and more relevant, records. Even the
NSCLC **parent**-broadening still beat frozen on trials (4 NCT vs 1).

### Layer 2 — Spec: SAFE DEGRADATION on the misfire (the key finding) ✅
**On melanoma, wide-net grounded to generic "Neoplasms" and retrieved non-melanoma
trials (gastric/thyroid/bladder CNN studies) — but cite-or-flag caught every one
and quarantined it:**
- *"No dermoscopy-specific melanoma validation trial was retrieved in this pull —
  the design is mapped from adjacent CNN-oncology imaging studies, so confidence
  is capped."*
- *"Do not import numbers from gastric/thyroid/bladder CNN papers as if they were
  melanoma benchmarks."*
- *"the returned 510(k) dermatology records (K862862, K862864 surgical lasers;
  K861301 bacti plate)… are NOT analogous devices and must not be cited as
  predicates."*

**The bad retrieval never contaminated the spec — it was disclosed and quarantined.
Zero fabrication across all 8 specs.** This is the headline: when disease-recovery
misfires, the system degrades safely rather than confidently citing the wrong
disease's evidence. Frozen's off-target retrieval is likewise honestly flagged
(the frozen DR and melanoma specs carry ~10 hedge/flag markers each). Neither
engine fabricates; wide-net simply gives the model better material to cite, so it
spends fewer words disclaiming off-target retrieval on the on-target cases.

### Layer 3 — Critic panel: real but modest sharpening (weaker than the n=1 demo)
Both arms' panels catch the SAME big blockers (lock intended-use, real FDA predicate
search, powered sample size, subgroup power, concrete clinical action). Wide-net's
edge is narrower than the heart-failure F5b case implied — it occasionally escalates
one blocker to disease-specific science:
- **DR wide-net** flags the **fundus-only DME blind spot → OCT confirmation
  protocol** (a real diabetic-retinopathy nuance frozen's panel missed).
- **NSCLC wide-net** flags **U-Net detector-sensitivity gating** as a
  system-sensitivity pre-condition.
- **Crohn's and melanoma**: near-parity between arms.

So the "frozen spends a blocker on plumbing / wide-net escalates to disease-science"
pattern from F5b reproduces, but partially — clearly on DR and NSCLC, near-parity
on the other two.

## Bottom line

Wide-net's downstream value is **real but modest**, concentrated at **retrieval +
spec** (on-target, richer citations; less wasted hedging), with **smaller,
case-dependent** panel sharpening. The most important result is the **safe-degradation
proof**: the melanoma misfire never produced a misfire spec — cite-or-flag caught
and quarantined the off-target grounding.

## Decision this drives (Option B)

**Recommendation: do NOT run Option B (the other 6 cases, ~40 calls).** It would
add more examples of the same three patterns without changing the qualitative
conclusion, and the retrieval story is already n=10 (the free B2 sweep). n=4
spanning all three tiers is a defensible sample for the qualitative downstream
claim. With the deadline near, bank this and proceed to the FDA build-vs-ship
decision, then submission work.

## Carry-forward for the FDA decision (next)

B3 reconfirms the FDA gap is orthogonal to the frozen-vs-widenet A/B: on melanoma
BOTH arms returned the same non-analogous 510(k) records (surgical lasers, bacti
plate) because the openFDA path keys off generic device keywords, not the disease.
Wide-net's disease recovery does not reach the FDA product-code path. Fixing this
needs a separate indication→product-code bridge — the subject of the next decision.
