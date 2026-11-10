"""The facts.yaml schema (SPEC.md §3 and §4, rules 1-7)."""
from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Hosts a source may live on: these domains and their subdomains, plus anything under gc.ca.
ALLOWED_DOMAINS = ("canada.ca", "ontario.ca", "bankofcanada.ca")
ALLOWED_SUFFIXES = (".gc.ca",)


def host_allowed(url: str) -> bool:
    parts = urlparse(url)
    if parts.scheme != "https" or not parts.hostname:
        return False
    host = parts.hostname.lower()
    if any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS):
        return True
    return any(host.endswith(s) for s in ALLOWED_SUFFIXES)


class Status(str, Enum):
    unverified = "unverified"
    confirmed = "confirmed"
    pending = "pending"
    superseded = "superseded"


class Kind(str, Enum):
    yearly = "yearly"
    fixed = "fixed"


class Jurisdiction(str, Enum):
    federal = "federal"
    ON = "ON"


class Unit(str, Enum):
    CAD = "CAD"
    percent = "percent"
    percent_per_month = "percent_per_month"
    factor = "factor"
    date = "date"
    text = "text"
    years = "years"


class Authority(str, Enum):
    statute = "statute"
    cra_position = "cra_position"
    official_publication = "official_publication"
    budget_proposal = "budget_proposal"  # proposed in a federal budget: not law until enacted


class BracketRow(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    from_: Decimal = Field(alias="from", ge=0)
    to: Decimal | None = None
    rate: Decimal = Field(ge=0, le=100)  # percent


class FactorRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    age: int = Field(ge=0, le=120)
    factor: Decimal = Field(ge=0, le=1)


Value = Decimal | date | str | list[BracketRow] | list[FactorRow]

ID_RE = re.compile(r"^[a-z][a-z0-9_]*(\.\d{4})?$")


class Fact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    series: str
    title: str
    kind: Kind
    jurisdiction: Jurisdiction
    tax_year: int | None = None
    value: Value | None = None
    unit: Unit
    source_url: str
    source_quote: str | None = None
    authority: Authority
    as_of: date
    status: Status
    verified_by: str | None = None
    verified_on: date | None = None
    superseded_by: str | None = None
    notes: str | None = None

    @field_validator("source_url")
    @classmethod
    def _source_allowed(cls, v: str) -> str:  # rule 1
        if not host_allowed(v):
            raise ValueError(f"source must be https on an allowlisted government host: {v}")
        return v

    @model_validator(mode="after")
    def _rules(self) -> "Fact":
        if not ID_RE.match(self.id):  # rule 7
            raise ValueError(f"bad id: {self.id}")
        if self.kind is Kind.yearly:  # rule 6
            if self.tax_year is None:
                raise ValueError("yearly entries need tax_year")
            if self.id != f"{self.series}.{self.tax_year}":
                raise ValueError("yearly id must be series.tax_year")
        else:
            if self.tax_year is not None:
                raise ValueError("fixed entries have no tax_year")
            if self.id != self.series:
                raise ValueError("fixed id must equal series")
        s = self.status
        if s is Status.pending:  # rule 2
            if self.value is not None or self.source_quote is not None:
                raise ValueError("pending means value and source_quote are null")
        if s in (Status.confirmed, Status.unverified, Status.superseded):
            if self.value is None or not self.source_quote:
                raise ValueError(f"{s.value} needs a value and a source_quote")
        if s is Status.confirmed:  # rule 3
            if not self.verified_by or self.verified_on is None:
                raise ValueError("confirmed needs verified_by and verified_on")
            if self.verified_on < self.as_of:
                raise ValueError("verified_on must be on or after as_of")
        if s is Status.unverified and self.verified_by:  # rule 4
            raise ValueError("unverified entries have no verified_by")
        if s is Status.superseded and not self.superseded_by:  # rule 5 (target checked in FactsFile)
            raise ValueError("superseded needs superseded_by")
        return self


class FactsFile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    facts: list[Fact]

    @model_validator(mode="after")
    def _file_rules(self) -> "FactsFile":
        ids = [f.id for f in self.facts]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:  # rule 7
            raise ValueError(f"duplicate ids: {sorted(dupes)}")
        known = set(ids)
        for f in self.facts:  # rule 5
            if f.superseded_by and f.superseded_by not in known:
                raise ValueError(f"{f.id} is superseded by unknown id {f.superseded_by}")
        return self
