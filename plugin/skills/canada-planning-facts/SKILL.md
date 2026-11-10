---
name: canada-planning-facts
description: >-
  Answers Canadian planning-rule questions (TFSA, RRSP, FHSA limits, CPP and OAS ages and rules, federal and Ontario tax brackets, RRIF minimums) with the value, its official source, tax year and the date it was read. Says "not yet published" for figures that are not out yet and never guesses. Gives general rules only: for personal "should I" questions it explains the rule and the trade-offs and points to a qualified professional. Use for questions about Canadian registered-plan limits, public pension rules or tax brackets.
license: MIT
---

# Canada Planning Facts

Prototype. AI-assisted. Reference data: verify at the source. Education, not advice.

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
