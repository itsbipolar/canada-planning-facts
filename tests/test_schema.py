"""Rules 1-7 (SPEC.md §4). These test the schema itself, so they pass from W0."""
import pytest
from pydantic import ValidationError

from canada_planning_facts.schema import Fact, FactsFile, host_allowed


@pytest.mark.parametrize("url", [
    "https://www.canada.ca/en/x.html", "https://canada.ca/x", "https://laws-lois.justice.gc.ca/eng/acts/I-3.3/",
    "https://www.ontario.ca/page/x", "https://www.bankofcanada.ca/valet/docs", "https://gazette.gc.ca/x",
])
def test_allowed_hosts(url):
    assert host_allowed(url)


@pytest.mark.parametrize("url", [
    "http://www.canada.ca/x", "https://canada.ca.evil.com/x", "https://notcanada.ca/x", "https://fakegc.ca/x",
    "https://www.wealthsimple.com/x", "https://en.wikipedia.org/wiki/TFSA", "ftp://canada.ca/x", "canada.ca/x",
])
def test_rejected_hosts(url):
    assert not host_allowed(url)


def test_valid_confirmed(base):
    assert Fact(**base).status.value == "confirmed"


def test_bad_source_rejected(base):
    with pytest.raises(ValidationError):
        Fact(**{**base, "source_url": "https://example.com/tfsa"})


def test_pending_means_null(base):
    Fact(**{**base, "id": "tfsa_annual_limit.2027", "tax_year": 2027, "status": "pending", "value": None,
            "source_quote": None, "verified_by": None, "verified_on": None})
    with pytest.raises(ValidationError):
        Fact(**{**base, "id": "tfsa_annual_limit.2027", "tax_year": 2027, "status": "pending",
                "source_quote": None, "verified_by": None, "verified_on": None})


def test_confirmed_needs_verification(base):
    with pytest.raises(ValidationError):
        Fact(**{**base, "verified_by": None})
    with pytest.raises(ValidationError):
        Fact(**{**base, "verified_on": "2026-11-01"})  # before as_of


def test_unverified_has_no_verifier(base):
    Fact(**{**base, "status": "unverified", "verified_by": None, "verified_on": None})
    with pytest.raises(ValidationError):
        Fact(**{**base, "status": "unverified"})


def test_yearly_and_fixed_ids(base):
    with pytest.raises(ValidationError):
        Fact(**{**base, "id": "tfsa_annual_limit.2025"})  # id year differs from tax_year
    Fact(**{**base, "id": "tfsa_created", "series": "tfsa_created", "kind": "fixed", "tax_year": None,
            "value": "2009-01-01", "unit": "date"})
    with pytest.raises(ValidationError):
        Fact(**{**base, "id": "tfsa_created", "series": "tfsa_created", "kind": "fixed"})  # fixed with a tax_year


def test_table_values(base):
    Fact(**{**base, "id": "federal_brackets.2026", "series": "federal_brackets", "unit": "percent",
            "value": [{"from": 0, "to": 100, "rate": 10}, {"from": 100, "rate": 20}]})


def test_duplicates_and_superseded_targets(base):
    with pytest.raises(ValidationError):
        FactsFile(facts=[base, base])
    old = {**base, "id": "tfsa_annual_limit.2025", "tax_year": 2025, "status": "superseded",
           "superseded_by": "tfsa_annual_limit.2099"}
    with pytest.raises(ValidationError):
        FactsFile(facts=[base, old])
