"""Rules 9 and 10 and the real facts.yaml. These fail until the facts are drafted and the loader exists (W1)."""
from canada_planning_facts.facts import load_facts, servable
from canada_planning_facts.schema import Fact


def test_facts_file_loads_and_has_35_to_150_entries():
    facts = load_facts()
    assert 35 <= len(facts.facts) <= 150


def test_every_series_has_a_2027_entry_when_yearly():
    facts = load_facts()
    yearly = {f.series for f in facts.facts if f.kind.value == "yearly"}
    with_2027 = {f.series for f in facts.facts if f.tax_year == 2027}
    assert yearly and yearly <= with_2027


def test_only_confirmed_is_servable(base):
    assert servable(Fact(**base))
    assert not servable(Fact(**{**base, "status": "unverified", "verified_by": None, "verified_on": None}))


def test_par_dividend_rules_are_the_official_lines_word_for_word():
    # SPEC section 2: a Claude-checked value is copied word for word from its official page. The participating policy
    # dividends tool sets these as quotations, so each text value is its own source_quote.
    par = [f for f in load_facts().facts if f.id.startswith("par_") and f.unit.value == "text"]
    assert len(par) >= 10
    for f in par:
        assert f.value == f.source_quote, f.id


def test_every_claude_checked_text_rule_is_the_official_line_word_for_word():
    # SPEC section 2: under Mo's standing OK, Claude may confirm only a value copied word for word from the official
    # page. A text rule in Claude's own words would be a paraphrase, so every Claude-checked text value must be exactly
    # its source_quote (itself checked against the page). Numbers and tables are transcriptions and are not covered.
    checked = [
        f for f in load_facts().facts
        if f.status.value == "confirmed" and f.unit.value == "text" and (f.verified_by or "").startswith("Claude")
    ]
    assert len(checked) >= 15
    for f in checked:
        assert isinstance(f.value, str) and f.value == f.source_quote, f.id
