# Limitations

- One prompt, one product workload, 35 scenarios, and one provider route cannot establish a universal model ranking.
- The prompt was tuned around GPT-family behavior; model and prompt effects are confounded.
- Six category subsets are small. A three-scenario robustness slice cannot support broad claims about messy input.
- Repeated trials reduce random noise but do not cure scenario-selection bias.
- Deterministic route scoring misses qualitative differences and can misclassify state-aware no-ops.
- Latency includes provider routing and network behavior, not model inference alone.
- Historical prices and model identifiers can drift.
- The original raw results were not suitable for automatic public release: one processed file is malformed, raw calls are unaudited, and the corpus contains excluded proprietary material.
- The synthetic fixture verifies the public scorer, not the original results.

