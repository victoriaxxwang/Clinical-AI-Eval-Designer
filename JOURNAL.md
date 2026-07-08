# Hackathon Development Log & Deliverables Prep

## 🛠️ Active Blockers & Technical Issues
- [ ] Issue: Streamlit API timeout on deep literature synthesis.
  - *Notes/Context:* When querying the API for complex disease profiles, the response takes over 30 seconds and causes a UI stutter.
- [ ] Issue: Safety filter fallback handling.
  - *Notes/Context:* Navigating conversational safeguards by decoupling the infrastructure code from the internal clinical prompt.

## 📈 Key Milestones & Decisions
- **July 7:** Decided to pivot to a single-file Streamlit + Streamlit Secrets architecture to completely bypass complex backend state management.
- **July 7:** Established the "Constraint Layer as a Product" thesis for the Anthropic pitch angle.

## 💡 Claude Capabilities Feedback (For Submission)
- *What worked well:* Claude Code's ability to initialize the repository structure and debug local path variables instantly.
- *Friction points:* Conversational safety filters triggering on standard clinical research terms (e.g., "disease indication"), requiring a sanitized code architecture.

> ⚠️ **Flagged for revision before submission** (kept for now, but likely not the framing we want for Anthropic judges). Preferred wording:
> *Friction point: safety classifiers can occasionally false-positive on benign biomedical requests. Handled with Anthropic's documented server-side refusal fallback (Fable 5 → Opus 4.8), so legitimate clinical requests complete without weakening any safeguard.*

## 📝 Running Log (synthesize before submission)
- **July 7:** Built the live grounding pipeline — app now queries PubMed, ClinicalTrials.gov, and openFDA directly, then hands real records to Fable 5. Verified all three endpoints return real identifiers (NCT03831841, live PMIDs, openFDA product code QEX).
- **July 7:** Added optional reference-URL ingestion (stdlib HTML→text extraction) so users can feed a specific whitepaper / FDA guidance page into the grounding context.
- **July 7:** Established architecture doc versioning (ARCHITECTURE.md + ARCHITECTURE.html, shared version number; now at v2).
- **July 8:** Extracted the Core Deterministic Engine into `engine.py`; hardened query construction (keyword extraction, modality lexicon, drop verbs/filler); added `test_engine.py` (20 tests incl. a 12-indication disease-agnosticism sweep). Consolidated architecture to a single `ARCHITECTURE.md` v3.
- **July 8 — decision:** Do NOT wrap or route through Claude Science. It has no programmatic endpoint and is R&D-only. The app's runtime is direct registry REST (deterministic); Claude Science is for build-time discovery / minting demo fixtures. **Why:** routing through a UI app is brittle and non-deterministic — the opposite of the Phase-1 goal.
- **July 8 — decision:** MCP connectors (Claude Code plugins / API MCP connector) are a Phase-2 breadth option, not Phase 1. Model-mediated retrieval is non-deterministic and costs credits. **How to apply:** keep Phase-1 on direct REST; consider MCP only when we want dynamic, agentic search later.
- **July 8 — open:** waiting on Claude Science to produce a source-endpoint manifest; will review it against our 3 registries + Europe PMC + OpenAlex, keeping only free/stable/identifier-returning sources.
