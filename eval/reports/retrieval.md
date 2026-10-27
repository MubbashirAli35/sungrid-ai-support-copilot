# Retrieval results
Generated 2026-10-28 by `python -m eval.run_eval retrieval`. 14 questions with gold chunks, corpus of 69 chunks, bge-small-en-v1.5, fallback margin 0.05.

| Mode | recall@1 | recall@3 | recall@5 | MRR | questions missed at 5 |
|---|---|---|---|---|---|
| Dense, no category filter | 0.86 | 1.00 | 1.00 | 0.90 | - |
| Dense + BM25 (RRF), no category filter | 0.86 | 1.00 | 1.00 | 0.90 | - |
| Dense, correct label, strict filter | 0.86 | 1.00 | 1.00 | 0.90 | - |
| Dense + BM25, correct label, strict filter | 0.79 | 1.00 | 1.00 | 0.87 | - |
| Dense, correct label, with fallback | 0.86 | 1.00 | 1.00 | 0.90 | - |
| Dense, WRONG label, strict filter | 0.00 | 0.00 | 0.00 | 0.00 | q01, q02, q03, q04, q05, q06, q07, q08, q09, q10, q11, q12, q13, q14 |
| Dense, WRONG label, with fallback | 0.86 | 1.00 | 1.00 | 0.90 | - |

Ambiguous doc 06, strict filter on each acceptable label:

| question | label | hit@1 | hit@5 |
|---|---|---|---|
| q13 | incentive_rebate | 1 | 1 |
| q13 | billing_account | 1 | 1 |
| q14 | incentive_rebate | 0 | 1 |
| q14 | billing_account | 0 | 1 |

Caveats: n is small, and the 69-chunk corpus makes recall@5 easy (5 chunks is 7% of the corpus). The fallback margin was chosen after looking at the score gaps on these same questions, so the fallback rows are optimistic.
