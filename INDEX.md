# Project Index — Clinical AI Eval Designer

The map of this repo. Read this first after a compaction or a break; it points to
everything else.

## What this is (one paragraph)
A Streamlit app (`app.py`) that turns a clinical AI model + its context into a
structured, citable **8-field validation specification**. It grounds every
citation by querying public registries **live** (ClinicalTrials.gov v2, openFDA,
PubMed) *before* prompting the model, then uses **Claude Fable 5** purely as a
constrained synthesis layer (no invented numbers, cite-or-flag, confidence +
expert-review tiers). Discovery was proven manually in **Claude Science**; the
app is the automated, programmatic mirror of that workflow.

## Key facts
- **Model:** `claude-fable-5` (auto-fallback `claude-opus-4-8`). Fable needs 30-day data retention.
- **Runtime engine:** Anthropic API + live registry APIs. **Not** a Claude Science API call (there is none).
- **Repo:** https://github.com/victoriaxxwang/clinical-ai-eval-designer
- **Run:** `python3 -m venv .venv && source .venv/bin/activate` → `pip install -r requirements.txt` → add key to `.streamlit/secrets.toml` → `streamlit run app.py`
- **Deadline:** 2026-07-13 (Built with Claude: Life Sciences hackathon, Build track)

## File map
| File | What it's for | Status |
|---|---|---|
| `app.py` | The app: retrieval pipeline + constrained synthesis | ✅ built, compiles; not yet run end-to-end |
| `requirements.txt` | Deps: streamlit, anthropic, requests | ✅ |
| `README.md` | Public-facing: what it is + how to run | ✅ |
| `SUBMISSION.md` | Draft answers to the 5 hackathon questions (video script TBD) | ✅ draft |
| `DEMO_PLAN.md` | 3-min video blueprint | ✅ |
| `JOURNAL.md` | Dev log: blockers, decisions, running log | ✅ |
| `ARCHITECTURE.md` (+`.html`) | How the current system works | ⚠️ consolidating (see to-dos) |
| `SYSTEM_ARCHITECTURE_FUTURE_STATE.md` | Future state: Core-First-Agents-Later | ⚠️ merge into one arch doc |
| `CORE_ENGINE_INTEGRATION_BLUEPRINT.md` | Path A/B code-level detail | ⚠️ merge or keep as appendix |
| `GIT_DEPLOYMENT_GUIDE.md` | Git/deploy ops | ✅ |
| `INDEX.md` | This map | ✅ |

## Open to-dos
- [ ] Run `app.py` end-to-end with a real API key (nothing has actually generated yet)
- [ ] Push local git repo to GitHub (`git push -u origin main`)
- [ ] **Consolidate the architecture files into one** (decision pending — see below)
- [ ] Harden Phase 1 retrieval: query construction, use `population` input, add tests
- [ ] Add `st.session_state` cache so re-runs don't re-hit registries (rate-limit safety)
- [ ] Decide the JOURNAL safety-framing reframe (currently flagged, not applied)
- [ ] Write the final demo video talk-track script (after the app is finalized)

## Architecture consolidation (in progress)
Three files currently overlap on "how it works": `ARCHITECTURE.md`,
`SYSTEM_ARCHITECTURE_FUTURE_STATE.md`, `CORE_ENGINE_INTEGRATION_BLUEPRINT.md`.
Plan: collapse to a single canonical architecture doc using the **"Core First,
Agents Later"** framing — Phase 1 deterministic engine (built) + Phase 2 agentic
expansion (future: Multi-Agent Critic + Competitive Intelligence tracks).
Structure decisions pending user input.
