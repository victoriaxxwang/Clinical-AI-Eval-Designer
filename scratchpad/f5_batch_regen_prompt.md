# Claude Science regeneration prompt — "buried-but-present" 10 cases (F5 batch, take 2)

*Paste the block below into Claude Science. Goal: same 10 diseases/areas as the
first batch, but rewritten so the disease is NAMED EXACTLY ONCE, buried inside the
mechanism-first MODEL_DESC — recreating the heart-failure demo condition
(disease present-but-buried), which is what the wide-net engine recovers and the
frozen engine misses. Bring the response back and I'll re-run the free B2 sweep to
confirm the gate now passes before we spend the API key.*

---

I need 10 clinical AI/ML model test cases, one per case, across these 10 fixed
clinical areas and primary conditions (keep these exact diseases, one per case):

1. Non-small cell lung cancer
2. Acute ischemic stroke
3. Chronic obstructive pulmonary disease
4. Acute kidney injury
5. Pulmonary tuberculosis
6. Diabetic retinopathy
7. Melanoma
8. Crohn's disease
9. Type 2 diabetes mellitus
10. Major depressive disorder

For each case give these fields, in this order:

DISEASE: the primary condition (from the list above).

MODEL_DESC: a technical, architecture-forward description of the model (layer
types, backbone, inputs, feature engineering, outputs) — the mechanism should
dominate. CRITICAL CONSTRAINT: name the disease by its standard clinical name
**exactly once**, and bury that mention in a **non-opening** clause (e.g. the
last sentence, as a "...in patients with <disease>" or "...to predict onset of
<disease>..." clause). Do NOT put the disease in the first sentence, and do NOT
repeat it. Everywhere else, refer only to mechanisms, biomarkers, imaging
findings, or scores. Use the disease's standard name (e.g. "acute kidney injury",
"non-small cell lung cancer", "chronic obstructive pulmonary disease") so it is
recognizable, not an abbreviation or a euphemism.

USE_CASE: the task the model performs, phrased as a function WITHOUT naming the
disease (e.g. "continuous inpatient deterioration monitoring").

POPULATION: the intended patient population (a clinical phrase; may be generic).

SETTING: the care setting.

Number them Case 1 through Case 10. Keep each case to a single primary condition.
Do not use heart failure. The only change from a normal mechanism-first write-up
is that constraint in MODEL_DESC: the disease must appear once, buried, in its
standard clinical name.
