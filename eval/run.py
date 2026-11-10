"""Run the forty prompts in two configurations and write the results.

    uv run --group eval python eval/run.py --model <id> --in-price <US$/M in> --out-price <US$/M out>

The key is read from EVAL_ANTHROPIC_API_KEY (Mo's Console key, set in the environment's settings, never in the repo).
The runner calls https://api.anthropic.com directly and ignores ANTHROPIC_API_KEY and ANTHROPIC_BASE_URL, so the run is
billed to that Console workspace and its cap, never to anything else this machine is signed in to.

Configurations:
  bare   the model with a one-line system prompt and today's date; no tools.
  tools  the same, plus the shipped MCP server: its instructions and its five tools, called in-process.

The model id and prices come from the command line, so no model name is written in this repo's files; it appears only in
the generated results. The run stops before it can spend more than --cap US dollars (default 8, under the US$10 limit).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import ROOT, load_facts, score  # noqa: E402

TODAY = date(2026, 11, 10)
BASE_SYSTEM = (
    "You answer questions about Canadian personal-finance rules for a general audience. "
    "Today's date is {today}."
)
MAX_TOOL_TURNS = 6


class Spend:
    def __init__(self, in_price: float, out_price: float, cap: float):
        self.in_price, self.out_price, self.cap, self.usd = in_price, out_price, cap, 0.0

    def add(self, usage: Any) -> None:
        tokens_in = usage.input_tokens + (usage.cache_creation_input_tokens or 0) * 1.25 + \
            (usage.cache_read_input_tokens or 0) * 0.1
        self.usd += tokens_in * self.in_price / 1e6 + usage.output_tokens * self.out_price / 1e6

    def check(self) -> None:
        if self.usd >= self.cap:
            raise SystemExit(f"Stopped: spend estimate US${self.usd:.2f} reached the cap of US${self.cap:.2f}.")


def text_of(content: list[Any]) -> str:
    return "\n".join(b.text for b in content if b.type == "text").strip()


async def ask(client: Any, model: str, prompt: str, mcp_client: Any | None, tools: list[dict] | None,
              instructions: str | None, spend: Spend) -> dict[str, Any]:
    system = BASE_SYSTEM.format(today=TODAY.isoformat())
    if instructions:
        system += "\n\n" + instructions
    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
    calls: list[dict[str, Any]] = []
    for _ in range(MAX_TOOL_TURNS):
        spend.check()
        kwargs: dict[str, Any] = dict(model=model, max_tokens=8000, system=system, messages=messages,
                                      output_config={"effort": "medium"})
        if tools:
            kwargs["tools"] = tools
        resp = client.messages.create(**kwargs)
        spend.add(resp.usage)
        if resp.stop_reason == "refusal":
            return {"answer": text_of(resp.content), "stop_reason": "refusal", "tool_calls": calls}
        if resp.stop_reason != "tool_use":
            return {"answer": text_of(resp.content), "stop_reason": resp.stop_reason, "tool_calls": calls}
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            try:
                r = await mcp_client.call_tool(block.name, block.input, raise_on_error=False)
                out, err = (r.content[0].text if r.content else ""), bool(r.is_error)
            except Exception as e:  # a bad tool name or argument goes back to the model as an error
                out, err = f"Tool error: {e}", True
            calls.append({"tool": block.name, "input": block.input, "error": err})
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": out, "is_error": err})
        messages.append({"role": "user", "content": results})
    return {"answer": "", "stop_reason": "tool_turn_limit", "tool_calls": calls}


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--in-price", type=float, required=True, help="US$ per million input tokens")
    ap.add_argument("--out-price", type=float, required=True, help="US$ per million output tokens")
    ap.add_argument("--cap", type=float, default=8.0)
    ap.add_argument("--only", nargs="*", help="prompt ids to run (for a smoke test)")
    ap.add_argument("--out", default=str(ROOT / "eval" / "results" / TODAY.isoformat()))
    args = ap.parse_args()

    import anthropic
    from fastmcp import Client

    from canada_planning_facts.server import mcp

    prompts = yaml.safe_load((ROOT / "eval" / "prompts.yaml").read_text())["prompts"]
    if args.only:
        prompts = [p for p in prompts if p["id"] in args.only]
    facts = load_facts()
    import os
    key = os.environ.get("EVAL_ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("EVAL_ANTHROPIC_API_KEY is not set: add the Console key in the environment's settings.")
    client = anthropic.Anthropic(api_key=key, base_url="https://api.anthropic.com")
    spend = Spend(args.in_price, args.out_price, args.cap)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    async with Client(mcp) as mc:
        tools = [{"name": t.name, "description": t.description, "input_schema": t.input_schema}
                 for t in await mc.list_tools()]
        for config in ("bare", "tools"):
            for p in prompts:
                r = await ask(client, args.model, p["prompt"], mc if config == "tools" else None,
                              tools if config == "tools" else None,
                              mcp.instructions if config == "tools" else None, spend)
                row = {"config": config, **{k: p.get(k) for k in ("id", "category", "targets", "prompt")}, **r,
                       "score": score(p, r["answer"], facts)}
                rows.append(row)
                print(f"{config:5} {p['id']} {p['category']:11} pass={row['score'].get('pass')} "
                      f"spend=US${spend.usd:.2f}", flush=True)
    meta = {"model": args.model, "date": TODAY.isoformat(), "effort": "medium", "max_tool_turns": MAX_TOOL_TURNS,
            "configurations": {"bare": "system prompt only, no tools",
                               "tools": "system prompt plus the canada-planning-facts MCP server (instructions and five tools)"},
            "estimated_spend_usd": round(spend.usd, 2), "prompts_written_by": "drafted by Claude Code, reviewed and approved by Mo"}
    (out / "results.json").write_text(json.dumps({"meta": meta, "rows": rows}, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {out / 'results.json'}; estimated spend US${spend.usd:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
