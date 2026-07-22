# LLM Agent Benchmark

A sanitized, publication-ready companion to Pete Ghiorse's April 2026 field test of eight language-model configurations on structured agent routing.

The original experiment used one production-shaped prompt and action schema. This repository does **not** publish that prompt, its tool catalog, original scenarios, mock production state, or raw provider responses. It publishes the corrected aggregate record and a new generic fixture that demonstrates the deterministic scoring method.

## Locked original-study counts

| Item | Count |
| --- | ---: |
| Models | 8 |
| Scenarios | 35 |
| Categories | 6 |
| Trials per scenario/model | 10 |
| API calls | 2,800 |
| Temperature | 0.2 |
| Shuffle seed | 42 |
| Reported run cost | $145.83 |

The arithmetic and artifact counts are enforced in CI.

## What this repository is—and is not

This is:

- an auditable record of the corrected public claims;
- a deterministic scorer for tool choice, response mode, and JSON validity;
- a fully synthetic 18-scenario example corpus;
- a template for builders to replace with their own prompt, schema, scenarios, and calls.

This is not:

- a reproduction of the original model ranking;
- a release of the proprietary frozen prompt or action schema;
- a release of production-derived prompts, sessions, or state;
- a release of the malformed result file or raw unaudited calls;
- evidence that one model is universally best.

## Quick start

Python 3.11+ is sufficient; there are no third-party dependencies or network calls.

```bash
python src/score.py \
  --scenarios data/synthetic_scenarios.jsonl \
  --outputs data/example_outputs.jsonl
python -m unittest discover -s tests -v
python scripts/validate_publication.py
```

## What the field test supports

The useful observations were prompt- and provider-specific failure modes: conversational inputs could trigger unwarranted tools, ambiguity remained hard, route labels could hide duplicate awareness, fenced JSON needed tolerant parsing, and observed latency varied materially. The corrected article explicitly retracts a broad “typos are solved” interpretation and does not present the overall ordering as a universal leaderboard.

See `CORRECTIONS.md`, `LIMITATIONS.md`, and `REPRODUCTION.md` before citing a number.

Canonical article: <https://peterghiorse.com/blog/llm-benchmark-stop-defaulting-to-the-frontier>

Code is Apache-2.0. Data and figures are CC BY 4.0; see `DATA_LICENSE.md`.

