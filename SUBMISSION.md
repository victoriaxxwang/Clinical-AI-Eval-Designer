# Hackathon Submission — Clinical AI Eval Designer

Built with Claude: Life Sciences · Build track · Deadline 2026-07-13

> Draft answers to the five required submission fields. Refine wording before
> submitting; the video talk-track (Q3) will be written last, once the app is
> finalized.

---

## 1. Project description — what you built, what you found, why it matters

**What I built.** Clinical AI Eval Designer — a tool that takes what a clinical
AI model does and its clinical context (AI model, clinical use case, patient
population, healthcare setting) and outputs a structured, citable **validation
specification**: study design, sensor/input validation, performance benchmarks,
ground-truth strategy, sample size, subgroup requirements, regulatory pathway,
and post-deployment monitoring — eight fields, each flagged by confidence
(HIGH/MEDIUM/LOW) and by the kind of expert review it still needs.

Critically, it grounds every citation in **live registry data** — it queries
ClinicalTrials.gov, openFDA, and PubMed programmatically *before* the model
writes anything, then uses Claude Fable 5 as a constrained synthesis layer that
maps real records into the structure. It is constrained by design: no invented
thresholds, every quantitative claim carries a real citation or is explicitly
flagged as team-set.

**What I found.** The weeks-long, expert-only process of figuring out *what a
clinical AI model must prove before anyone will adopt it* can be compressed into
a grounded, citable first draft in minutes — and, more importantly, doing it
*safely* is not a retrieval problem, it's a **constraint problem**. An
unconstrained model produces confident, fabricated benchmarks. The value is the
constraint layer that forces honesty (cite-or-flag, confidence tiers,
"certifies / does not certify"), plus grounding that makes citations verifiable
by construction.

**Why it matters.** Clinical AI teams routinely build models that work
technically but stall clinically because they lack the right validation
evidence, and the answer changes by indication, population, and intended claim.
A tool that gives them a rigorous, grounded starting point — while being honest
about what still needs a human — turns weeks of manual literature work into an
expert-review conversation. And it's a template for trustworthy AI in a
high-stakes domain: the safety is enforced at the model-behavior level, not just
the UI.

## 2. Link to your work
- **GitHub:** https://github.com/victoriaxxwang/clinical-ai-eval-designer
  *(ensure the repo is public before submission)*

## 3. Demo video (max 3 minutes)
- **Link:** _TBD — https://youtube.com/watch?v=..._
- **Script:** to be written after the app is finalized. Working blueprint in
  `DEMO_PLAN.md` (Problem/Hook → live 8-field generation showing confidence flags
  and real citations → moat + roadmap). Final talk-track goes here.

## 4. How did you use Claude? Which products? Where did they matter most?

Three distinct roles:

- **Claude Science — the discovery engine.** Where I *proved the concept*: I ran
  the full literature synthesis for HRV-based stress detection on consumer
  wearables (500-participant decentralized design, per-device sensor validation,
  Fitzpatrick skin-tone subgroup analysis, regulatory landscape) grounded in 48
  papers, and it worked. That proof-of-concept is what convinced me the
  structured starting point could be generated automatically.

- **Claude Code — the builder.** Wrote the Streamlit app, the constraint-layer
  system prompt, and the live-registry retrieval pipeline; handled git/repo
  setup. This is where the manual insight became working software.

- **Anthropic API (Claude Fable 5) — the runtime engine.** Every generation runs
  Fable 5 as the constrained synthesis layer over records retrieved live from the
  public registries, with an automatic Opus 4.8 fallback for benign requests a
  safety classifier occasionally false-positives on.

**Where it mattered most:** Claude Science proved the workflow was possible;
Claude Code turned that into a product whose defensibility is the constraint
layer, not the retrieval. The honest framing is that the app is an *automated,
programmatic mirror* of the Claude Science discovery workflow — Claude Science
has no runtime API to call, so I replicated its pattern (grounded retrieval →
constrained reasoning) with direct registry APIs.

## 5. Thoughts / feedback on building with Claude Science

- **What worked well:** Fast, high-quality synthesis across dozens of papers into
  a structured, decision-ready output — exactly the discovery step that normally
  takes an expert weeks. It made the whole product idea credible.
- **Friction / wishlist:** There's no programmatic way to invoke a
  Claude-Science-style deep-research workflow from an application — I had to
  rebuild the retrieval pattern against public registry APIs to productize it. A
  callable "deep research" primitive (retrieve + verify against named sources +
  return real identifiers) would let builders ship the Claude Science experience
  instead of approximating it. Also: surfacing verifiable identifiers (PMIDs,
  NCT numbers, clearance numbers) as first-class, checkable outputs would make
  grounded citation the default rather than something builders have to engineer.
