"""The answers (SPEC.md sections 5 and 6). Fixtures are synthetic; the last tests read the real facts file."""
import asyncio
from datetime import date

from canada_planning_facts import service
from canada_planning_facts.schema import FactsFile

TODAY = date(2026, 11, 10)


def _facts(base, extra=()):
    rows = [dict(base), {**base, "id": "tfsa_annual_limit.2027", "tax_year": 2027, "status": "pending", "value": None, "source_quote": None, "verified_by": None, "verified_on": None}, *extra]
    return FactsFile(facts=rows)


def test_confirmed_value_has_the_whole_envelope(base):
    r = service.get_fact("tfsa_annual_limit.2026", _facts(base), TODAY)
    for k in ("value", "unit", "tax_year", "source_url", "as_of", "status", "note"):
        assert r[k] is not None
    assert r["status"] == "confirmed" and r["value"] == "1234" and "Education only" in r["note"]


def test_pending_says_not_yet_published_and_gives_the_latest(base):
    r = service.get_fact("tfsa_annual_limit.2027", _facts(base), TODAY)
    assert r["value"] is None and r["status"] == "pending"
    assert r["message"] == "Not yet published as of 2026-11-10."
    assert r["latest_published"]["tax_year"] == 2026 and r["latest_published"]["value"] == "1234"


def test_unknown_is_never_guessed(base):
    r = service.get_fact("tfsa_annual_limit.2099", _facts(base), TODAY)
    assert r["value"] is None and r["message"] == "Not in the verified facts file." and "Education only" in r["note"]


def test_unverified_is_never_served(base):
    unv = {**base, "id": "tfsa_annual_limit.2025", "tax_year": 2025, "status": "unverified", "verified_by": None, "verified_on": None}
    r = service.get_fact("tfsa_annual_limit.2025", _facts(base, [unv]), TODAY)
    assert r["value"] is None and r["message"] == "Not in the verified facts file."


def test_get_limit_year_and_default(base):
    f = _facts(base)
    assert service.get_limit("tfsa", 2026, f, TODAY)["value"] == "1234"
    assert service.get_limit("tfsa", None, f, TODAY)["tax_year"] == 2026
    assert service.get_limit("tfsa", 2027, f, TODAY)["status"] == "pending"
    assert "Unknown account" in service.get_limit("savings", 2026, f, TODAY)["message"]


def test_list_pending(base):
    r = service.list_pending(_facts(base), TODAY)
    assert [p["id"] for p in r["pending"]] == ["tfsa_annual_limit.2027"] and r["pending"][0]["latest_published"]["value"] == "1234"


def test_boc_validates_caches_and_attributes():
    calls = []
    fetch = lambda sid: (calls.append(sid), {"observations": [{"d": "2026-11-09", sid: {"v": "1.0"}}], "seriesDetail": {sid: {"label": "x"}}})[1]
    clock = [1000.0]
    service._cache.clear()
    a = service.boc_series("FXTEST", fetch, lambda: clock[0])
    b = service.boc_series("FXTEST", fetch, lambda: clock[0] + 100)
    assert a is b and calls == ["FXTEST"] and "Bank of Canada" in a["attribution"] and "Not affiliated" in a["attribution"]
    service.boc_series("FXTEST", fetch, lambda: clock[0] + 4000)
    assert calls == ["FXTEST", "FXTEST"]
    assert "not a valid" in service.boc_series("../etc/passwd", fetch)["message"]
    assert "could not be read" in service.boc_series("NOPE", lambda s: (_ for _ in ()).throw(RuntimeError("x")))["message"]


def test_real_file_answers():
    assert service.get_fact("oas_deferral_increase")["value"] == "0.6"
    assert service.get_limit("tfsa", 2026)["value"] == "7000"
    r = service.get_limit("tfsa", 2027)
    assert r["status"] == "pending" and r["latest_published"]["tax_year"] == 2026
    assert [row["rate"] for row in service.get_brackets("ON", 2026)["value"]][0] == "5.05"
    assert service.get_limit("fhsa_lifetime")["value"] == "40000"


def test_real_file_never_serves_an_unverified_value():
    from canada_planning_facts.facts import load_facts
    from canada_planning_facts.schema import Status

    for f in load_facts().facts:
        r = service.get_fact(f.id)
        if f.status is Status.confirmed:
            assert r["value"] is not None, f.id
        else:
            assert r["value"] is None, f.id


def test_server_exposes_five_tools_and_answers():
    from fastmcp import Client

    from canada_planning_facts.server import mcp

    async def go():
        async with Client(mcp) as c:
            names = {t.name for t in await c.list_tools()}
            res = await c.call_tool("get_limit", {"account": "tfsa", "year": 2027})
            return names, res.data
    names, data = asyncio.run(go())
    assert names == {"get_fact", "get_limit", "get_brackets", "list_pending", "boc_series"}
    assert data["status"] == "pending" and data["latest_published"]["value"] == "7000"


def test_generated_files_match_a_fresh_build():
    """CI fails if SKILL.md, references/facts.md or shared/facts.json were edited by hand or the facts changed without rebuilding."""
    import importlib.util
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("build_skill", root / "scripts" / "build_skill.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    assert (root / "shared" / "facts.json").read_text(encoding="utf-8") == mod.facts_json()
    assert (root / "plugin/skills/canada-planning-facts/references/facts.md").read_text(encoding="utf-8") == mod.facts_md()
    assert (root / "plugin/skills/canada-planning-facts/SKILL.md").read_text(encoding="utf-8") == mod.SKILL_MD
    assert len(mod.SKILL_MD.splitlines()) < 500


def test_the_built_package_ships_its_facts(tmp_path):
    """A wheel built from this repo must contain facts.yaml, or an installed server cannot answer (found by installing from GitHub)."""
    import subprocess, sys, zipfile
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    subprocess.run(["uv", "build", "--wheel", "-o", str(tmp_path)], cwd=root, check=True, capture_output=True)
    names = zipfile.ZipFile(next(tmp_path.glob("*.whl"))).namelist()
    assert "canada_planning_facts/facts.yaml" in names
