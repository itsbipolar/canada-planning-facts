"""The answers (SPEC.md sections 5 and 6): pure functions over the facts file, so they are easy to test.
Every answer has the same envelope. Only confirmed values are served; pending ones say so and point to the latest
published value; anything else is "Not in the verified facts file" (never a guess)."""
from __future__ import annotations

import re
import time
from datetime import date
from decimal import Decimal
from typing import Any, Callable

from .facts import load_facts
from .schema import Fact, FactsFile, Kind, Status

NOTE = "Education only, not personal financial, tax, legal or investment advice. Verify at the source."
ACCOUNTS = {"tfsa": "tfsa_annual_limit", "rrsp": "rrsp_dollar_limit", "fhsa_annual": "fhsa_annual_base_limit", "fhsa_lifetime": "fhsa_lifetime_limit"}
BRACKETS = {"federal": "federal_brackets", "ON": "ontario_brackets"}


def _plain(v: Any) -> Any:
    if isinstance(v, Decimal):
        return format(v, "f")
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, list):
        return [_plain(x) for x in v]
    if hasattr(v, "model_dump"):
        return {k: _plain(x) for k, x in v.model_dump(by_alias=True, exclude_none=True).items()}
    return v


def _envelope(f: Fact) -> dict[str, Any]:
    return {
        "id": f.id, "title": f.title, "value": _plain(f.value), "unit": f.unit.value, "tax_year": f.tax_year,
        "source_url": f.source_url, "source_quote": f.source_quote, "authority": f.authority.value,
        "as_of": f.as_of.isoformat(), "status": f.status.value, "note": NOTE,
    }


def _latest_confirmed(facts: FactsFile, series: str) -> Fact | None:
    c = [f for f in facts.facts if f.series == series and f.status is Status.confirmed]
    return max(c, key=lambda f: f.tax_year or 0, default=None)


def _unavailable(message: str, **extra: Any) -> dict[str, Any]:
    return {"value": None, "status": "not_verified", "message": message, "note": NOTE, **extra}


def _serve(facts: FactsFile, f: Fact | None, today: date, asked: str) -> dict[str, Any]:
    if f is None:
        return _unavailable("Not in the verified facts file.", id=asked)
    if f.status is Status.confirmed:
        return _envelope(f)
    if f.status is Status.pending:
        latest = _latest_confirmed(facts, f.series)
        return {"id": f.id, "title": f.title, "value": None, "status": "pending", "tax_year": f.tax_year,
                "source_url": f.source_url, "as_of": f.as_of.isoformat(), "message": f"Not yet published as of {today.isoformat()}.",
                "latest_published": _envelope(latest) if latest else None, "note": NOTE}
    if f.status is Status.superseded:
        return _unavailable(f"Superseded by {f.superseded_by}.", id=f.id, superseded_by=f.superseded_by)
    return _unavailable("Not in the verified facts file.", id=asked)  # unverified: never served as a fact


def available_ids(facts: FactsFile) -> dict[str, str]:
    """The ids get_fact can answer (confirmed or pending), with their titles. No values: those come only from get_fact."""
    return {f.id: f.title for f in facts.facts if f.status in (Status.confirmed, Status.pending)}


def get_fact(fact_id: str, facts: FactsFile | None = None, today: date | None = None) -> dict[str, Any]:
    facts = facts or load_facts(); today = today or date.today()
    f = next((x for x in facts.facts if x.id == fact_id), None)
    out = _serve(facts, f, today, fact_id)
    if f is None:  # an unknown id: say so, and list the ids that do exist so a guessed name can be corrected
        out["available_ids"] = available_ids(facts)
    return out


def get_limit(account: str, year: int | None = None, facts: FactsFile | None = None, today: date | None = None) -> dict[str, Any]:
    facts = facts or load_facts(); today = today or date.today()
    series = ACCOUNTS.get(account)
    if series is None:
        return _unavailable(f"Unknown account. Use one of: {', '.join(ACCOUNTS)}.", id=account)
    entries = [f for f in facts.facts if f.series == series]
    if entries and entries[0].kind is Kind.fixed:
        return _serve(facts, entries[0], today, series)
    year = year or today.year
    return _serve(facts, next((f for f in entries if f.tax_year == year), None), today, f"{series}.{year}")


def get_brackets(jurisdiction: str, year: int | None = None, facts: FactsFile | None = None, today: date | None = None) -> dict[str, Any]:
    facts = facts or load_facts(); today = today or date.today()
    series = BRACKETS.get(jurisdiction)
    if series is None:
        return _unavailable("Unknown jurisdiction. Use 'federal' or 'ON'.", id=jurisdiction)
    year = year or today.year
    return _serve(facts, next((f for f in facts.facts if f.series == series and f.tax_year == year), None), today, f"{series}.{year}")


def list_pending(facts: FactsFile | None = None, today: date | None = None) -> dict[str, Any]:
    facts = facts or load_facts(); today = today or date.today()
    return {"as_of": today.isoformat(), "pending": [_serve(facts, f, today, f.id) for f in facts.facts if f.status is Status.pending], "note": NOTE}


# Bank of Canada Valet: live, keyless, read-only, cached for an hour. Fetching is injectable so tests never touch the network.
_SERIES_ID = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")
_cache: dict[str, tuple[float, dict[str, Any]]] = {}
ATTRIBUTION = "Source: Bank of Canada. Terms: https://www.bankofcanada.ca/terms/. Not affiliated with or endorsed by the Bank of Canada."


def _fetch_valet(series_id: str) -> dict[str, Any]:
    import httpx

    r = httpx.get(f"https://www.bankofcanada.ca/valet/observations/{series_id}/json", params={"recent": 5}, timeout=15)
    r.raise_for_status()
    return r.json()


def boc_series(series_id: str, fetch: Callable[[str], dict[str, Any]] = _fetch_valet, now: Callable[[], float] = time.time) -> dict[str, Any]:
    if not _SERIES_ID.match(series_id):
        return _unavailable("That is not a valid Bank of Canada series id.", id=series_id)
    hit = _cache.get(series_id)
    if hit and now() - hit[0] < 3600:
        return hit[1]
    try:
        data = fetch(series_id)
    except Exception:  # network or unknown series: say so, never guess
        return _unavailable("The Bank of Canada series could not be read right now.", id=series_id)
    obs = data.get("observations", [])
    out = {"id": series_id, "observations": obs, "series_detail": data.get("seriesDetail", {}).get(series_id), "status": "live",
           "source_url": f"https://www.bankofcanada.ca/valet/observations/{series_id}/json", "retrieved": date.today().isoformat(),
           "attribution": ATTRIBUTION, "note": NOTE}
    _cache[series_id] = (now(), out)
    return out
