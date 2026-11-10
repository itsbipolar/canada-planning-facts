# Canada Planning Facts

**Prototype. AI-assisted. Reference data: verify at the source. Education, not advice.**

Hand-verified Canadian planning figures, each with its official source, tax year, the date it was read and its status, served to AI assistants as a local MCP server and an Agent Skill. A value that is not yet published (next year's limits, for example) comes back as "not yet published", with the latest published value, never a guess. Personal "should I" questions get the general rule and a pointer to a qualified professional, never a recommendation.

**Demo (26 s, muted):** [`docs/demo.mp4`](docs/demo.mp4): the test suite, then three questions sent straight to the
server's tools (a confirmed figure, a 2027 figure not yet published, a figure not in the file). No model is called.
**Eval:** [`eval/RESULTS.md`](eval/RESULTS.md): 40 prompts, with and without these tools. Evaluation output, not advice.

## What it covers
TFSA, RRSP and FHSA limits, CPP and OAS ages and rules, the OAS recovery tax threshold, federal and Ontario tax brackets, RRIF minimum factors, the RRSP contribution deadline, and the creation dates of the main registered plans. [`plugin/skills/canada-planning-facts/references/facts.md`](plugin/skills/canada-planning-facts/references/facts.md) lists every verified fact. Only values a person has checked against the official page are served.

## Install (two lines)
Claude Code, as a plugin (the skill and the server together):

    /plugin marketplace add itsbipolar/canada-planning-facts
    /plugin install canada-planning-facts@canada-planning-facts

Or just the server, from the terminal:

    claude mcp add canada-planning-facts -- uvx --from git+https://github.com/itsbipolar/canada-planning-facts canada-planning-facts

The server runs locally, collects nothing and makes no network calls except `boc_series`, which reads a public Bank of Canada series.

## Tools
`get_fact`, `get_limit`, `get_brackets`, `list_pending`, `boc_series`. Every answer carries the value, unit, tax year, source link, the date it was read, its status and an education-only note.

## How the facts are kept honest
`facts.yaml` is the one source. Each entry has the exact line it was copied from, and only a person can mark it `confirmed`. The tests refuse to serve anything unconfirmed, refuse any source outside `canada.ca`, `ontario.ca`, `bankofcanada.ca` and `gc.ca` sites, and a weekly check fails when a new tax year arrives and a figure has not been refreshed or marked pending.

    uv sync --group dev && uv run pytest

Details: [SPEC.md](SPEC.md). The generated files (`plugin/skills/.../SKILL.md`, `references/facts.md`, `shared/facts.json`) come from `uv run python scripts/build_skill.py`; do not edit them by hand.

Bank of Canada data: Source: Bank of Canada, [terms](https://www.bankofcanada.ca/terms/). Not affiliated with or endorsed by the Bank of Canada.

Education only, not personal financial, tax, legal or investment advice. A personal project, not affiliated with or endorsed by any employer. MIT licence.
