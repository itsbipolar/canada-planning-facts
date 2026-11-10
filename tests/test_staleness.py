"""Rule 8: staleness (SPEC.md §4). Fails until stale_series and old_reads exist (W1)."""
from datetime import date

from canada_planning_facts.facts import old_reads, stale_series
from canada_planning_facts.schema import FactsFile


def _f(base, year, status="confirmed", **kw):
    d = {**base, "id": f"tfsa_annual_limit.{year}", "tax_year": year, "status": status, **kw}
    if status == "pending":
        d.update(value=None, source_quote=None, verified_by=None, verified_on=None)
    return d


def test_current_year_confirmed_is_not_stale(base):
    ff = FactsFile(facts=[_f(base, 2026)])
    assert stale_series(ff, date(2026, 11, 6)) == []


def test_new_year_without_entry_is_stale(base):
    ff = FactsFile(facts=[_f(base, 2026)])
    assert stale_series(ff, date(2027, 1, 5)) == ["tfsa_annual_limit"]


def test_new_year_with_pending_entry_is_not_stale(base):
    ff = FactsFile(facts=[_f(base, 2026), _f(base, 2027, "pending")])
    assert stale_series(ff, date(2027, 1, 5)) == []


def test_old_reads_warn_after_400_days(base):
    ff = FactsFile(facts=[_f(base, 2026, as_of="2025-01-02", verified_on="2025-01-03")])
    assert old_reads(ff, date(2026, 11, 6)) == ["tfsa_annual_limit.2026"]


def test_the_real_file_is_not_stale_today():
    """Fails in January until the new year's entries are added or marked pending (SPEC.md rule 8). CI runs this weekly."""
    from canada_planning_facts.facts import load_facts

    assert stale_series(load_facts(), date.today()) == []
