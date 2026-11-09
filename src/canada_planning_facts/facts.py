"""Loading and staleness (SPEC.md §4, rules 8-10). Built in W1; stubs until then so the tests fail first."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from .schema import Fact, FactsFile

FACTS_PATH = Path(__file__).resolve().parents[2] / "facts.yaml"


def load_facts(path: Path = FACTS_PATH) -> FactsFile:
    """Read facts.yaml and validate it against the schema."""
    raise NotImplementedError("W1")


def stale_series(facts: FactsFile, today: date) -> list[str]:
    """Yearly series whose newest confirmed entry is older than today's tax year with no pending entry for it."""
    raise NotImplementedError("W1")


def old_reads(facts: FactsFile, today: date, max_days: int = 400) -> list[str]:
    """Ids of confirmed entries read at the source more than max_days ago (a warning, not a failure)."""
    raise NotImplementedError("W1")


def servable(fact: Fact) -> bool:
    """Only confirmed values are served as facts (rule 10)."""
    raise NotImplementedError("W1")
