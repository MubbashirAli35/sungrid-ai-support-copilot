# End-to-end results
Generated 2026-10-28 by `python -m eval.run_eval e2e`. Full copilot (runtime model claude-haiku-5-5, judge claude-sonnet-5-5), 23 questions (3 are unanswerable probes) x 3 runs.

- Overall pass: 66/69 (96%)
- Hard gate respected on eligibility questions: 12/12
- Runtime cost per question: $0.0004 (judge cost for this run, not a runtime cost: $0.0930)
- Latency per question: median 3.1s, max 5.1s

| type | passed |
|---|---|
| knowledge | 33/36 |
| ambiguous | 6/6 |
| eligibility | 12/12 |
| non_relevant | 6/6 |
| unanswerable | 9/9 |

Pass means: knowledge = no tool call, a gold chunk cited, every required fact present per the judge, no contradiction; eligibility = routed, parameters exact, gate respected; non_relevant = refused with no retrieval; unanswerable = abstained.

| id | type | passed | paths seen | detail |
|---|---|---|---|---|
| q01 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 3/3; contradiction 0 |
| q02 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 6/6; contradiction 0 |
| q03 | knowledge | 0/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 3/6; contradiction 0 **FAIL** |
| q04 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 6/6; contradiction 0 |
| q05 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 6/6; contradiction 0 |
| q06 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 6/6; contradiction 0 |
| q07 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 6/6; contradiction 0 |
| q08 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 3/3; contradiction 0 |
| q09 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 6/6; contradiction 0 |
| q10 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 3/3; contradiction 0 |
| q11 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 3/3; contradiction 0 |
| q12 | knowledge | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 9/9; contradiction 0 |
| q13 | ambiguous | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 6/6; contradiction 0 |
| q14 | ambiguous | 3/3 | knowledge | hit@5 3/3; cited gold 3/3; facts 9/9; contradiction 0 |
| q15 | eligibility | 3/3 | eligibility | params 3/3; gate 3/3 |
| q16 | eligibility | 3/3 | eligibility | params 3/3; gate 3/3 |
| q17 | eligibility | 3/3 | eligibility | params 3/3; gate 3/3 |
| q18 | eligibility | 3/3 | eligibility | params 3/3; gate 3/3 |
| q19 | non_relevant | 3/3 | out_of_scope |  |
| q20 | non_relevant | 3/3 | out_of_scope |  |
| u1 | unanswerable | 3/3 | abstain |  |
| u2 | unanswerable | 3/3 | abstain |  |
| u3 | unanswerable | 3/3 | abstain |  |

## Failing cases (last failing run shown)

**q03** Do Household-tier members get more voting weight than Community-tier members?
- path: knowledge; grade: {'routed': True, 'hit5': True, 'cited_gold': True, 'no_tool': True, 'facts': [True, False], 'contradiction': False, 'pass': False}
- answer: No. Under the voting rights section, Household and Commercial-tier members receive one vote per account, and Community-tier members also receive one vote per account regardless of the size of their shared-array subscription, so the excerpts do not give Household-tier members more voting weight than Community-tier members. Board seat elections are a separate matter: only household-tier members elect board seats.

Caveats: 23 questions, one author; the LLM judge is a second model reading a short answer against listed facts and is itself unvalidated against human grading; runs cannot be seeded.
