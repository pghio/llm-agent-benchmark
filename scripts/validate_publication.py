#!/usr/bin/env python3
"""Validate counts and reject sensitive or malformed publication content."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "README.md", "METHODS.md", "LIMITATIONS.md", "CORRECTIONS.md", "REPRODUCTION.md",
    "PROVENANCE.md", "AI_USE.md", "SECURITY.md", "LICENSE", "DATA_LICENSE.md", "CITATION.cff",
}
TEXT_SUFFIXES = {".cff", ".csv", ".json", ".jsonl", ".md", ".py", ".toml", ".yml"}
SENSITIVE_PATTERNS = {
    "absolute user path": re.compile(r"(?:/" + r"Users/|/" + r"home/|[A-Za-z]:\\\\Users\\\\)"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "common secret token": re.compile(r"(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})"),
}
PRIVATE_MARKERS = (
    "honeydew_" + "corpus_rollout",
    "frozen-" + "prompt",
    "results-" + "raw",
    "dew_" + "sessions",
    "real " + "user",
)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> int:
    failures: list[str] = []
    files = [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]
    names = {path.relative_to(ROOT).as_posix() for path in files}
    failures.extend(f"missing required file: {name}" for name in sorted(REQUIRED - names))

    for path in files:
        if path.is_symlink():
            failures.append(f"symlink not allowed: {path.relative_to(ROOT)}")
        if path.stat().st_size > 2_000_000:
            failures.append(f"file exceeds 2 MB: {path.relative_to(ROOT)}")
        if path.suffix not in TEXT_SUFFIXES and path.name != "LICENSE":
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{label} in {path.relative_to(ROOT)}")

    for folder in ("data", "src", "tests"):
        for path in (ROOT / folder).rglob("*"):
            if not path.is_file():
                continue
            lowered = path.read_text(encoding="utf-8").lower()
            for marker in PRIVATE_MARKERS:
                if marker in lowered:
                    failures.append(f"private marker {marker!r} in {path.relative_to(ROOT)}")

    manifest = json.loads((ROOT / "data" / "study_manifest.json").read_text())
    study = manifest["original_study"]
    if study["scenario_count"] * study["model_count"] * study["trials_per_scenario_model"] != 2800:
        failures.append("original API-call arithmetic drifted")
    scenarios = read_jsonl(ROOT / "data" / "synthetic_scenarios.jsonl")
    if len(scenarios) != 18 or len({row["id"] for row in scenarios}) != 18:
        failures.append("synthetic scenario count or uniqueness drifted")
    if any(row.get("synthetic") is not True for row in scenarios):
        failures.append("every public scenario must be explicitly synthetic")
    counts = Counter(row["category"] for row in scenarios)
    if len(counts) != 6 or set(counts.values()) != {3}:
        failures.append("synthetic categories must remain six groups of three")
    outputs = read_jsonl(ROOT / "data" / "example_outputs.jsonl")
    if len(outputs) != 18 or any(row.get("synthetic") is not True for row in outputs):
        failures.append("example output contract drifted")
    aggregate_path = ROOT / "data" / "published_aggregate_results.csv"
    with aggregate_path.open(newline="") as handle:
        aggregate = list(csv.DictReader(handle))
    if len(aggregate) != 8:
        failures.append("aggregate model count drifted")
    if round(sum(float(row["total_cost_usd"]) for row in aggregate), 2) != 145.83:
        failures.append("aggregate reported cost drifted")
    if hashlib.sha256(aggregate_path.read_bytes()).hexdigest() != (
        "986d3f190f91dc4273c758a7dc946c06b4953496d0b5f01d297157b1453d057c"
    ):
        failures.append("published aggregate values drifted")

    if failures:
        print("Publication validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Publication validation passed: {len(files)} files, 18 synthetic scenarios, 8 aggregate models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
