# 30-day development plan for the Associate

Part D(i)(c). Goal: in 30 days the Associate can take a change from a ticket to a released, measured result on this system without rescue, and has the habit of reporting honest numbers. The review (D1) shows a capable builder with good structure and three gaps: **measure honestly, treat safety rules as code, and respect ownership boundaries** (a service, a key, a number). The plan is built around those, not around new tools.

**How I will work with them.** A 30-minute 1:1 twice a week (Tuesday: unblock and review; Friday: look at the week's numbers together). Pair for the first hour of each new skill. PRs reviewed within one working day, with comments that explain why. I will say what I am doing and why, so the Associate can do the same later. Success is theirs to define each week in writing, and my feedback measures against that.

| Week | Focus | Concrete work | Evidence it is done |
|---|---|---|---|
| **1: Fix and understand** (days 1 to 7) | Own the review findings | Restore `stub_tools.py` and move the key (day 1). Fix the missing-input and hard-gate defects with tests that need no API (D1 B3, B4). Write a short note: how did the key, the stub edit and the 95% line happen, and what will you check next time? | The tests pass and fail in the right cases. The note exists and is honest. Walk me through the gate code and explain every branch. |
| **2: Measure** (days 8 to 14) | Evaluation habits | Build a 15 to 20 question evaluation set for their own version, written from the documents before running anything. Compute scores in code; report failures. Learn from my `eval/` folder: labelled data, deterministic scoring and a judge for free text, and why each. Read 5 failed answers by hand. | A report with every failure listed. A one-page "what I trust and do not trust about this score". No hard-coded numbers anywhere. |
| **3: Retrieval quality** (days 15 to 21) | Chunking, filters, ambiguity | Replace the fixed 500-character chunks with heading-based chunks; add a registry with several categories per document; make the category filter soft with a fallback (D1 H3 to H5). Measure recall@k before and after. | A before/after table on their own set. They can explain, without notes, why document 06 is handled as it is and one risk of their approach. |
| **4: Ship a change** (days 22 to 30) | Working in the team's process | Take a real ticket from the backlog (for example the conflict-detection item from the TDR, or the cost-per-trace report). Follow the SOP in C1 and the change control in C2 end to end: branch, evals, comparison table, approval, release, 7-day check. Present it at the team review. | The change is released with a comparison table and a rollback target. Their PR needs at most one round of comments. |

## What I will check at day 30
- **Safety by construction:** every rule that must always hold (the gate, no key in code) is a test, not a hope.
- **Honest numbers:** every figure in their work traces back to a report the code generated, with caveats.
- **Boundaries:** they ask the owner before editing something that belongs to someone else.
- **Communication:** a PR description saying what, why, how tested, and what could go wrong.
- **Independence:** they pick the next ticket's approach themselves and ask questions early.

## If it is going slower
At day 10 and day 20 I check progress against the table. If the tests and measurement habits are not in place by day 14, week 3 is shortened and the retrieval work moves to the following month; the safety and measurement habits come first, since the review shows those are the gaps that matter. I will say that plainly to the Associate at the time, not at day 30.

## What I own
Clear tickets with acceptance criteria. Review within a day. A weekly honest summary. Protecting 3 uninterrupted hours a day for this work. Making sure this plan does not collide with the delivery plan (D4): the tasks in weeks 3 and 4 are chosen to be the same tasks the delivery plan needs.
