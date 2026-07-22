from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("score", ROOT / "src" / "score.py")
assert SPEC and SPEC.loader
SCORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORE)


class ContractTests(unittest.TestCase):
    def test_original_call_count_is_locked(self) -> None:
        manifest = json.loads((ROOT / "data" / "study_manifest.json").read_text())
        study = manifest["original_study"]
        self.assertEqual(study["scenario_count"], 35)
        self.assertEqual(study["model_count"], 8)
        self.assertEqual(study["trials_per_scenario_model"], 10)
        self.assertEqual(35 * 8 * 10, 2800)
        self.assertEqual(study["api_call_count"], 2800)

    def test_fixture_is_balanced_and_synthetic(self) -> None:
        scenarios = SCORE.read_jsonl(ROOT / "data" / "synthetic_scenarios.jsonl")
        self.assertEqual(len(scenarios), 18)
        self.assertEqual(len({row["id"] for row in scenarios}), 18)
        self.assertTrue(all(row["synthetic"] is True for row in scenarios))
        self.assertEqual(set(Counter(row["category"] for row in scenarios).values()), {3})

    def test_fenced_json_and_example_score(self) -> None:
        fenced = '```json\n{"response_mode":"reason","tools":[],"message":"ok"}\n```'
        self.assertEqual(SCORE.parse_response(fenced)["response_mode"], "reason")
        scenarios = SCORE.read_jsonl(ROOT / "data" / "synthetic_scenarios.jsonl")
        outputs = SCORE.read_jsonl(ROOT / "data" / "example_outputs.jsonl")
        report = SCORE.score(scenarios, outputs)
        self.assertEqual(report["scenario_count"], 18)
        self.assertEqual(report["parse_failures"], 1)
        self.assertEqual(report["tool_matches"], 15)
        self.assertEqual(report["mode_matches"], 16)

    def test_aggregate_table_has_eight_models(self) -> None:
        aggregate_path = ROOT / "data" / "published_aggregate_results.csv"
        with aggregate_path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 8)
        self.assertAlmostEqual(sum(float(row["total_cost_usd"]) for row in rows), 145.83, places=2)
        self.assertEqual(
            hashlib.sha256(aggregate_path.read_bytes()).hexdigest(),
            "986d3f190f91dc4273c758a7dc946c06b4953496d0b5f01d297157b1453d057c",
        )


if __name__ == "__main__":
    unittest.main()
