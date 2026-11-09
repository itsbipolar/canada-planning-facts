# canada-planning-facts

A local MCP server and Agent Skill of hand-verified Canadian planning facts. Read SPEC.md first; it wins.
Start each session: read HANDOFF.md and SPEC.md. End each session: a 10-line HANDOFF.md, commit, push.
Python 3.12, uv, FastMCP, pydantic v2, pytest. Run `uv run pytest` before every commit.

## Facts
- facts.yaml is the only source. facts.json, SKILL.md and references/facts.md are generated; never hand-edit them.
- Claude drafts values only by copying them from the official page, with the URL and the exact quoted line,
  status `unverified`. Never a value from memory. Only Mo sets `confirmed` (verified_by, verified_on).
- Sources: https on canada.ca, ontario.ca, bankofcanada.ca (and subdomains) or any host under gc.ca. Nothing else.
- 2027 values stay `pending` with value null until the government publishes them.
- The server serves `confirmed` values only. Unverified or unknown: "Not in the verified facts file."

## Answers
- Every answer carries value, unit, tax_year, source_url, as_of, status and the education-only note.
- General rules only. For "should I" or a person's own numbers: the rule, neutral trade-offs, a redirect to a
  qualified professional. Never a recommendation. Don't refuse ordinary education questions.
- No client data, no employer data, no names of real people's situations.

## Never
- "CFP" in any repo, package, tool or file name; any FP Canada content or marks.
- "Financial Planner", "Financial Advisor" or their variants as anyone's title.
- Model names in files or commits. The eval results table names the model only in its generated output.
- Secrets in the repo. The eval reads the Console key from the environment.

## Labels
README and SKILL.md: "Prototype. AI-assisted. Reference data: verify at the source. Education, not advice."
Bank of Canada data: the Bank's attribution line, and no implied affiliation.
Eval outputs: "Evaluation output, not advice", with model, date and configuration.
