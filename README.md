# SunGrid AI Support Copilot (Part A)

A support assistant for SunGrid Cooperative members. It answers questions from the 14-document
knowledge base (retrieval-augmented, with citations) and checks Rooftop Rebate eligibility through
the provided `stub_tools.check_rebate_eligibility`, kept separate from retrieval and behind a hard gate.

## Setup
    python3 -m virtualenv .venv && source .venv/bin/activate   # python3 -m venv needs python3-venv
    pip install -r requirements.txt
    cp .env.example .env        # set ANTHROPIC_API_KEY (the only required variable)
    python -m copilot.ingest    # builds the local Qdrant index in ./qdrant_data (~69 chunks)

Optional: `COPILOT_RUNTIME_MODEL` (default `claude-haiku-5-5`), `COPILOT_JUDGE_MODEL` (default `claude-sonnet-5-5`).
No key is stored in the repository; `.env` is gitignored.

## Use
    python -m copilot ask "How many members does SunGrid have?"
    python -m copilot ask "ZIP 94103, income $85,000, 6 kW, approved installer. Do I qualify?" --json

Every request is traced to `traces/traces.jsonl` (gitignored): classification, retrieved chunks and
scores, tool inputs and outputs, answer, cost and latency.

## Tests and evals
    pytest                                   # 44 tests, no API calls
    python -m eval.run_eval retrieval        # no API calls
    python -m eval.run_eval classifier       # live, 3 runs
    python -m eval.run_eval eligibility      # live, 3 runs
    python -m eval.run_eval e2e              # live, 3 runs, LLM judge

Reports are in `eval/reports/`. The 20-question set is `eval/questions.yaml`; it was written from the
docs before any model output was looked at.

## How it works
1. **Ingest** (`copilot/ingest.py`): one chunk per `##` section with "Document title > Heading" prepended;
   `bge-small-en-v1.5` embeddings via fastembed; Qdrant in local mode. Each document has hand-assigned
   categories in `data/doc_registry.yaml` (multi-label, so the ambiguous doc 06 carries both
   `incentive_rebate` and `billing_account`). Doc 05's "Upcoming Changes" section is marked `unreleased`.
2. **Classify** (`copilot/classifier.py`): Haiku with structured output returns one category of six,
   a confidence, an optional secondary category and an intent (knowledge / eligibility_check / out_of_scope).
   The category is a retrieval filter, not a router. Inconsistent or failed output returns `None`,
   which means: search unfiltered, never call the tool.
3. **Retrieve** (`copilot/retrieval.py`): dense search filtered to the category (secondary included
   unless confidence is high). If the best chunk anywhere beats the best in-filter chunk by more than 0.05
   cosine, the label is treated as wrong and the search is repeated unfiltered.
4. **Answer** (`copilot/agent.py`): Haiku answers only from the retrieved excerpts and must cite their ids.
   Code rejects any answer whose citations are missing or not among the retrieved chunks and replies
   "not found" instead. Unreleased excerpts are labelled in the prompt; the prompt forbids using them as policy.
5. **Eligibility** (`copilot/tools/eligibility.py`): the model only extracts the four inputs (null when not
   stated). Code validates them, asks the member for anything missing without calling the service, calls the
   stub with a timeout, and builds the reply from a template. A dollar figure can only be the service's own
   `estimated_rebate_usd` when it said eligible. Any extraction, validation or service failure ends in a message
   with no figure.

`stub_tools.py` is unchanged (`tests/test_stub_unchanged.py` checks its hash).

## Results (all numbers from the reports in `eval/reports/`)
| Check | Result |
|---|---|
| Retrieval, 14 questions with gold chunks, no filter | recall@1 0.86, recall@5 1.00, MRR 0.90 |
| Classifier, 20 questions x 3 runs | category 60/60, intent 60/60 |
| Eligibility path, 8 cases x 3 runs | routed 24/24, parameters exact 24/24, gate respected 24/24 |
| End to end, 23 questions x 3 runs, LLM judge | 66/69 (96%); eligibility gate 12/12 |

Cost: about $0.0004 per question at runtime on Haiku 5.5 (classifier plus answer). Median latency 3.1 s.
The judge (Sonnet 5.5) costs about $0.09 per full eval run and is not a runtime cost.

## Failure analysis
- **q03 fails 3/3 (voting weight, docs 01 vs 08).** Doc 08 says one vote per account in every tier; doc 01 says
  "voting weight ... vary by tier". The copilot answers from doc 08 alone and does not flag the conflict, because
  doc 01's "Annual Meeting Attendance" chunk ranks 9th for this question, below the top 5 the model sees. This is a
  retrieval-recall problem at k=5, not a prompt problem. I did not raise k to fix one question; the real fixes are
  a larger k with reranking, or a conflict-detection pass over the chunks that share an entity.
- **A citation-format bug was found by the first e2e run** (the model sometimes wrote `[04#Common Fault Codes]`
  with brackets, which failed the citation check and produced a false "not found" on q09 and q10). Fixed by stripping
  brackets and adding a prompt line, then the eval was rerun: 63/69 before, 66/69 after. The fix was made after seeing
  the eval results, so the 96% is not a clean held-out number.
- **Classifier edge:** "Does SunGrid offer financing for electric vehicle chargers?" was labelled non-relevant and got the
  out-of-scope refusal instead of "not found". It is a safe error but a wrong label.
- **Ambiguous doc 06:** retrievable under either label. For q14 the classifier gave no secondary label in 3/3 runs,
  which is harmless only because the document itself carries both labels.

## Limits and honest caveats
- 20 questions plus a few probes, one author. The classifier prompt names "reversal or clawback of a rebate" under
  `incentive_rebate`, written after reading doc 06. The unanswerable probes and eligibility probes were written by
  the same author as the prompts. Scores are weak evidence, not an accuracy estimate.
- recall@5 is saturated on a 69-chunk corpus (5 chunks is 7% of it). The category filter gave no measurable gain at
  this size; it matters at scale, and the fallback is what makes it safe.
- The fallback margin (0.05) was chosen after looking at score gaps on these same questions.
- No score-based abstain threshold: answerable questions scored 0.74 and above, unanswerable probes up to 0.70, a gap too
  narrow to trust. Abstention rests on the model's `answerable` flag and the citation check.
- The LLM judge is unvalidated beyond a manual spot check of four answers; runs cannot be seeded (Haiku 5.5 rejects
  sampling parameters).
- The gate stops guessing but cannot detect a member who supplies complete, wrong details.
- Qdrant local mode locks its data directory to one process and warns above about 20k points; production would use a
  Qdrant server.

## Data-quality issues found in the documents
Docs 01 and 08 disagree on voting weight; doc 05's fourth tier is unreleased; the income threshold appears in the stub
but not in the docs; "Appendix A" is referenced but missing; doc 06 points to a section in doc 12 that does not exist;
doc 03's net-metering wording is inconsistent; doc 05 counts 4,200 installations while doc 14 counts about 5,000 members
(different things).
