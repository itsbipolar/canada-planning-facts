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

**Eval ready to run (Opus, 2026-11-10; Mo: "do this as you see best"):** `eval/prompts.yaml` has 40 prompts AI-drafted by
Claude Code (stated with the results). `eval/score.py` scores deterministically (tested in `tests/test_eval.py`, 51 tests
pass). `eval/run.py` runs bare and with the MCP server in-process, effort medium, stops at an estimated US$8. The session's
own Anthropic route cannot carry Mo's key, so the runner reads `EVAL_ANTHROPIC_API_KEY` and calls api.anthropic.com
directly. **Mo:** add that variable in the "Portfolio build" environment settings. **Then:** run it, write
`eval/RESULTS.md` (model, date, configuration, "Evaluation output, not advice", five annotated failures), label the ten
advice-bait answers (draft labels marked as Claude's), then Mo sends `mo-sample-portfolio/p1-spec/compliance-heads-up.md`.

**2026-11-10, eval run once (branch `claude/quirky-lovelace-wgxra9`):** Mo's approved prompts in `eval/prompts.yaml`
(17 lookup / 3 freshness / 5 not in file / 10 advice / 5 education); est. spend US$3.06. Results are NOT in this public
repo (`eval/results/` is ignored) until the compliance heads-up: a copy is in mo-sample-portfolio
`p1-spec/eval/results-2026-11-10/`. **Fix next:** the tools only take exact ids, and the model guessed wrong ids for RRIF
factors, CPP start adjustments and start ages, then said "not in the file". Consider a `search_facts`/`list_facts` tool
or listing ids in the server instructions; then a re-run. Not yet: RESULTS.md, Mo's advice labels.
**2026-11-10, eval run 2:** after the `available_ids` fix, tools 17/17 lookups, 5/5 not in file, 5/5 education, 2/3
freshness (fresh-03 still projects a 2027 figure when asked for "a rough number": the instructions don't cover
projections yet). Draft RESULTS lives in mo-sample-portfolio until the heads-up; then copy it here as eval/RESULTS.md.
**2026-11-10, eval published (Mo approved, merged to main):** `eval/RESULTS.md`, `eval/advice_labels.yaml` (Claude's labels,
not reviewed by Mo, at his request) and both runs' `results.json`. Run 2: tools 17/17 lookups, 5/5 not in file, 5/5
education, 10/10 advice held (2 borderline); bare crossed the line on 7/10. Open: fresh-03 projects a 2027 figure when
asked for "a rough number" (instructions don't cover projections; fixing it means a new run, ~US$3, cap nearly used).
Not yet: the vhs recording and the site case study.
