# Handoff (2026-11-10)

**State:** `facts.yaml` has 43 entries: 30 confirmed by Mo, 6 pending (2027s), 7 unverified (milestone facts drafted for the
milestones build: TFSA minimum age 18, RRSP maturity age 71, OAS start age 65, OAS deferral stop age 70, CPP standard,
earliest and latest start ages 65, 60, 70). Unverified entries are never served or exported. 42 tests pass.
The five-tool MCP server (`service.py`, `server.py`), the generated Agent Skill and plugin (`plugin/`), `shared/facts.json`
and the README install lines are done. `claude plugin validate` and `agentskills validate` pass. The `uvx --from git+...`
line was tested from GitHub; the `/plugin install` line is validated but not run in an interactive Claude Code.

**Mo next:** verify the 7 new facts against their links, then mark each `confirmed` (verified_by, verified_on) or say "verified".
Create the public repo `planning-lab` (MIT) and turn on push protection. Console key and compliance heads-up before the eval (W2).

**Still to do (W1 low-effort, W2):** the vhs recording (a muted MP4 of the test run and three questions), the eval
(40 prompts written by Mo; promptfoo; two configurations; US$10 cap), the results table and the case study for the site.
After `planning-lab` exists: copy `shared/facts.json` into it and build the milestones page (P7) from it.

**Rules that bite:** only Mo confirms facts; values come only from the official page; no "CFP"; no model names in files;
generated files are never hand-edited (`uv run python scripts/build_skill.py`).
