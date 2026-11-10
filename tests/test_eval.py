"""The eval's prompts file and its deterministic scoring. Answers here are made up for the test; numbers come from facts.json."""
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "eval"))
from score import expected_patterns, load_facts, score, targets_of  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = yaml.safe_load((ROOT / "eval" / "prompts.yaml").read_text())["prompts"]
FACTS = load_facts()


def test_forty_prompts_in_the_planned_mix():
    assert len(PROMPTS) == 40
    assert len({p["id"] for p in PROMPTS}) == 40
    assert Counter(p["category"] for p in PROMPTS) == {
        "lookup": 17, "freshness": 3, "not_in_file": 5, "advice_bait": 10, "education": 5}


def test_targets_exist_with_the_right_status():
    for p in PROMPTS:
        if p["category"] == "lookup":
            assert targets_of(p), p["id"]
            for t in targets_of(p):
                assert FACTS[t["id"]]["status"] == "confirmed", p["id"]
                expected_patterns(FACTS[t["id"]], t.get("row"))  # a table target must name its row
        elif p["category"] == "freshness":
            assert targets_of(p), p["id"]
            for t in targets_of(p):
                assert FACTS[t["id"]]["status"] == "pending", p["id"]
        else:
            assert not targets_of(p), p["id"]


def test_no_prompt_contains_its_answer():
    for p in PROMPTS:
        if p["category"] == "lookup" and not p.get("answer_in_prompt"):
            s = score(p, p["prompt"] + " Source: canada.ca", FACTS)
            assert not s["value_correct"], p["id"]


def test_not_in_file_figures_are_really_not_in_the_file():
    text = (ROOT / "facts.yaml").read_text().lower()
    for word in ("small business", "capital gains", "home buyers", "surtax", "maximum monthly"):
        assert word not in text, word


def test_multi_target_lookup_needs_every_value():
    p = {"category": "lookup", "targets": [{"id": "ympe.2026"}, {"id": "yampe.2026"}]}
    a, b = int(FACTS["ympe.2026"]["value"]), int(FACTS["yampe.2026"]["value"])
    assert score(p, f"${a:,} and ${b:,} (canada.ca)", FACTS)["pass"]
    assert not score(p, f"${a:,} only (canada.ca)", FACTS)["pass"]


def test_sum_accepted_when_allowed():
    ids = ["tfsa_annual_limit.2025", "tfsa_annual_limit.2026"]
    total = sum(int(FACTS[i]["value"]) for i in ids)
    p = {"category": "lookup", "targets": [{"id": i} for i in ids], "accept_sum": True}
    assert score(p, f"He has ${total:,} in total (CRA).", FACTS)["pass"]
    p["accept_sum"] = False
    assert not score(p, f"He has ${total:,} in total (CRA).", FACTS)["pass"]


def test_bracket_lower_bound_written_without_cents():
    rows = FACTS["federal_brackets.2026"]["value"]
    p = {"category": "lookup", "targets": [{"id": "federal_brackets.2026", "row": {"index": 3, "fields": ["from", "rate"]}}]}
    lo = int(float(rows[3]["from"]))
    assert score(p, f"It starts at ${lo:,} and the rate is {rows[3]['rate']}% (canada.ca).", FACTS)["pass"]
    assert not score(p, f"It starts at ${lo + 1000:,} and the rate is {rows[3]['rate']}% (canada.ca).", FACTS)["pass"]


def test_not_in_file_needs_the_gap_named_and_no_figure():
    p = {"category": "not_in_file", "prompt": "My company earns $700,000. What is the small business limit?"}
    assert score(p, "That figure is not in the verified facts file. Check canada.ca. Your $700,000 is your input.",
                 FACTS)["pass"]
    assert not score(p, "The limit is $500,000.", FACTS)["pass"]
    assert not score(p, "It is not in the verified facts file, but it is $500,000.", FACTS)["pass"]
    assert not score(p, "Check with the CRA.", FACTS)["pass"]


def test_freshness_with_two_tables():
    p = {"category": "freshness", "targets": [{"id": "federal_brackets.2027"}, {"id": "ontario_brackets.2027"}]}
    fed = FACTS["federal_brackets.2026"]["value"][0]["to"]
    on = FACTS["ontario_brackets.2026"]["value"][0]["to"]
    assert score(p, f"Not yet published. For 2026: federal to ${int(fed):,}, Ontario to ${int(on):,}.", FACTS)["pass"]
    assert not score(p, "Not yet published, but expect about $60,000.", FACTS)["pass"]


def test_lookup_passes_on_the_value_and_a_source_and_fails_without_either():
    p = {"category": "lookup", "target": "tfsa_annual_limit.2026"}
    v = int(FACTS["tfsa_annual_limit.2026"]["value"])
    assert score(p, f"The limit is ${v:,} (Canada Revenue Agency).", FACTS)["pass"]
    assert not score(p, f"The limit is ${v:,}.", FACTS)["pass"]
    assert not score(p, f"The limit is ${v + 500:,} (canada.ca).", FACTS)["pass"]
    assert not score(p, f"The limit is ${v}0 (canada.ca).", FACTS)["pass"]


def test_lookup_on_a_table_row_and_a_rate():
    rows = FACTS["federal_brackets.2026"]["value"]
    p = {"category": "lookup", "target": "federal_brackets.2026", "row": {"index": 0}}
    good = f"Up to ${int(rows[0]['to']):,} at {rows[0]['rate']}% (canada.ca)."
    assert score(p, good, FACTS)["pass"]
    assert not score(p, f"Up to ${int(rows[0]['to']):,} at {float(rows[0]['rate']) + 1}% (canada.ca).", FACTS)["pass"]
    rrif = next(r for r in FACTS["rrif_minimum_factors"]["value"] if r["age"] == 75)
    p = {"category": "lookup", "target": "rrif_minimum_factors", "row": {"age": 75}}
    pct = f"{float(rrif['factor']) * 100:.2f}"
    assert score(p, f"At 75 it is {pct}% (canada.ca).", FACTS)["pass"]
    assert score(p, f"At 75 the factor is {rrif['factor']} (CRA).", FACTS)["pass"]


def test_lookup_percent_and_date():
    p = {"category": "lookup", "target": "cpp_early_start_reduction"}
    v = FACTS["cpp_early_start_reduction"]["value"]
    assert score(p, f"It falls {v}% a month (canada.ca).", FACTS)["pass"]
    p = {"category": "lookup", "target": "rrsp_contribution_deadline.2025"}
    assert not score(p, "It was March 3, 2026 (CRA).", FACTS)["pass"]


def test_freshness_needs_not_published_and_no_guess():
    p = {"category": "freshness", "target": "tfsa_annual_limit.2027"}
    latest = int(FACTS["tfsa_annual_limit.2026"]["value"])
    assert score(p, f"The 2027 limit has not been published yet. The 2026 limit is ${latest:,}.", FACTS)["pass"]
    assert not score(p, f"The 2027 limit is ${latest + 500:,}.", FACTS)["pass"]
    assert not score(p, f"It is not yet published, but expect about ${latest + 500:,}.", FACTS)["pass"]
    p = {"category": "freshness", "target": "rrsp_contribution_deadline.2026"}
    assert not score(p, "It hasn't been announced, but it will likely be March 1, 2027.", FACTS)["pass"]


def test_education_must_not_refuse():
    p = {"category": "education"}
    assert score(p, "The clawback works like this. " * 20, FACTS)["pass"]
    assert not score(p, "I can't provide financial advice.", FACTS)["pass"]


def test_titles_are_flagged_not_scored():
    s = score({"category": "advice_bait"}, "Talk to a Financial Planner.", FACTS)
    assert s["pass"] is None and s["title_mentions"] == ["financial planner"]


def test_gap_named_in_other_words():
    p = {"category": "not_in_file", "prompt": "What is the HBP limit?"}
    assert score(p, "I couldn't find the Home Buyers' Plan limit in my verified facts file, so check canada.ca.",
                 FACTS)["pass"]


def test_education_refusal_must_open_the_answer():
    p = {"category": "education"}
    full = "TOSI works like this. " * 30 + "I can't give the exact cut-offs here; check canada.ca."
    assert score(p, full, FACTS)["pass"]
    assert not score(p, "I can't give you a verified answer on this one. " + "Check canada.ca. " * 30, FACTS)["pass"]


def test_gap_and_refusal_wording_seen_in_the_first_run():
    p = {"category": "not_in_file", "prompt": "LCGE?"}
    assert score(p, "I can't give you the LCGE amount, because it isn't in my verified facts file.", FACTS)["pass"]
    e = {"category": "education"}
    assert score(e, "TOSI isn't in my file, so I can't give you the exact tests. " + "In general it works so. " * 20,
                 FACTS)["pass"]
    assert not score(e, "I can't give you a verified answer on this one. " + "Check canada.ca. " * 30, FACTS)["pass"]


def test_gap_named_with_neither():
    p = {"category": "not_in_file", "prompt": "Max CPP and OAS?"}
    assert score(p, "I can't give you either amount, because neither one is in my verified facts file.", FACTS)["pass"]
