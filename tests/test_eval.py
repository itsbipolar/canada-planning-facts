"""The eval's prompts file and its deterministic scoring. Answers here are made up for the test; numbers come from facts.json."""
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "eval"))
from score import expected_patterns, load_facts, score  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = yaml.safe_load((ROOT / "eval" / "prompts.yaml").read_text())["prompts"]
FACTS = load_facts()


def test_forty_prompts_in_the_planned_mix():
    assert len(PROMPTS) == 40
    assert len({p["id"] for p in PROMPTS}) == 40
    assert Counter(p["category"] for p in PROMPTS) == {"lookup": 20, "freshness": 5, "advice_bait": 10, "education": 5}


def test_targets_exist_with_the_right_status():
    for p in PROMPTS:
        if p["category"] == "lookup":
            assert FACTS[p["target"]]["status"] == "confirmed", p["id"]
            expected_patterns(FACTS[p["target"]], p.get("row"))  # a table target must name its row
        elif p["category"] == "freshness":
            assert FACTS[p["target"]]["status"] == "pending", p["id"]


def test_no_prompt_contains_its_answer():
    for p in PROMPTS:
        if p["category"] == "lookup":
            s = score(p, p["prompt"] + " Source: canada.ca", FACTS)
            assert not s["value_correct"], p["id"]


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
