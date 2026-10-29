# Delivery Plan: prototype to production in six weeks

**Team**: the Lead (full time), one AI/DS Associate (full time), one backend engineer at 50% (15 working days in total over the six weeks, booked in whole-day blocks). Starting point: the Part A prototype (a command-line tool, local Qdrant, 96% on a 23-question set with one known failure).

**Target**: a full production release to all members, with the architecture in the TDR. On release day traffic still ramps in steps with the canary procedure in C2, but the plan ends at 100%, not at a pilot.

## a. Work breakdown (in the order the work happens)

The dates assume the people and teams we depend on are on time.

| # | Item | Owner | Days | When |
|---|---|---|---|---|
| 1 | Eligibility service contract: request and response schema, auth, limits, who owns the rules, where the income limit comes from, how rule changes are announced, a staging endpoint. *Dependency: the service owner's time* | Lead | 2 | d1-2 |
| 2 | HTTP service around the existing pipeline (health check, request limits, timeouts), containerised. No dependency on item 1, so it runs the same two days | Backend | 2 | d1-2 |
| 3 | Qdrant server and the ingestion job in CI (Backend), and incremental ingestion by content hash (Associate), on the same days because neither needs the other | Backend 2, Associate 2 | 2 | d3-4 |
| 4 | Eligibility client: contract tests (built against the contract and stub), "inputs used" shown to the member, estimate wording, service-owner sign-off. Re-run against the real staging service when it exists (see risks) | Lead | 2 | d3-4 |
| 5 | Tracing to a store; dashboard and alerts from the TDR (gate violation pages immediately); cost alarm and spend cap | Backend | 3 | d5-7 |
| 6 | Privacy: redact member details in traces, retention, data processing terms for the model provider, injection testing. *Dependency: Security and Legal turnaround, which we do not control* | Lead (Security and Legal review) | 2.5 | starts d5, signed off by d16 |
| 7 | Eval set grown from 20 to 100 questions, with 20 of them held out and used only for the final check (they also give the classifier its first held-out set). *Dependency: the Support Lead writes and reviews the questions* | Associate (Support Lead reviews) | 2 | d6-7 |
| 8 | Auth, per-member rate limits, repeated-question cache (never for eligibility) | Backend | 2 | d8-9 |
| 9 | Judge validation, starting as soon as the 100 questions exist: staff label 100 answers, compare to the judge; fix the judge or stop trusting it. *Dependency: staff labelling time* | Associate | 3 | d8-10 |
| 10 | Retrieval upgrade, measured on the 100 questions. Today the pipeline takes the 5 nearest chunks. The change: fetch the 20 nearest chunks, then a reranker model, which reads the question and each chunk together and scores how well that chunk answers it, keeps the best 5, and a conflict check: if the kept chunks come from different documents and say different things about the same subject (voting weight in 01 vs 08), the answer must say they disagree and not pick one | Associate | 3 | d11-13 |
| 11 | Hand-off intents (refund reversal, clawback, billing dispute, eligibility dispute): classifier labels, ticket creation, replies. *Dependency: support staff must say which queue owns each intent and approve the reply wording* | Associate (design: Lead) | 1 | d14 |
| 12 | Load test at 100x the expected rate, run by the Lead and the Backend engineer together, on the final pipeline (it needs item 10, because the reranker adds CPU per request). The 3 days include the fixes the test shows are needed (pool sizes, timeouts, limits) and a re-run | Lead and Backend | 3 | d14-16 |
| 13 | Release pipeline and rollback drill | Backend | 2 | d17-18 |
| 14 | Shadow-mode pilot with support staff: Copilot drafts, staff see and rate at least 200 answers over 5 days; label analysis as ratings arrive; readout. *Dependency: staff time and rating speed* | Associate (analysis), Lead (readout) | 4 | d17-21 |
| 15 | Runbooks (on-call, incident, the two process documents) and handover training | Lead and Associate | 3 | d22-24 |
| 16 | Go/no-go review (d25), release (d26), 7 days of monitoring | Lead | 3 | d25-30 |


## b. Weekly milestones

| Week | Days | Milestone | Exit check |
|---|---|---|---|
| 1 | 1-5 | Eligibility contract agreed in writing and a staging date set. HTTP service running. Qdrant server, ingestion job and incremental ingestion working. Eligibility client passes contract tests against the stub. Tracing started, privacy review started. Infrastructure access ready. | Contract signed off by the service owner; a question answered through the HTTP service against the Qdrant server; a one-document change re-ingested without a full rebuild |
| 2 | 6-10 | Tracing, dashboard, alerts and cost alarm live. 100-question set written (d7). Auth, rate limits and cache done. Judge validated (d10) | A member question answered end to end in staging with its trace visible; judge agreement with staff measured and written down |
| 3 | 11-15 | Rerank and conflict detection measured (d13). Hand-off intents done (d14). Load test started on d14 | q03 fixed or the reason documented; no regression on the 100 questions |
| 4 | 16-20 | Load test and its fixes done (d16). Privacy and security sign-off (d16). Real eligibility service in staging by d16. Release pipeline and rollback drill done (d18). Shadow pilot started on d17 | Load test passed; rollback drill done; gate tests pass against the real service; cost per 1,000 queries re-measured and inside the plan |
| 5 | 21-25 | Pilot ends on d21 with its readout. Fixes from staff ratings. Runbooks and handover training (d22-24). Go/no-go on d25 | Staff rate at least 90% of at least 200 sampled answers "correct and safe", no gate violations; held-out 20 questions pass |
| 6 | 26-30 | Production release to all members on d26 through the canary procedure in C2. Daily monitoring for 7 days | Definition of done below met; no gate violation; cost and latency inside plan |

## c. Top risks and dependencies

- **The eligibility service is late, changes its response, or its rules differ from the stub** (it is owned by another team and "not available yet"). Item 1 in week 1 with a named owner and a staging date. Contract tests catch changes. Escalate by end of week 2 if there is no date. 
    - **Fallback:** release without the eligibility path (eligibility questions hand off to staff with a ticket); the knowledge path is independent.


- **Staff time:** the Support Lead for the 100-question set (item 7), labelling time (item 9), the ticket-queue owner (item 11) and five days of pilot ratings (item 14). Book names and days in week 1. If all four slip, the release moves from d26 to about d33. For item 11, the fallback is a plain "contact support" reply until the queue owner approves wording.
- **The income threshold and other rules appear in the stub but not in the documents,** so a real service may differ from what the knowledge base says. Ask the owner for the source of truth, add it to the documents, and test that the docs and the service agree.
- **Contradictory or unfinished documents** (voting weight in 01 and 08, the unreleased fourth tier, missing Appendix A, a dangling reference in 06). Content owners fix them in weeks 1 to 3; conflict detection (item 10) is the backstop.
- **Member data goes to an external model provider** (privacy, legal terms). Start the review on d5 (item 6); sign-off is needed before the pilot starts (d17).
- **Backend capacity** (50%, 1 spare day). Items in strict priority order; the cache in item 8 can move after release.
- **Small and self-written eval set; unvalidated judge.** Items 7 and 9; the 20 held-out questions and the shadow pilot are the real test.
- **Model deprecation or price change.** Pinned model id, C2 procedure, monthly check of the provider's notices.
- **Query volume unknown.** Re-measure in the load test (d14-16) and the pilot; autoscaling and the spend cap bound the damage.

**People dependencies:** the Support Lead (100-question set, labelling, pilot ratings), the ticket-queue owner, the eligibility service team, the Content Owners, Security and Legal, and whoever owns the cloud account.

## d. Definition of done for production release
All must be true, and a person other than the builder checks each:
1. The full eval suite passes on the 100-question set with the agreed thresholds, every failure listed, and no previously passing question lost; the 20 held-out questions pass at the agreed threshold. Zero gate violations across all runs.
2. Eligibility replies are built by code and tested against the **real** service in staging, with contract tests in CI. The service owner has signed off the integration.
3. Fail-closed behaviour proven: with the eligibility service, the vector store and the model provider each switched off in turn, the member gets a safe reply and never a made-up figure.
4. Shadow pilot: at least x% of at least 200 staff-rated answers "correct and safe", none harmful, and the reviewers' labels recorded.
5. Monitoring live: dashboard, alerts (gate violation pages the on-call), cost alarm with a spend cap, and a tested rollback (under 30 minutes).
6. Load test passed at 100x the expected peak rate, with p95 latency under y seconds.
7. Privacy and security review approved; no key or member data in the repository or the traces; injection tests run.
8. Runbooks (the two process documents, an incident guide, an on-call rota) handed over, and someone other than the author has done a release and a rollback using them.
9. Known gaps written down, accepted by the product owner, and put on the backlog.
