# F5 batch — B2 retrieval sweep findings (10 Claude-Science cases, no API key)

*Free retrieval-only sweep: each of 10 single-disease, mechanism-first cases run
through BOTH engines (frozen `engine.py` vs wide-net `experimental/engine_widenet.py`).
Tripwire `2e6d49cdaa3106b6c29ee66b5df37e58` clean at start and end. Raw per-arm
contexts in `scratchpad/f5_batch/<id>_<arm>_context.txt`; metrics in
`f5_batch_retrieval_summary.json` + `_table.md`.*

## Headline numbers

| Metric | Result |
|---|---|
| Frozen surfaced the oracle disease | **0 / 10** |
| Wide-net surfaced the oracle disease | **0 / 10** |
| Gate pass (frozen misses ∧ wide-net recovers) | **0 / 10** |
| FDA sections byte-identical between arms | **10 / 10** |
| Literature query diverged between arms | **10 / 10** |

## What this means (the important nuance)

**The wide-net win did NOT reproduce on these cases — and that is a *correct*,
informative negative, not a regression.** The reason is structural: Claude Science
followed "do not restate the disease" so faithfully that in these 10 cases the
disease name is **entirely absent** from the engine-visible text (model
description + use case + population + setting). The disease lives only in the
`DISEASE:` header, which no engine ever reads.

Wide-net recovers a disease by **reading it from the text** and MeSH-normalizing
it. That is the "buried-but-**present**" scenario the heart-failure demo won on
("...admitted with decompensated **heart failure**"). When the disease word is
**absent**, wide-net has nothing to normalize — and its greedy "grab a medical
noun and normalize it" heuristic latches onto whatever *is* present, which here is
either too broad or outright wrong:

- **NSCLC** → grabs "malignancy" → normalizes to **"Neoplasms"** (generic cancer,
  D009369) — real MeSH, far too broad, not the oracle.
- **Stroke** → grabs "emergency" → normalizes to **"Emergencies"** (D004630) — an
  administrative MeSH term, off-target and arguably worse than raw keywords.
- **COPD** → no candidate noun → falls back to raw keywords (identical to frozen).

So *literature diverged 10/10* is real (the queries differ) but on these cases the
divergence is **noise or mis-grab, not clean disease recovery.** Recovering the
disease here would require **semantic inference** ("KDIGO → acute kidney injury",
"PHQ-9 → depression", "Lung-RADS → lung cancer") — a capability neither engine
has, and a different, bigger problem than the one wide-net solves.

## Two things this DOES establish (both useful for the submission)

1. **The FDA bound is universal, now confirmed across 10 diverse cases.** The
   openFDA sections are byte-identical between arms in **all 10** — wide-net never
   touches the FDA product-code path, exactly as documented. The F5b (heart
   failure) FDA finding was not a one-off; it is the general behavior.

2. **Wide-net's advantage is scoped to "disease present-but-buried," not "disease
   absent."** An honest boundary: wide-net rescues a buried disease name; it does
   NOT infer an unnamed disease from mechanism. And its noun-grab heuristic can
   mis-fire (Neoplasms / Emergencies) when the disease is absent — a candid
   Phase-2 limitation worth stating (a confidence/disease-type guardrail would
   suppress the off-target grab; note F3's disambiguation pop-up only fires on
   *ambiguity between candidates*, so a single confident-but-wrong pick like
   "Emergencies" slips through silently).

## Decision this drives

To upgrade the wide-net win from n=1 to an n=10 **pattern** (the batch's original
goal), the cases must recreate the demo condition: **disease named exactly once,
buried inside the mechanism-first `model_desc`** (e.g. "...to predict onset of
**acute kidney injury** within 48h per KDIGO staging..."). Running the current
"fully-absent" 10 through the paid live spec+panel (B3) would show wide-net ≈
frozen (no recovery) or wide-net mis-grounded (Neoplasms/Emergencies) — not the
pattern we want, and a poor use of the API key.

**Recommendation:** regenerate the 10 cases as "buried-but-present" variants
(one Claude Science round-trip), re-run this free sweep to confirm the gate now
passes, THEN spend the key on B3. Keep this fully-absent sweep as the documented
boundary result.
