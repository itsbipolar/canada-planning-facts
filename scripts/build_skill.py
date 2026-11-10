"""Generates the Agent Skill (SKILL.md, references/facts.md) and shared/facts.json from facts.yaml (SPEC.md sections 3 and 7).
Never hand-edit the outputs. Run: uv run python scripts/build_skill.py   (CI fails if they differ from a fresh build)."""
from __future__ import annotations

import json
from pathlib import Path

from canada_planning_facts.facts import load_facts
from canada_planning_facts.schema import Status
from canada_planning_facts.service import _plain

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugin" / "skills" / "canada-planning-facts"
LABEL = "Prototype. AI-assisted. Reference data: verify at the source. Education, not advice."


def facts_json() -> str:
    facts = load_facts().facts
    rows = []
    for f in facts:
        if f.status in (Status.confirmed, Status.pending):  # an unverified value is never exported
            rows.append({"id": f.id, "series": f.series, "title": f.title, "kind": f.kind.value, "jurisdiction": f.jurisdiction.value,
                         "tax_year": f.tax_year, "value": _plain(f.value), "unit": f.unit.value, "source_url": f.source_url,
                         "authority": f.authority.value, "as_of": f.as_of.isoformat(), "status": f.status.value})
    return json.dumps({"_note": "Generated from facts.yaml. " + LABEL, "facts": rows}, indent=2, ensure_ascii=False) + "\n"


def facts_md() -> str:
    out = ["# Verified facts", "", f"_{LABEL}_", "", "Only confirmed values are listed as facts. Pending means not yet published.", ""]
    for f in load_facts().facts:
        if f.status is Status.confirmed:
            v = _plain(f.value)
            val = "a table (use get_fact or get_brackets)" if isinstance(v, list) else f"{v} ({f.unit.value})"
            out.append(f"- `{f.id}`: {f.title}: {val}. Source: {f.source_url} (read {f.as_of.isoformat()}).")
        elif f.status is Status.pending:
            out.append(f"- `{f.id}`: {f.title}: **not yet published** as of the last check ({f.as_of.isoformat()}).")
    return "\n".join(out) + "\n"


SKILL_MD = f"""---
name: canada-planning-facts
description: >-
  Answers Canadian planning-rule questions (TFSA, RRSP, FHSA limits, CPP and OAS ages and rules, federal and Ontario tax brackets, RRIF minimums) with the value, its official source, tax year and the date it was read. Says "not yet published" for figures that are not out yet and never guesses. Gives general rules only: for personal "should I" questions it explains the rule and the trade-offs and points to a qualified professional. Use for questions about Canadian registered-plan limits, public pension rules or tax brackets.
license: MIT
---

# Canada Planning Facts

{LABEL}

## How to answer
1. Use the `canada-planning-facts` MCP tools for any figure or rule: `get_limit`, `get_brackets`, `get_fact`, `list_pending`, `boc_series`. Do not answer a figure from memory.
2. Give the value with its tax year, its source link and the date it was read.
3. If the tool says a value is **pending** ("not yet published as of <date>"), say exactly that and give the latest published value with its source. Never estimate next year's figure.
4. If the tool says "Not in the verified facts file", say so. Do not fill the gap.
5. Add: "Education only, not personal advice. Verify at the source."

## The advice line
- General rules and neutral trade-offs: answer them. "How does the OAS recovery tax work?" is an education question and must be answered, not refused.
- Personal decisions ("Should I take CPP at 60?", "Is it better for me to ...?"): give the general rules that bear on it, list the trade-offs neutrally, and say that a qualified professional who knows the whole situation can help. Never recommend what the person should do.
- Never give a person's own tax or benefit amount as a conclusion; show how the rule works instead.

## What is covered
See `references/facts.md` for every verified fact and its source. Anything not listed is not covered.
"""


def main() -> None:
    SKILL.mkdir(parents=True, exist_ok=True); (SKILL / "references").mkdir(exist_ok=True)
    (SKILL / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
    (SKILL / "references" / "facts.md").write_text(facts_md(), encoding="utf-8")
    (ROOT / "shared").mkdir(exist_ok=True)
    (ROOT / "shared" / "facts.json").write_text(facts_json(), encoding="utf-8")
    print("wrote skill, references/facts.md and shared/facts.json")


if __name__ == "__main__":
    main()
