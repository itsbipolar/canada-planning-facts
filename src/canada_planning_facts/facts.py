"""Loading and staleness (SPEC.md section 4, rules 8-10)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from .schema import Fact, FactsFile, Kind, Status

FACTS_PATH = Path(__file__).resolve().parents[2] / "facts.yaml"


def load_facts(path: Path = FACTS_PATH) -> FactsFile:
    """Read facts.yaml and validate it against the schema."""
    return FactsFile(**yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def stale_series(facts: FactsFile, today: date) -> list[str]:
    """Yearly series with no confirmed entry for today's tax year and no pending entry for it (rule 8)."""
    out = []
    for series in sorted({f.series for f in facts.facts if f.kind is Kind.yearly}):
        entries = [f for f in facts.facts if f.series == series]
        confirmed = [f.tax_year for f in entries if f.status is Status.confirmed]
        pending = [f.tax_year for f in entries if f.status is Status.pending]
        current = bool(confirmed) and max(confirmed) >= today.year
        if not (current or today.year in pending):
            out.append(series)
    return out


def old_reads(facts: FactsFile, today: date, max_days: int = 400) -> list[str]:
    """Ids of confirmed entries read at the source more than max_days ago (a warning, not a failure)."""
    return [f.id for f in facts.facts if f.status is Status.confirmed and (today - f.as_of).days > max_days]


def servable(fact: Fact) -> bool:
    """Only confirmed values are served as facts (rule 10)."""
    return fact.status is Status.confirmed
