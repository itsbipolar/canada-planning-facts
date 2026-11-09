"""Rules 9 and 10 and the real facts.yaml. These fail until the facts are drafted and the loader exists (W1)."""
from canada_planning_facts.facts import load_facts, servable
from canada_planning_facts.schema import Fact


def test_facts_file_loads_and_has_35_to_45_entries():
    facts = load_facts()
    assert 35 <= len(facts.facts) <= 45


def test_every_series_has_a_2027_entry_when_yearly():
    facts = load_facts()
    yearly = {f.series for f in facts.facts if f.kind.value == "yearly"}
    with_2027 = {f.series for f in facts.facts if f.tax_year == 2027}
    assert yearly and yearly <= with_2027


def test_only_confirmed_is_servable(base):
    assert servable(Fact(**base))
    assert not servable(Fact(**{**base, "status": "unverified", "verified_by": None, "verified_on": None}))
