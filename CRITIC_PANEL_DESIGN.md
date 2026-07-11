# Critic Panel — Design Spec (Window A output)

**Status:** DESIGN LOCKED 2026-07-10 (Victoria approved). No code yet — this is the
build brief for Window B. The Critic Panel sits ON TOP of the app (`app.py` + one
new file) and touches NOTHING in the deterministic `engine.py`.

## What it is (plain English)
After the app (1) gathers real evidence from public registries and (2) drafts a
validation spec, the Critic Panel adds a (3) **simulated advisory review panel**:
three Claude-played expert voices stress-test the drafted spec before a real
reviewer ever sees it. It is a **rehearsal, advisory — NOT an official regulatory
verdict.** A disclaimer says so on screen.

## The three personas
| Persona | Mindset | Standard focus areas |
|---|---|---|
| ⚖️ Regulator | FDA-reviewer | intended use, predefined primary endpoint, comparator, study-design adequacy |
| 📊 Biostatistician | numbers referee | sample size / power, metric choice (AUROC vs AUPRC/calibration), subgroup validity, single- vs multi-site |
| 🔬 Clinical Scientist | the doctor who'd use it | does the output change clinical action, alert fatigue, workflow fit, lead-time actionability |

## Two layers of where critiques come from (honesty note)
1. **Review criteria = fixed expert knowledge** (standard FDA/biostat/clinical
   review questions baked into the prompt). NOT pulled from the search.
2. **Specific findings = grounded** in the engine's retrieved evidence + the spec.
3. **Evidence-informed focus (Victoria's call, approved):** the panel may ALSO
   surface recurring patterns / failure modes it sees IN the retrieved evidence —
   but ONLY where it can point to the specific evidence. This is where the LLM
   earns its keep over a rule-based checklist. Never assert an ungrounded pattern.

## Output shape per persona
- exactly **one strength** line (what the plan gets right), then
- **2–3 critiques**, each flagged `blocking` (🔴) or `minor` (🟡), each with an
  `evidence_basis`.
- a **fix_before_submission** list = every 🔴 item as a short action.

## The critical grounding rule
A critique may name a specific study / trial / device record / citation ONLY if it
appears in the retrieved evidence. NEVER invent a study, author, identifier,
statistic, citation, or pattern. If the plan lacks something, say so generally
("no head-to-head comparator trial appears in the retrieved evidence"). Fabrication
defeats the product's whole purpose.

## Technical shape (for Window B)
- **ONE structured Claude call**, all three personas in one prompt. Light, not a
  heavy multi-agent loop.
- Model: **`claude-fable-5`** with **`claude-opus-4-8` server-side refusal
  fallback** (`betas: ["server-side-fallback-2026-06-01"]`,
  `fallbacks: [{"model": "claude-opus-4-8"}]`) — same as the synthesis step.
- **Returns JSON** (schema below) so the app renders clean expandable blocks.
- Display (Window C): **simple text blocks first** — one expandable section per
  persona with the flags, then a "Fix before submission" panel. Prettify later
  only if time remains.
- Plug-in point: a **"Convene review panel"** button in `app.py` that appears AFTER
  a spec is generated. Inputs it passes: the retrieved evidence bundle + the
  generated validation spec.

## JSON schema
```json
{
  "panel": [
    {"persona": "regulator|biostatistician|clinical_scientist",
     "strength": "one sentence",
     "critiques": [
       {"severity": "blocking|minor",
        "issue": "the concern, one or two sentences",
        "evidence_basis": "what in the retrieved evidence (or its absence) this rests on"}
     ]}
  ],
  "fix_before_submission": ["short action", "..."]
}
```

## The prompt

### System instruction
> You are simulating a three-member advisory review panel that stress-tests a
> *draft clinical-AI validation plan* before it reaches a real reviewer. This is a
> rehearsal, not an official determination. The three members are: ⚖️ a Regulator
> (FDA-reviewer mindset — intended use, predefined endpoints, comparators,
> study-design adequacy); 📊 a Biostatistician (sample size/power, metric choice,
> subgroup validity, single- vs multi-site, calibration); 🔬 a Clinical Scientist
> (does the output change clinical action, alert fatigue, workflow fit, lead-time
> actionability).
>
> **Grounding rule — this is critical:** You may reference a specific study, trial,
> device record, or citation ONLY if it appears in the RETRIEVED EVIDENCE provided
> below. You must never invent a study, author, identifier, statistic, citation, or
> pattern. If the plan lacks something, say so generally (e.g., "no head-to-head
> comparator trial appears in the retrieved evidence"). Fabrication defeats the
> purpose of this tool.
>
> **In addition to the standard review criteria, examine the retrieved evidence for
> recurring patterns, failure modes, or gaps relevant to this model's class, and
> raise any that the plan fails to address — but ONLY where you can point to the
> specific retrieved evidence supporting the pattern. Never assert a pattern you
> cannot ground in the evidence provided.**
>
> For each persona: give exactly one short **strength** (what the plan gets right),
> then 2–3 **critiques**. Flag each critique `blocking` or `minor`. Then produce a
> **fix_before_submission** list containing every `blocking` item, phrased as a
> short action.
>
> Return ONLY JSON matching the schema above.

### User message (filled at runtime)
> RETRIEVED EVIDENCE (the only evidence you may cite):
> `{the engine's grounded evidence bundle}`
>
> DRAFT VALIDATION PLAN (the thing under review):
> `{the generated validation spec}`
>
> Convene the panel.

## Advisory disclaimer (shown on screen)
> ⚠️ This is a simulated advisory review to help you stress-test your plan before a
> real review. It is not an official regulatory determination and does not
> guarantee any outcome.
