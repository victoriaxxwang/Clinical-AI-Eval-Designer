# Option 1 — the wide-net + disambiguation prototype

*A standalone writeup of a Phase-2 experiment. This is an **appendix**, not the
submission and not shipped code. The submitted app runs the frozen engine
(`engine.py`); the work described here lives entirely in an isolated copy
(`experimental/engine_widenet.py`) and was never allowed to touch the shipped
engine.*

---

## The one-paragraph version

The shipped engine finds a study's disease only when the write-up **names the
disease early**. On realistic *mechanism-first* descriptions — where the disease is
buried under machine-learning jargon — it misses the condition and the whole citation
search goes off-target. This experiment asked: can a **wide net** (read the entire
case text, not just the first few keywords) recover that miss, and can we then **pick
the right disease** when the wider net inevitably surfaces more than one? The answer to
both is yes, measured: the net recovers the buried disease (**oracle match 2/6 → 4/6**,
all gains on the hard mechanism-first cases, zero regression on the easy ones), and a
three-rule tiebreaker plus a clarifying-question pop-up resolves the multi-disease fork
or asks the user — scoring **10/10** on a combined test slate, and **never making a
silent wrong pick.**

---

## The problem it addresses

The engine grounds every citation by first identifying the clinical condition, then
querying public registries for that condition. The shipped ("Option 2") approach reads
roughly the first dozen keywords of the model description to surface the disease name.

That works when a human or Claude Science writes the case **condition-forward** ("A
model for **heart failure** that ingests..."). But real users — and Claude Science
itself, left to its own phrasing — often write **mechanism-first**: "A gradient-boosted
ensemble ingesting longitudinal structured EHR signals to flag decompensation..." — and
the disease ("heart failure") shows up only in the last sentence, past the keyword
window. An independent 20-case check measured this bound honestly: the shipped surfacing
lands the disease on only **3 of 20** mechanism-first cases. It's a *first-principle*
limit of reading only the opening keywords, not a bug.

---

## The idea: cast a wider net

Instead of the first ~12 keywords of one field, scan the **whole case text**
(model description + use case + population + setting) as single words **and** adjacent
two-word phrases, and run each through the **same** disease-only safety filter the
engine already uses. Two-word phrases matter because many real MeSH headings are
multi-word ("Heart Failure", "Pulmonary Embolism") and a lone word can't match them.

A read-only probe of this idea (no engine edits) recovered disease surfacing from
**2/20 → 17/20** with no loosening of the matching rules. Encouraging enough to build
it properly — in isolation.

---

## How it was built, safely

Everything below lives in `experimental/engine_widenet.py`, a copy. The frozen
`engine.py` was **never opened for edit**. A guardrail (an md5 fingerprint of the frozen
engine, `2e6d49cdaa3106b6c29ee66b5df37e58`) was re-checked at the start and end of every
work session; if it had ever changed, work would have stopped. It never changed.

The work went in four measured steps (F1–F4).

### F1 — the wide net

Built the whole-text unigram-and-bigram scan in the isolated copy. Offline sanity check:
on all three mechanism-first test phrasings the buried disease now surfaces as a
two-word phrase ("heart failure", "kidney disease", "pulmonary embolism") — impossible
for the frozen keyword-only path. On condition-forward phrasings nothing regressed.

### F2 — does the net actually find the disease? (Yes)

Ran the frozen engine and the wide-net engine side by side on 3 fresh clinical topics,
each written **twice** — once condition-forward (the control) and once mechanism-first —
against a live medical-vocabulary lookup, no API key.

| | Frozen (shipped) | Wide-net |
|---|---|---|
| Oracle-heading match, total | **2 / 6** | **4 / 6** |
| Condition-forward controls | identical | identical (**zero regression**) |
| Mechanism-first (heart failure, pulmonary embolism) | disease **absent** from the query | resolves to the **exact** heading |

Every gain came from the mechanism-first cases; the controls were byte-for-byte
unchanged. (The third topic, chronic kidney disease, resolves to an adjacent heading on
*both* engines — a separate vocabulary-map quirk, not a wide-net failure.) **Verdict:
the net earns its keep.**

### F3 probe — the catch: the net finds *too much*

A wider net surfaces more than one disease. A stress test on two comorbidity topics
(heart-failure-in-diabetes; atrial-fibrillation-with-stroke), each written twice,
confirmed the risk cleanly: **more than one disease resolved in all 4 cases.** When the
use case *named* the target disease, the naive "first one that resolves wins" logic
picked correctly. When it named *neither* (mechanism-first), it **silently mispicked**
the distractor — diabetes instead of heart failure, embolic stroke instead of atrial
fibrillation. A silent wrong pick is the worst outcome, so this fork had to be resolved.

### F3 build — three tiebreakers + a clarifying question (10/10)

The fix is a thin wrapper (`resolve_condition`) over the **unchanged** vocabulary
resolver. It applies three rules, in order:

1. **A disease named in the use case wins** outright.
2. **A full two-word heading beats a lone word** that happened to resolve.
3. **Over-generic headings are demoted** ("Disease", "Chronic Disease", etc.).

When those rules still leave a genuine tie — a mechanism-first case where the use case
names *neither* disease and a second real, specific disease also resolves — the engine
raises a **clarifying-question pop-up** offering both diseases, rather than guessing.
Otherwise the pop-up stays silent. (The extra output is purely additive, so any code
reading only the original fields is unaffected.)

Measured live on a combined slate — **10/10**:

- **No-regression (6 single-disease cases): 6/6.** Every previously-working case still
  resolves correctly, and the pop-up **never fires** — the tiebreaker does not
  over-trigger when there's only one disease.
- **Comorbidity (4 two-disease cases): 4/4.** Controls resolve cleanly and silently. The
  two mechanism-first cases that *previously mispicked* now raise the clarifying question
  with **both** diseases on offer.

The result: the buried disease gets found (F2), and the fork it opens is either resolved
by the rules or handed back to the user as a question (F3) — **never a silent wrong
pick.**

---

## Where it sits

This is a **measured Phase-2 prototype, not shipped**. The submitted app still runs the
frozen engine, and the honest bound of that shipped line (surfacing helps only when the
disease is named early) is reported openly in `SUBMISSION.md` and
`eval_results/ablation_findings.md`. What this experiment adds is evidence that the
recovery path is real and bounded — a capability we've built and measured, not a promise
— ready to graduate into the engine as a Phase-2 feature.

**Source of record:** the measurement scripts and results are in `scratchpad/`
(`f2_run.py`, `f3_probe.py`, `f3_build_run.py`, and their `.json`/`.log` outputs); the
code is in `experimental/engine_widenet.py`; the blow-by-blow log is in `INDEX.md`.
