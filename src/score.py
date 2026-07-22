#!/usr/bin/env python3
"""Offline scorer for the sanitized structured-agent fixture."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

MODES = {"execute", "clarify", "reason"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain an object")
        rows.append(value)
    return rows


def strip_outer_fence(raw: str) -> str:
    match = re.fullmatch(r"\s*```(?:json)?\s*\n?([\s\S]*?)\n?\s*```\s*", raw)
    return match.group(1).strip() if match else raw.strip()


def parse_response(raw: str) -> dict[str, Any]:
    value = json.loads(strip_outer_fence(raw))
    if not isinstance(value, dict):
        raise ValueError("response must be a JSON object")
    if value.get("response_mode") not in MODES:
        raise ValueError("response_mode is invalid")
    tools = value.get("tools")
    if not isinstance(tools, list) or any(not isinstance(item, str) for item in tools):
        raise ValueError("tools must be a string array")
    if not isinstance(value.get("message"), str) or not value["message"].strip():
        raise ValueError("message must be a non-empty string")
    return value


def score(scenarios: list[dict[str, Any]], outputs: list[dict[str, Any]]) -> dict[str, Any]:
    expected = {row["id"]: row for row in scenarios}
    seen: set[str] = set()
    parse_failures = 0
    duplicates = 0
    tool_matches = 0
    mode_matches = 0

    for row in outputs:
        scenario_id = row["scenario_id"]
        if scenario_id not in expected:
            raise ValueError(f"unknown scenario {scenario_id!r}")
        if scenario_id in seen:
            duplicates += 1
            continue
        seen.add(scenario_id)
        try:
            parsed = parse_response(row["raw"])
        except (json.JSONDecodeError, ValueError):
            parse_failures += 1
            continue
        scenario = expected[scenario_id]
        tool_matches += int(set(parsed["tools"]) == set(scenario["expected_tools"]))
        mode_matches += int(parsed["response_mode"] == scenario["expected_mode"])

    denominator = len(expected)
    return {
        "scenario_count": denominator,
        "output_count": len(outputs),
        "missing": denominator - len(seen),
        "duplicates": duplicates,
        "parse_failures": parse_failures,
        "tool_matches": tool_matches,
        "mode_matches": mode_matches,
        "tool_accuracy": tool_matches / denominator,
        "mode_accuracy": mode_matches / denominator,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", required=True, type=Path)
    parser.add_argument("--outputs", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(score(read_jsonl(args.scenarios), read_jsonl(args.outputs)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

