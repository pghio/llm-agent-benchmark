# Methods

## Original field test

Eight model configurations were evaluated on 35 scenarios in six task categories. Each model-scenario pair was repeated ten times at temperature 0.2, producing 2,800 calls. Scenario and model order used a seeded shuffle. All models received the same prompt and schema through the same provider surface.

The prompt had been developed around GPT-family behavior, creating an acknowledged home-field advantage. The experiment therefore answered “which model best fits this prompt and workload?” rather than “which model is best in general?”

Scoring separated:

- expected tool selection;
- response mode (`execute`, `clarify`, or `reason`);
- parse and schema validity;
- response consistency across repeated trials;
- category-specific behavior;
- observed latency and cost.

The public aggregate table is a historical snapshot. Prices, latency, provider routing, and model behavior should not be treated as current.

## Public synthetic fixture

The 18 scenarios in `data/synthetic_scenarios.jsonl` were written from scratch for this repository. They use generic workspace tools and invented state. There are three scenarios in each of the six original category shapes: clear intent, ambiguity, non-action, structured output, compound action, and robustness.

`src/score.py`:

1. strips an optional outer Markdown JSON fence;
2. parses each synthetic output;
3. validates a small public response shape;
4. compares tool sets and response mode independently;
5. reports missing, duplicate, parse-failure, tool-match, and mode-match counts.

The scorer deliberately does not call any provider. A publication package should not need a credential merely to validate its claims.

