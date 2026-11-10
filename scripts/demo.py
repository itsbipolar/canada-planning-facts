"""Three questions to the MCP server, in-process, for the recording. No model is called.

    uv run python scripts/demo.py            # the answers as JSON
    uv run python scripts/demo.py --brief 1  # question 1 only, in short readable lines (for the video)
"""
import asyncio
import json
import sys
import textwrap
from urllib.parse import urlparse

from fastmcp import Client

from canada_planning_facts.server import mcp

QUESTIONS = [
    ("What is the 2026 TFSA limit?", "get_limit", {"account": "tfsa", "year": 2026}),
    ("What is the 2027 TFSA limit?", "get_limit", {"account": "tfsa", "year": 2027}),
    ("What is the small business deduction limit?", "get_fact", {"id": "small_business_limit.2026"}),
]
KEEP = ("value", "unit", "tax_year", "status", "message", "source_url", "as_of")


def money(v: str, unit: str) -> str:
    return f"${int(v):,}" if unit == "CAD" else f"{v} {unit}"


def brief(q: str, tool: str, args: dict, r: dict) -> None:
    rows = []
    if r.get("value") is not None:
        rows.append(("value", money(r["value"], r["unit"])))
    if r.get("tax_year"):
        rows.append(("tax year", str(r["tax_year"])))
    rows.append(("status", r["status"]))
    if r.get("message"):
        rows.append(("answer", r["message"]))
    if r.get("latest_published"):
        lp = r["latest_published"]
        rows.append(("latest", f"{money(lp['value'], lp['unit'])} for {lp['tax_year']}"))
    if r.get("source_url"):
        rows.append(("source", urlparse(r["source_url"]).netloc.removeprefix("www.")))
    if r.get("as_of"):
        rows.append(("read on", r["as_of"]))
    print(f"Q: {q}\n   tool: {tool}({', '.join(str(v) for v in args.values())})\n")
    for k, v in rows:
        print(f"   {k:<10}{v}")
    print()
    for line in textwrap.wrap(r["note"], 52):
        print(f"   {line}")


async def main() -> None:
    only = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--brief" else None
    async with Client(mcp) as c:
        for n, (q, tool, args) in enumerate(QUESTIONS, 1):
            if only and n != only:
                continue
            r = json.loads((await c.call_tool(tool, args)).content[0].text)
            if only:
                brief(q, tool, args, r)
                continue
            out = {k: r[k] for k in KEEP if r.get(k) is not None}
            if r.get("latest_published"):
                lp = r["latest_published"]
                out["latest_published"] = {k: lp[k] for k in ("value", "tax_year", "source_url")}
            out["note"] = r["note"]
            print(f"\n> {q}\n  {tool}({', '.join(f'{k}={v!r}' for k, v in args.items())})")
            print("  " + json.dumps(out, indent=2, ensure_ascii=False).replace("\n", "\n  "))


if __name__ == "__main__":
    asyncio.run(main())
