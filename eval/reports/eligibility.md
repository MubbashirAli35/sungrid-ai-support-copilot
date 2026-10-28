# Eligibility path results
Generated 2026-10-28 by `python -m eval.run_eval eligibility`. 8 cases (4 from the eval set, 4 extra probes) x 3 runs. q-cases go through the classifier first; probes go straight to the eligibility path.

- Routed to the eligibility path: 24/24
- Extracted parameters exactly right (missing fields null): 24/24
- Gate respected (correct outcome, no figure unless the service said eligible, tool not called when info is missing): 24/24
- Cost: $0.0049 for 36 calls

| id | expected outcome | routed | params exact | gate respected | outcomes seen |
|---|---|---|---|---|---|
| q15 | eligible | 3/3 | 3/3 | 3/3 | eligible |
| q16 | ineligible | 3/3 | 3/3 | 3/3 | ineligible |
| q17 | ineligible | 3/3 | 3/3 | 3/3 | ineligible |
| q18 | needs_clarification | 3/3 | 3/3 | 3/3 | needs_info |
| p1 | needs_clarification | 3/3 | 3/3 | 3/3 | needs_info |
| p2 | needs_clarification | 3/3 | 3/3 | 3/3 | needs_info |
| p3 | needs_clarification | 3/3 | 3/3 | 3/3 | needs_info |
| p4 | ineligible | 3/3 | 3/3 | 3/3 | ineligible |

Caveats: 8 cases. p1-p4 were written by the same author as the extraction prompt, so they are not independent. The deterministic gate (validation, templates, fail-closed) is covered by tests/test_eligibility_gate.py, which needs no API; this report measures only the LLM extraction and routing.
