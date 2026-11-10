"""Three questions to the MCP server, in-process, for the recording. No model is called.

    uv run python scripts/demo.py                # the answers as JSON
    uv run python scripts/demo.py --brief 1      # question 1 only, in short readable lines (the wide video)
    uv run python scripts/demo.py --brief 1 36   # the same, at most 36 characters wide (the phone video)
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


def hang(label: str, value: str, width: int) -> list[str]:
    """The label, then the value wrapped so its later lines line up under its first."""
    lines = textwrap.wrap(value, width - len(label)) or [""]
    return [label + lines[0]] + [" " * len(label) + line for line in lines[1:]]


def brief(q: str, tool: str, args: dict, r: dict, width: int = 52) -> None:
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
    out = textwrap.wrap(f"Q: {q}", width, subsequent_indent="   ")
    call = f"({', '.join(str(v) for v in args.values())})"
    out += [f"   tool: {tool}{call}"] if len(f"   tool: {tool}{call}") <= width else [f"   tool: {tool}", f"         {call}"]
    out += [""]
    for k, v in rows:
        out += hang(f"   {k:<10}", v, width)
    out += [""] + ["   " + line for line in textwrap.wrap(r["note"], width - 3)]
    print("\n".join(out))


async def main() -> None:
    brief_n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--brief" else None
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 52
    async with Client(mcp) as c:
        for n, (q, tool, args) in enumerate(QUESTIONS, 1):
            if brief_n and n != brief_n:
                continue
            r = json.loads((await c.call_tool(tool, args)).content[0].text)
            if brief_n:
                brief(q, tool, args, r, width)
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
