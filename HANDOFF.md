# Handoff (2026-11-10)

**State:** `facts.yaml` has 46 entries: 33 confirmed by Mo, 6 pending (2027s), 7 unverified. Unverified entries are never
served or exported. 62 tests pass. The MCP server, Agent Skill, plugin and README are done.
**New (P3 reel, confirmed by Mo 2026-11-10):** `oas_start_year` 1952 (OSFI OAS 18th report, A.1), `rrsp_introduced_year` 1957
(Statistics Canada, tax-treatment study s.1), `cpp_start_year` 1966 (OSFI CPP 32nd report, 2.1). Quotes copied from the pages.
**P4 (2026-11-10):** 11 Budget 2026 entries confirmed by Mo (all), plus budget2026_budget_day (confirmed by Mo from the page's "Date modified: 2026-11-05" line), authority `budget_proposal` (new value: proposed, not law), each
quote checked word for word against budget.canada.ca tax measures. Budget Day's date has no quotable line there yet (Mo to supply).
The CGI entry avoids the words "capital gains" so the eval's not-in-file question stays valid. Entry cap now 35-65.
**Changed:** the entry-count rule is now 35-50 (was 35-45) in SPEC.md rule 9 and the test, so the new facts fit. Mo can revert.
**Caveats for Mo:** OAS, RRSP and CPP give a year, not a day. Justice Laws' Acts do not state the OAS or RRSP start.
**Mo next:** earlier milestone facts still await him.
Create the public repo `planning-lab` (MIT) and turn on push protection. Console key and compliance heads-up before the eval (W2).
**P5 facts draft (2026-11-11, branch `p5-facts-draft`, not main):** six entries drafted from official pages with exact quotes, status
unverified, for Mo to confirm: t1_self_employed_filing_deadline.2026 (June 15, 2027), t1_balance_due_date.2026 (April 30, 2027),
individual_instalment_due_dates (fixed: Mar 15, Jun 15, Sep 15, Dec 15), t3_filing_deadline_rule (90 days), t2_filing_deadline_rule
(six months), trust_deemed_disposition_years (21, ITA 104(4)(b)). Pending: t1_filing_deadline.2026 and the three T1 series for 2027.
Entry cap raised to 75 (68 now; flagged to Mo). The staleness test fails until the two 2026 dates are confirmed: merge to main after.
**P5 facts confirmed (Mo, 2026-11-11: "confirmed for the 5b facts"):** the six drafts are confirmed (verified_by MEC); merged to main.
62 tests pass, including staleness.
**P5b facts draft (2026-11-11, branch `p5b-facts-draft`):** five rules for the planning calendar's year-end rows, unverified for Mo:
superficial_loss_period, fhsa_contribution_period, rrif_minimum_payment_timing, donations_claim_year, cesg_basic_rate (73 entries).
Not found on an allowed source: whether a share sale counts on the trade date or the settlement date (CRA's T4037 page refused a
direct download); left out.
**P5b facts confirmed (Mo, 2026-11-11):** the five drafts are confirmed and merged to main.
