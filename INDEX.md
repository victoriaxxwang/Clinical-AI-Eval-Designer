# Project Index — Clinical AI Eval Designer

The map of this repo. Read this first after a compaction or a break; it points to
everything else.

## What this is (one paragraph)
A Streamlit app (`app.py`) that turns a clinical AI model + its context into a
structured, citable **8-field validation specification**. It grounds every
citation by querying public registries **live** (ClinicalTrials.gov v2, openFDA,
and a merged literature layer — Europe PMC + OpenAlex + Semantic Scholar, PubMed
fallback — all DOIs Crossref-verified) *before* prompting the model, then uses
**Claude Fable 5** purely as a
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
| `app.py` | UI layer: inputs, constraint-layer prompt, Fable 5 call, bundle output | ✅ built, compiles; not yet run end-to-end |
| `engine.py` | **Core Deterministic Engine**: registry retrieval + query building (no UI, importable, unit-tested) | ✅ hardened, live-verified |
| `test_engine.py` | 42 tests: query determinism, JSON field-path parsing, 12-indication sweep, Crossref verify, snapshot timestamp, multi-provider literature merge/dedup, openFDA PMA/MAUDE/recall + Drugs@FDA/label/FAERS parse+resilience, intervention-type gate, + two-tier golden gate | ✅ 41 pass / 1 skipped (offline); live gate 2 pass |
| `retrieval_sources_manifest.json` | Source-of-truth: 16 registry endpoints + params + identifier fields + toggles (from Claude Science) | ✅ saved, valid |
| `claude_code_task_brief.md` | Implementation spec for the retrieval expansion (references the manifest) | ✅ saved |
| `golden_validation_spec_HRV.md` | **Golden reference** HRV spec from Claude Science (hand-grounded, 18 DOIs + 15 FDA records) — the demo/diff target | ✅ saved |
| `golden_expected_ids.json` | The 39 identifiers the golden spec used — objective retrieval-coverage target for `test_engine.py` | ✅ saved |
| `COMPARISON.md` | **Golden-vs-app analysis (2026-07-08):** live pipeline hits 0/39 golden IDs today; evidence-based re-prioritized punch list | ✅ key finding |
| `requirements.txt` | Deps: streamlit, anthropic, requests | ✅ |
| `requirements-dev.txt` | Dev tools: markdown (render_docs), pytest (tests) | ✅ |
| `README.md` | Public-facing: what it is + how to run | ✅ |
| `SUBMISSION.md` | Draft answers to the 5 hackathon questions (video script TBD) | ✅ draft |
| `DEMO_PLAN.md` | 3-min video blueprint | ✅ |
| `JOURNAL.md` | Dev log: blockers, decisions, running log | ✅ |
| `ARCHITECTURE.md` | **Canonical** — how it works: Phase 1 (built) + Phase 2 (future) + Path A/B appendix | ✅ v3, consolidated |
| `CORE_ENGINE_INTEGRATION_BLUEPRINT.md` | Path A/B code detail | ⚠️ candidate for deletion (now folded into ARCHITECTURE appendix) — confirm |
| `render_docs.py` | Render any `.md` → styled HTML in `docs_html/` (git-ignored). Run `pip install markdown` once, then `python render_docs.py` | ✅ |
| `GIT_DEPLOYMENT_GUIDE.md` | Git/deploy ops | ✅ |
| `INDEX.md` | This map | ✅ |

## Locked decisions (settled — don't relitigate after compaction)
- **No Claude Science endpoint.** Claude Science is the discovery/R&D workbench; it has no API to call from the app. It proved the concept — it is not a runtime dependency.
- **Phase-1 runtime = direct REST to public registries** (ClinicalTrials.gov, openFDA, PubMed). Deterministic, free, verifiable by identifier. This is `engine.py`, done and tested.
- **MCP connectors (Claude Code plugins / Anthropic API MCP connector) = Phase-2 breadth option, not Phase 1.** They're model-mediated → nondeterministic + cost credits, which conflicts with the Phase-1 determinism goal. Build-time MCP use (pulling fixtures) is fine; runtime MCP is Phase 2.
- **Architecture confirmed unchanged** after the Claude Science / MCP brainstorm.

## Next-session plan (agreed 2026-07-08 — do after compaction)
**Sequence:** Tier A → Tier B → 10-case eval → GitHub → demo script. Phase-2 (critics, marketing agent) stays a roadmap item. Fixes #1–#4 AND Tier A are DONE (see COMPARISON.md).
- [x] **Tier A (cheap, do-regardless) — DONE 2026-07-08 (see COMPARISON.md → "Results after Tier A"):** (1) **snapshot + UTC `retrieval_timestamp`** — `build_grounded_context` now returns `(context, statuses, timestamp)`, stamped into a `### Retrieval Metadata` header + the bundle (the REAL regulator guarantee, frozen-once-generated); (2) literature cap 8→15 (context cap 9000→20000, sections independently bounded); (3) **`coverage_gaps` honesty note** — a `### Coverage & Retrieval Gaps` section ALWAYS emitted, names the PAID unreachable DBs + un-queried openFDA PMA/MAUDE/recall + ex-US regulators; (4) **Crossref verify** — `search_europepmc(verify=True)` drops 404 DOIs (keeps paper via PMID), marks confirmed DOIs `✓Crossref` (live 12/13 verified). Tests 27 pass / 1 skip; live gate 2 pass.
- **Tier B (breadth, each with a test):** [x] **(1) DONE 2026-07-09** — FREE sources **OpenAlex** + **Semantic Scholar** merged with Europe PMC, deduped by DOI/PMID, Crossref-verified (`search_literature`; see COMPARISON.md → "Results after Tier B (1)"; golden 2/39→**4/39**, first literature gain). [x] **(2) DONE 2026-07-08** — openFDA **PMA / MAUDE / recall** (`search_openfda_safety`; Class III pathway + post-market safety signals — wired into `build_grounded_context` as its own section, `coverage_gaps_note` updated; see COMPARISON.md → "Results after Tier B (2)"). [x] **(3) DONE 2026-07-08** — openFDA **drug/biologic** endpoints (`search_openfda_drug`: Drugs@FDA approvals / SPL labeling / FAERS adverse events), gated by an explicit **intervention-type selector** (device / drug / both) threaded through `build_grounded_context`; `coverage_gaps_note(intervention_type)` now truthful per-run; live-verified (warfarin/insulin/pembrolizumab); see COMPARISON.md → "Results after Tier B (3)". Remaining: **(4) MeSH** normalization LAST.
- **Eval:** 10-use-case golden comparison vs Claude Science, scored with the **reframed** metric (COMPARISON.md Lesson 2 — deterministic exact, literature as ≥K resolvable IDs). Extend `scratchpad/coverage_check.py` into a repeatable harness.
- **Determinism insight (for README/SUBMISSION):** **"reproducible + verifiable, not bit-identical."** Snapshot delivers the regulator guarantee; do NOT claim identical citations. Full rationale in JOURNAL 2026-07-08.
- **Phase 2 (after Phase-1 solid):** multi-agent **critic QC framework** (medium difficulty; a safety layer) + optional **marketing/competitive agent** (scope decision). Agent guardrails listed in JOURNAL 2026-07-08.

## Open to-dos
- [x] Run `app.py` end-to-end with a real API key — **the Phase-1 gate: PASSED 2026-07-08.** Headless smoke test on the HRV case: live retrieval (6 CT.gov + 10 openFDA + 8 PubMed) → full grounded 8-field spec in ~90s. Finding: Fable 5 refuses benign clinical inputs (safety false-positive); the Opus 4.8 server-side fallback catches it and generates the spec — so clinical inputs currently run on Opus 4.8. Decision: keep Fable-primary + fallback, framed honestly. Still TODO: (a) second run with web search ON (test `pause_turn` loop), (b) run the actual Streamlit UI once (`streamlit run app.py`) to confirm the rendering path.
- [x] Review Claude Science's source list — done. Saved `retrieval_sources_manifest.json` (16 sources) + `claude_code_task_brief.md`. Verdict below.

### Phase 1 — retrieval expansion (end-to-end run PASSED; now do this)
**Re-prioritized 2026-07-08 by the golden comparison — see `COMPARISON.md`.** The live
pipeline retrieves 0/39 golden identifiers, and the top causes are (1) `build_queries` drops
the model's distinctive terms and (2) openFDA uses one narrow keyword. New top-priority order:
- [x] **(NEW #1) Fixed `build_queries`** — query is now condition+method ("stress psychological heart rate", was "continuous passive stress daily"); PubMed returns on-topic papers. Tests 20/20.
- [x] **(NEW #2) Multi-term openFDA sweep** — `search_openfda` takes a term list (`fda_terms`); records 5→11 incl. **SEN**. Golden FDA 0→1/7.
- [x] **(NEW #2b) Threaded the `setting` input into `fda_terms`** — "consumer wellness" → openFDA "wellness" → **PWC** (correct General-Wellness class) now recovered *plus* SEN. Golden FDA 1→2/7, overall 1→2/39. Same change: reworked `search_openfda` to a per-term budget (≤3 records/term, both endpoints) so generic terms can't starve specific ones or truncate PubMed under the context cap. Tests 20/20. See COMPARISON.md → "Results after fix #2b".
- [x] **(NEW #3) Added Europe PMC** as the primary literature source (`search_europepmc`), PubMed kept as auto-fallback. Returns **PMID + DOI** in one call + indexes preprints. **DOIs retrieved 0 → 8 (all resolvable, on-topic).** Golden exact-DOI stays 0/18 — the *correct* Lesson-2 result (ranked search ≠ a curated set; the real bar is "K on-topic resolvable DOIs", now met). Tests 22/22. See COMPARISON.md → "Results after fix #3".
- [x] **(NEW #4) Reframed the golden test** in `test_engine.py` (two tiers): OFFLINE `test_golden_queries_target_the_deterministic_set` (always runs — asserts fda_terms carry "wellness"→PWC + "stress"→SEN; locks in #1/#2b) and LIVE opt-in `test_golden_live_retrieval_coverage` (skipped unless `RUN_LIVE_GOLDEN=1` — asserts PWC+SEN exactly, literature as a ≥5 PMID/DOI floor, and one DOI resolves at Crossref). Default suite: **23 passed, 1 skipped**; live gate: **2 passed**. See COMPARISON.md → "Results after fix #4".
- [~] **Quick wins:** UTC `retrieval_timestamp` in the bundle — **DONE** (Tier A #1). Still open: pin explicit sort keys on every registry query; reframe README/SUBMISSION prose to "reproducible + verifiable, not bit-identical".
- [x] Wire **Europe PMC** (PMID+PMCID+DOI in one call) — DONE (fix #3) + **Crossref** DOI verification pass — DONE (Tier A #4, `search_europepmc(verify=True)`; drops 404 DOIs, marks verified `✓Crossref`).
- [x] Add **openFDA PMA / MAUDE / recall** (Class III pathway + Post-Deployment Monitoring safety signal) — DONE 2026-07-08 (Tier B 2, `search_openfda_safety`; endpoint-outer/per-endpoint budget so PMA isn't starved, per-endpoint try/except resilience; live-verified: glucose→CGM PMAs P150019/P160048, ECG→MAUDE+recalls; 2 parse/resilience tests + 1 no-match test)
- [x] Add **drug/biologic endpoints** (Drugs@FDA / SPL label / FAERS) — DONE 2026-07-08 (Tier B 3, `search_openfda_drug`; endpoint-outer/per-endpoint budget mirroring safety; FAERS shows the report's full drug SET not drug[0] so the queried drug is visible; live-verified warfarin→JANTOVEN/boxed-warning/subdural-haematoma, insulin→BLA biologics, pembrolizumab→KEYTRUDA BLA125514; 3 parse/resilience + 1 gate + 1 drug-terms + 1 coverage test)
- [x] Add an **intervention-type input** (device / drug-biologic / both) — DONE 2026-07-08 (chose an EXPLICIT selector over inference — maximally deterministic + auditable regulatory-pathway declaration; default = device, so existing behavior/tests unchanged; radio in app.py form → `intervention_type` param on `build_grounded_context`)
- [x] Add the **`coverage_gaps` honesty flag** to the bundle — DONE (Tier A #3, `coverage_gaps_note()` → a `### Coverage & Retrieval Gaps` section always emitted; names Embase/PsycINFO/Cochrane/Scopus/WoS/CINAHL + un-queried openFDA/ex-US regulators)
- [ ] **MeSH normalization LAST** (highest complexity; disease-agnostic, not stress-specific)
- [ ] **SKIP:** WHO ICTRP (flaky API) and direct medRxiv API (date-window, not keyword) — get preprints via Europe PMC instead
- [ ] Write the vetted decisions into `SOURCES.md`
- [ ] Push local git repo to GitHub (`git push -u origin main`)
- [x] Consolidate architecture into one canonical `ARCHITECTURE.md` (v3)
- [ ] Confirm `CORE_ENGINE_INTEGRATION_BLUEPRINT.md` can be deleted (now folded into the ARCHITECTURE appendix)
- [x] Harden Phase 1 retrieval (query construction, device-keyword selection) + add tests (8/8 pass); found `population` is a poor retrieval filter → drives subgroup reasoning instead
- [x] Emit Phase-1 bundle: spec + source records travel together (download)
- [ ] Add `st.session_state` cache so re-runs don't re-hit registries (rate-limit safety) — Phase 1 polish, do after first successful run
- [ ] Decide the JOURNAL safety-framing reframe (currently flagged, not applied)
- [ ] Write the final demo video talk-track script (after the app is finalized)

## Viewing docs as HTML
`ARCHITECTURE.html` is no longer committed. Instead, generate HTML on demand:
`pip install markdown` (once) → `python render_docs.py` → open `docs_html/*.html`.
For quick edits, VS Code's built-in Markdown preview (`Cmd+Shift+V`) needs no
files at all and updates live.
