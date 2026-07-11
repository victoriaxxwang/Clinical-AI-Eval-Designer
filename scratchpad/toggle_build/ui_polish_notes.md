# UI polish notes (deferred — after toggle commit + FDA decision)

Captured during the toggle smoke test (wide-net run on the diabetic-retinopathy
case). These are Victoria's demo-facing UI observations, to address later — NOT
blockers for committing the toggle.

## Observations (2026-07-11, wide-net run)
1. **Dense text** — the output (grounding context + spec) has a lot of text
   bundled together; hard to scan. Wants more visual breaking-up / whitespace /
   sectioning for the demo.
2. **Slow load** — a run takes a while (live registry pulls + Fable 5 synthesis +
   critic panel). Consider: clearer progress feedback, or a lower default effort
   for demo takes (medium was fine in B3), or streaming the spec as it generates.

## Ideas to consider (not decided)
- Break the spec's 8 fields into cleaner visual sections / cards instead of one
  dense block.
- Progress: more granular spinner stages, or stream the spec tokens live.
- The "Live data retrieved" code block is long — consider collapsing by default
  or summarizing counts (N trials / N papers / N FDA records) above the raw dump.

## Status
Deferred. Belongs in the "app polish (timeboxed)" to-do, AFTER the toggle is
committed and the FDA build-vs-ship decision is made.
