"""The MCP server (stdio). Five read-only tools; every answer carries value, source, as-of, status and the education-only note."""
from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from . import service

mcp = FastMCP(
    "canada-planning-facts",
    instructions=(
        "Hand-verified Canadian planning facts with their official sources. Answer general rules with the value, its source "
        "and its date. If a value is pending, say it is not yet published and give the latest published value. If a value is "
        "not in the verified file, say so; never fill the gap from memory. For personal 'should I' questions, give the general "
        "rule and neutral trade-offs, then point to a qualified professional; never recommend. Education only, not advice."
    ),
)


@mcp.tool
def get_fact(id: str) -> dict[str, Any]:
    """One fact by id, for example 'tfsa_annual_limit.2026' or 'oas_start_age'. Returns value, source, as-of date and status."""
    return service.get_fact(id)


@mcp.tool
def get_limit(account: str, year: int | None = None) -> dict[str, Any]:
    """A contribution limit. account: 'tfsa', 'rrsp', 'fhsa_annual' or 'fhsa_lifetime'. year defaults to the current year; a year not yet published answers 'not yet published' with the latest value."""
    return service.get_limit(account, year)


@mcp.tool
def get_brackets(jurisdiction: str, year: int | None = None) -> dict[str, Any]:
    """Income tax brackets for 'federal' or 'ON' (Ontario) in a tax year, as a table of from, to and rate (percent)."""
    return service.get_brackets(jurisdiction, year)


@mcp.tool
def list_pending() -> dict[str, Any]:
    """Every value not yet published (such as next year's limits), each with the latest published value."""
    return service.list_pending()


@mcp.tool
def boc_series(series_id: str) -> dict[str, Any]:
    """Latest observations of a Bank of Canada Valet series (for example 'V39079' or 'FXUSDCAD'), live, with the Bank's attribution."""
    return service.boc_series(series_id)


def main() -> None:
    mcp.run(show_banner=False)


if __name__ == "__main__":
    main()
