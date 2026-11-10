"""Three questions to the MCP server, in-process, for the README recording. No model is called.

    uv run python scripts/demo.py
"""
import asyncio
import json

from fastmcp import Client

from canada_planning_facts.server import mcp

QUESTIONS = [
    ("What is the 2026 TFSA limit?", "get_limit", {"account": "tfsa", "year": 2026}),
    ("What is the 2027 TFSA limit?", "get_limit", {"account": "tfsa", "year": 2027}),
    ("What is the small business deduction limit?", "get_fact", {"id": "small_business_limit.2026"}),
]
KEEP = ("value", "unit", "tax_year", "status", "message", "source_url", "as_of")


async def main() -> None:
    async with Client(mcp) as c:
        for q, tool, args in QUESTIONS:
            r = json.loads((await c.call_tool(tool, args)).content[0].text)
            out = {k: r[k] for k in KEEP if r.get(k) is not None}
            if r.get("latest_published"):
                lp = r["latest_published"]
                out["latest_published"] = {k: lp[k] for k in ("value", "tax_year", "source_url")}
            out["note"] = r["note"]
            print(f"\n> {q}\n  {tool}({', '.join(f'{k}={v!r}' for k, v in args.items())})")
            print("  " + json.dumps(out, indent=2, ensure_ascii=False).replace("\n", "\n  "))
            await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
