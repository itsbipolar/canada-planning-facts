"""Re-score a results file offline with the current score.py; keeps the scores recorded at run time as score_as_run.

    uv run python eval/rescore.py eval/results/<date>/results.json
"""
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import ROOT, load_facts, score  # noqa: E402

path = Path(sys.argv[1])
data = json.loads(path.read_text())
prompts = {p["id"]: p for p in yaml.safe_load((ROOT / "eval" / "prompts.yaml").read_text())["prompts"]}
facts = load_facts()
for row in data["rows"]:
    row.setdefault("score_as_run", row["score"])
    row["score"] = score(prompts[row["id"]], row["answer"], facts)
data["meta"]["rescored"] = ("Re-scored after the run: two scorer bugs found by reading answers (gaps named as 'couldn't find it in "
                            "my verified facts file' or 'isn't in my verified facts file'; a partial 'I can't give those "
                            "details' inside a full education answer counted as a refusal). score_as_run keeps the original scores.")
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
