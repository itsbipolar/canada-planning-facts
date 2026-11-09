# Test data is synthetic: values like 1234 are placeholders, not real figures.
import pytest


@pytest.fixture
def base():
    return dict(
        id="tfsa_annual_limit.2026", series="tfsa_annual_limit", title="TFSA annual dollar limit",
        kind="yearly", jurisdiction="federal", tax_year=2026, value="1234", unit="CAD",
        source_url="https://www.canada.ca/en/revenue-agency/example.html",
        source_quote="Example quoted line.", authority="cra_position", as_of="2026-11-06",
        status="confirmed", verified_by="MEC", verified_on="2026-11-07",
    )
