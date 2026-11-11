# SPEC: Canada Planning Facts (P1)

*Written 2026-11-06 in the W0 P1 SPEC session. Repo: `canada-planning-facts`, public from the first commit, MIT. Status badge: prototype. This file wins over every skill.*

## 1. What it is
A local MCP server and an installable Agent Skill that answer Canadian planning-rule questions with the value, its source, its tax year, the date it was read and its status. Values not yet published (2027) come back as "not yet published as of <date>", never a guess. Personal "should I" questions get the general rule and a redirect, never a recommendation. A 40-prompt eval measures all three behaviours, with and without the tools.

**Readers:** product and AI leads at Canadian WealthTech and planning-software firms; AI-transformation and compliance leads at wealth managers; heads of planning trying AI tools for associates.

## 2. Decisions this SPEC rests on
| Item | Decision | Who, when |
|---|---|---|
| Facts entry | Claude drafts each value from its official page with the URL and the exact quoted line, marked `unverified`. Mo checks each against the page and sets it `confirmed` with his initials and date. Only confirmed values are served | Mo, 2026-11-06 |
| Repo | Public from day one. Unverified drafts are visible in history, which is acceptable because they are labelled and never served | Mo, 2026-11-06 |
| Eval | Anthropic Console with a hard prepaid cap of US$10 (expected US$1–3) | Mo, 2026-11-06 |
| Firm | A short heads-up to compliance before the eval is published (W2). Not an approval | Mo, 2026-11-06 |
| Scope | Federal and Ontario; tax years 2025 and 2026 confirmed, 2027 pending | project plan |
| Language | Python 3.12, FastMCP, pydantic v2, pytest, managed with uv | project plan |

## 3. The facts file
`facts.yaml` is the one source. Everything else is generated from it: `shared/facts.json` (for `planning-lab`), `skill/SKILL.md` and `skill/references/facts.md`.

**About 40 entries (35–75; raised for P5's dated rules, 2026-11-11), in these series:**
- Accounts: TFSA annual limit; RRSP dollar maximum; FHSA annual and lifetime limits; the RRSP contribution deadline.
- CPP: year's maximum pensionable earnings (YMPE); the second ceiling (YAMPE); the start-age adjustments (reduction per month before 65, increase per month after 65).
- OAS: the deferral increase per month; the recovery-tax threshold.
- Brackets: federal and Ontario, as tables.
- RRIF: the minimum withdrawal factors, as a table by age.
- Dates (no tax year; `kind: fixed`): the creation of OAS, the RRSP, CPP, the TFSA and the FHSA (used by P3).

The exact list is fixed when the draft is written; each series has entries for 2025, 2026 and a 2027 `pending` entry where the figure is indexed yearly.

**Each entry** (schema: `src/canada_planning_facts/schema.py`):
| Field | Meaning |
|---|---|
| `id` | `series.year` for yearly figures (`tfsa_annual_limit.2026`), `series` for fixed ones |
| `series`, `title` | the figure's family and its plain name |
| `kind` | `yearly` or `fixed` |
| `jurisdiction` | `federal` or `ON` |
| `tax_year` | the year the value applies to (null for `fixed`) |
| `value`, `unit` | a number, a date, a short text, or a table (rows of `{from, to?, rate}` for brackets, `{age, factor}` for RRIF); unit is one of `CAD`, `percent`, `percent_per_month`, `factor`, `date`, `text` |
| `source_url` | https, on an allowlisted government host (§4) |
| `source_quote` | the exact line on the page that holds the value |
| `authority` | `statute`, `cra_position`, `official_publication`, `budget_proposal` (proposed in a federal budget; not law until enacted) |
| `as_of` | the date the value was read at the source |
| `status` | `unverified`, `confirmed`, `pending` or `superseded` |
| `verified_by`, `verified_on` | Mo's initials and the date he checked it; required for `confirmed` |
| `superseded_by` | the id that replaces it; required for `superseded` |

## 4. Rules (each one is a test)
1. Every `source_url` is https, and its host is `canada.ca`, `ontario.ca` or `bankofcanada.ca`, any subdomain of those, or any host under `gc.ca` (which covers Justice Laws and the Canada Gazette). No other host.
2. `pending` means `value` is null and `source_quote` is null.
3. `confirmed` means a value, a source quote, `verified_by` and `verified_on` are all present, and `verified_on` is on or after `as_of`.
4. `unverified` means a value and quote, and no `verified_by`.
5. `superseded` names an existing `superseded_by`.
6. `yearly` entries have a `tax_year`; `fixed` entries don't.
7. Ids are unique and match `series.year` or `series`.
8. **Staleness:** for every yearly series, the newest `confirmed` entry is for the current tax year (the calendar year today), or there is a `pending` entry for it. Otherwise the series is stale and CI fails. Any confirmed entry read more than 400 days ago is reported as a warning.
9. The file has 35–75 entries.
10. The server never returns an `unverified` value as a fact (it answers "not yet verified").

## 5. Tools (FastMCP, stdio)
| Tool | Input | Returns |
|---|---|---|
| `get_fact` | `id` | the entry |
| `get_limit` | `account` (`tfsa`, `rrsp`, `fhsa_annual`, `fhsa_lifetime`), `year` | the entry for that account and year |
| `get_brackets` | `jurisdiction` (`federal`, `ON`), `year` | the bracket table |
| `list_pending` | none | every pending entry, with its series' latest confirmed value |
| `boc_series` | a Bank of Canada Valet series id | the latest observations, live, with the Bank's attribution line; cached for one hour; read-only, no key |

**Every answer has the same envelope:** `value`, `unit`, `tax_year`, `source_url`, `as_of`, `status`, and a `note`: "Education only, not personal financial, tax, legal or investment advice. Verify at the source."
- **Pending:** `value: null`, `message: "Not yet published as of <today>."`, and `latest_published` with the newest confirmed entry and its source.
- **Unverified or unknown:** `value: null`, `message: "Not in the verified facts file."` No guess, no fallback to the model's memory.

## 6. The advice line
The tool descriptions and SKILL.md tell the model: answer general rules with their source; for "should I", "is it better for me" or anything about a person's own numbers, give the general rule, the trade-offs in a neutral list, and a redirect ("For your situation, talk to a qualified professional who knows your full picture."), never a recommendation. Ordinary education questions ("how does the OAS clawback work?") are answered, not refused. Based on CSA/CIRO Staff Notice 31-369: a disclaimer doesn't cure advice, and the builder is responsible for what the AI says.

## 7. The skill and the plugin
- `skill/SKILL.md` (under 500 lines) and `skill/references/facts.md` are generated from `facts.yaml` by `scripts/build_skill.py`; CI fails if they differ from a fresh build.
- `.claude-plugin/marketplace.json` makes the repo a one-plugin marketplace.
- `skills-ref validate` and `claude plugin validate` pass.
- README: two install lines (`claude mcp add …` and `uvx --from git+https://github.com/<owner>/canada-planning-facts …`), and the labels "Prototype. AI-assisted. Reference data: verify at the source. Education, not advice."

## 8. The eval (W2)
- **40 prompts, drafted by Claude Code and approved by Mo (2026-11-10):** 17 fact lookups, 3 freshness questions (2027 values), 5 "not in the file" questions (figures outside `facts.yaml`, testing §5's "no fallback to the model's memory"), 10 advice-bait prompts, 5 general-education questions that must not be refused. *Changed 2026-11-10 from 20/5/10/5: five lookups became "not in the file" prompts, and two freshness prompts became lookups because the 2027 YMPE, YAMPE and RRSP limit were published and confirmed before the run.*
- **Two configurations:** the bare model, and the model with the facts tools. One run each, through promptfoo with a Python provider, on the Console under the US$10 cap.
- **Assertions are deterministic:** the number matches `facts.json`; a government source is cited; no banned title appears; pending questions get "not yet published"; "not in the file" questions name the gap and give no dollar figure from memory. Mo hand-labels the 10 advice-bait outputs (crossed the line / held the line / over-refused).
- **Published as:** a results table stating the model, the date and the configuration, plus 5 annotated failures, labelled "Evaluation output, not advice". No vendor verdicts.
- **Before publishing:** Mo sends the short heads-up to compliance.

## 9. Repo layout
```
canada-planning-facts/
  SPEC.md  CLAUDE.md  README.md  LICENSE  pyproject.toml
  facts.yaml
  src/canada_planning_facts/  schema.py  facts.py (load, stale)  server.py (W1)
  scripts/  build_skill.py  export_json.py  (W1)
  skill/  SKILL.md  references/facts.md  (generated, W1)
  .claude-plugin/marketplace.json  (W1)
  eval/  promptfooconfig.yaml  prompts.yaml  (W2)
  tests/  test_schema.py  test_facts_file.py  test_staleness.py
```

## 10. Done when
- `facts.yaml` has 35–75 entries; CI is green on the schema, pending and staleness tests.
- In a clean Claude Code session the README's two install lines work: a 2027 question returns "not yet published as of <date>" with the latest published value and its source; "Should I take CPP at 60?" gets the general rules and a redirect.
- `skills-ref validate` and `claude plugin validate` pass; SKILL.md is under 500 lines and generated from the YAML.
- The eval has run once in both configurations; the results table states model, date and configuration; the 10 advice-bait outputs are hand-labelled; Console spend is at or under US$10.
- The vhs recording is under 25 MiB; the README carries the prototype, education and AI-assisted labels; "CFP" appears in no name.
- Every served value is `confirmed` by Mo, and the staleness test runs in CI weekly, so 2027 shows up as stale or pending in January without anyone remembering.

## 11. Sessions
| When | Model | Work |
|---|---|---|
| W0 (this session) | Opus | SPEC, CLAUDE.md, schema, failing tests |
| W0–W1 | Sonnet | The facts draft (needs network access to canada.ca, ontario.ca, Justice Laws and bankofcanada.ca; this environment blocks them today). Mo verifies |
| W1 | Sonnet | `facts.py`, the server and its tools until tests pass; `facts.json` export; README install lines |
| W1 | Sonnet, low effort | The generated skill, the plugin files, both validators, the vhs recording |
| W2 | Sonnet | The eval run, the results table, the case study for the site |

## 12. Still open
| Item | Owner | Needed by |
|---|---|---|
| Create the public repo `canada-planning-facts` | Mo | W1 |
| Network access for the facts draft (the four government hosts above) | Mo approves an environment change when the draft session asks | facts draft session |
| Verify each drafted value against its page | Mo | end of W1 |
| Console account with the US$10 cap | Mo | W2 |
| Heads-up to compliance | Mo | before the eval is published (W2) |
| The 40 eval prompts | Mo | W2 |
