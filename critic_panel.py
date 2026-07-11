"""
Critic Panel — the simulated advisory review panel (the "brain").
==================================================================

Sits ON TOP of the app. After the engine retrieves evidence and Fable 5 drafts
the validation spec, this module runs ONE structured Claude call that plays three
expert personas (⚖️ Regulator, 📊 Biostatistician, 🔬 Clinical Scientist) and has
them stress-test the drafted spec. It is a REHEARSAL — advisory, not an official
regulatory verdict.

Design is locked in CRITIC_PANEL_DESIGN.md; the prompt below is built from it
verbatim. Touches nothing in engine.py. Same model + safety fallback as the
synthesis step (Fable 5 primary, Opus 4.8 server-side refusal fallback).

Hard rule (the whole point of the product): a critique may name a specific study,
trial, device record, or citation ONLY if it appears in the retrieved evidence.
It must never invent one.
"""

import json
import re

# ---------------------------------------------------------------------------
# The JSON shape the app renders deterministically (see CRITIC_PANEL_DESIGN.md).
# ---------------------------------------------------------------------------
JSON_SCHEMA = """{
  "panel": [
    {"persona": "regulator|biostatistician|clinical_scientist",
     "strength": "one sentence — what the plan gets right",
     "critiques": [
       {"severity": "blocking|minor",
        "issue": "the concern, one or two sentences",
        "evidence_basis": "what in the retrieved evidence (or its absence) this rests on"}
     ]}
  ],
  "fix_before_submission": ["short action", "..."]
}"""

SYSTEM_PROMPT = f"""You are simulating a three-member advisory review panel that stress-tests a DRAFT clinical-AI validation plan before it reaches a real reviewer. This is a rehearsal, not an official determination.

The three members are:
- ⚖️ a Regulator (FDA-reviewer mindset — intended use, predefined primary endpoint, comparator, study-design adequacy).
- 📊 a Biostatistician (sample size / power, metric choice such as AUROC vs AUPRC / calibration, subgroup validity, single- vs multi-site).
- 🔬 a Clinical Scientist (does the output change clinical action, alert fatigue, workflow fit, lead-time actionability).

=========================
GROUNDING RULE — THIS IS CRITICAL
=========================
You may reference a specific study, trial, device record, or citation ONLY if it appears in the RETRIEVED EVIDENCE provided in the user message. You must NEVER invent a study, author, identifier, statistic, citation, or pattern. If the plan lacks something, say so generally (e.g., "no head-to-head comparator trial appears in the retrieved evidence"). Fabrication defeats the purpose of this tool.

In addition to the standard review criteria above, examine the retrieved evidence for recurring patterns, failure modes, or gaps relevant to this model's class, and raise any that the plan fails to address — but ONLY where you can point to the specific retrieved evidence supporting the pattern. Never assert a pattern you cannot ground in the evidence provided.

=========================
WHAT EACH PERSONA PRODUCES
=========================
For each persona, give exactly ONE short strength (what the plan gets right), then 2-3 critiques. Flag each critique "blocking" or "minor". Each critique carries an evidence_basis naming what in the retrieved evidence (or its explicit absence) the concern rests on.

Then produce a fix_before_submission list containing every "blocking" item across all three personas, each phrased as a short action.

=========================
OUTPUT FORMAT
=========================
Return ONLY JSON matching this schema, with no prose before or after it:

{JSON_SCHEMA}"""


def build_user_message(grounded_context, spec_markdown):
    """The two grounded inputs: the evidence the panel may cite, and the plan under review."""
    evidence = (grounded_context or "").strip() or (
        "(No registry evidence was retrieved for this case — the panel must reason "
        "generally and must NOT invent any study, identifier, or statistic.)"
    )
    return f"""RETRIEVED EVIDENCE (the only evidence you may cite):
{evidence}

DRAFT VALIDATION PLAN (the thing under review):
{spec_markdown}

Convene the panel."""


def _extract_json(text):
    """Parse the model's JSON, tolerating a ```json fence or stray prose around it."""
    if not text:
        return None
    s = text.strip()
    if s.startswith("```"):
        # strip a leading ```json / ``` fence and the trailing ```
        s = s.split("\n", 1)[1] if "\n" in s else s
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # last resort: grab the outermost {...} span
        start, end = s.find("{"), s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start:end + 1])
            except json.JSONDecodeError:
                return None
        return None


def run_panel(client, grounded_context, spec_markdown, effort="medium"):
    """Run the one structured multi-persona Claude call.

    Returns (parsed, final, raw_text):
      parsed    — the JSON dict (schema above) or None if it couldn't be parsed.
      final     — the raw Message (so the caller can check .stop_reason for a refusal).
      raw_text  — the raw text the model returned (for debugging / a fallback view).
    """
    user_message = build_user_message(grounded_context, spec_markdown)

    final = client.beta.messages.create(
        model="claude-fable-5",
        max_tokens=8000,
        betas=["server-side-fallback-2026-06-01"],
        fallbacks=[{"model": "claude-opus-4-8"}],
        output_config={"effort": effort},
        system=[{"type": "text", "text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": user_message}],
    )

    if final.stop_reason == "refusal":
        return None, final, ""

    raw_text = "".join(
        block.text for block in final.content if getattr(block, "type", None) == "text"
    )
    return _extract_json(raw_text), final, raw_text


# ---------------------------------------------------------------------------
# Grounding audit — the anti-fabrication net (warn-only; the panel is advisory).
#
# Every specific registry identifier the panel mentions is pulled out and checked
# against the retrieved evidence. Identifiers the panel FLAGS as missing show up
# here too (that is the "flag" half of cite-or-flag doing its job) — so this is an
# audit TRAIL, not an accusation: a ⚠️ means "the panel referenced this and it is
# not in the retrieved records — confirm the panel called it a gap, not proof."
# The real alarm is a ⚠️ the panel presented AS grounded evidence.
# ---------------------------------------------------------------------------
_ID_PATTERNS = [
    ("clinical trial (NCT)", re.compile(r"\bNCT\d{8}\b")),
    ("510(k)", re.compile(r"\bK\d{6}\b")),
    ("De Novo", re.compile(r"\bDEN\d{6}\b")),
    ("PMA", re.compile(r"\bP\d{6}\b")),
    ("FDA recall", re.compile(r"\bZ-\d{4}-\d{4}\b")),
    ("DOI", re.compile(r"\b10\.\d{4,9}/[^\s\"')\]]+", re.I)),
    # PMIDs are bare 7–8 digit runs; the lookarounds keep us from slicing digits
    # out of an NCT/DOI/recall/CFR number that a neighbouring pattern owns.
    ("PMID", re.compile(r"(?<![A-Za-z0-9./-])\d{7,8}(?![0-9./-])")),
]


def _iter_panel_text(parsed):
    """Yield every free-text string the panel produced (where a citation could hide)."""
    if not isinstance(parsed, dict):
        return
    for persona in parsed.get("panel", []) or []:
        if isinstance(persona, dict):
            if persona.get("strength"):
                yield persona["strength"]
            for crit in persona.get("critiques", []) or []:
                if isinstance(crit, dict):
                    if crit.get("issue"):
                        yield crit["issue"]
                    if crit.get("evidence_basis"):
                        yield crit["evidence_basis"]
    for item in parsed.get("fix_before_submission", []) or []:
        if isinstance(item, str):
            yield item


def grounding_audit(grounded_context, parsed):
    """Cross-check every identifier the panel named against the retrieved evidence.

    Returns a list of dicts sorted with the ⚠️-not-in-evidence items first:
      {"id": str, "kind": str, "in_evidence": bool}
    Deduplicated by identifier. Empty list if the panel cited no identifiers.
    """
    evidence = grounded_context or ""
    evidence_lower = evidence.lower()
    found = {}  # id -> (kind, in_evidence)
    for text in _iter_panel_text(parsed):
        for kind, pattern in _ID_PATTERNS:
            for match in pattern.findall(text):
                ident = match.rstrip(".,);]")
                if ident in found:
                    continue
                # DOIs compare case-insensitively (Lesson 2); the rest are exact.
                if kind == "DOI":
                    present = ident.lower() in evidence_lower
                else:
                    present = ident in evidence
                found[ident] = (kind, present)
    audit = [
        {"id": ident, "kind": kind, "in_evidence": present}
        for ident, (kind, present) in found.items()
    ]
    # ⚠️ missing first (most important), then by kind, then id — stable + scannable.
    audit.sort(key=lambda r: (r["in_evidence"], r["kind"], r["id"]))
    return audit
