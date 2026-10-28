# Delivery Plan: prototype to production in six weeks

Part D(ii). Team: the Lead (full time), one AI/DS Associate (full time), one backend engineer at 50% (about 15 working days in total over the six weeks). Starting point: the Part A prototype (a command-line tool, local Qdrant, 96% on a 23-question set with one known failure). Target: a limited production release, with the architecture in the TDR. **Assumptions, because the brief does not say:** a launch means a limited release to a small share of members, not everyone; the cloud account, secrets store and CI exist or can be had in week 1; query volume is unknown, so sizing uses the TDR's cost per query and gets checked in week 4.

## a. Work breakdown (owner, days)

| # | Item | Owner | Days |
|---|---|---|---|
| 1 | Eligibility service contract: request and response schema, auth, limits, who owns the rules, where the income limit comes from, how rule changes are announced, a staging endpoint | Lead | 3 |
| 2 | HTTP service around the existing pipeline (health check, request limits, timeouts), containerised | Backend | 4 |
| 3 | Qdrant server, ingestion job in CI, incremental ingestion by content hash | Backend (job), Associate (hashing) | 3 + 2 |
| 4 | Tracing to a store; dashboard and alerts from the TDR (gate violation pages immediately); cost alarm and spend cap | Backend | 3 |
| 5 | Auth, per-member rate limits, repeated-question cache (never for eligibility) | Backend | 2 |
| 6 | Load test at 100x the expected rate; rollback drill; release pipeline | Backend | 3 |
| 7 | Eligibility client: contract tests against the staging service, "inputs used" shown to the member, estimate wording, service-owner sign-off | Lead | 4 |
| 8 | Eval set grown from 20 to about 80 questions with the Support Lead, including 20 held-out for the classifier, which was tuned on the first set | Associate (Support Lead reviews) | 5 |
| 9 | Retrieval: retrieve 20, rerank to 5, conflict detection (fixes the known q03 failure); measured against the 80-question set | Associate | 6 |
| 10 | Hand-off intents (refund reversal, clawback, billing dispute, eligibility dispute): classifier labels, ticket creation, replies | Associate (design: Lead) | 4 |
| 11 | Judge validation: staff label 100 answers, compare to the judge; fix the judge or stop trusting it | Associate | 3 |
| 12 | Privacy: redact member details in traces, retention, data processing terms for the model provider, injection testing | Lead (Security and Legal review) | 4 |
| 13 | Shadow-mode pilot with support staff: Copilot drafts, staff see and rate; label analysis | Associate (analysis), Lead (readout) | 4 |
| 14 | Runbooks: on-call, incident, the two process documents; handover training | Lead and Associate | 3 |
| 15 | Go/no-go review, limited release, 7-day monitoring | Lead | 3 |

Backend: items 2 to 6 total 15 days, which is the whole 50% allocation, so there is no spare capacity. Anything added to that engineer's list pushes the release. Associate: items 8 to 11, 13 and 14 total about 26 of 30 days, 4 days of buffer. The Associate's 30-day development plan (D3) uses items 8, 9 and 10 as their growth work.

## b. Weekly milestones

| Week | Milestone | Exit check |
|---|---|---|
| 1 | Eligibility contract agreed in writing and a staging endpoint date set. Infrastructure access ready. Service skeleton running. Eval set expansion started | Contract signed off by the service owner |
| 2 | Service running with Qdrant server and the ingestion job. Tracing on. Eligibility client passes contract tests against the stub. 80-question set written | A member question answered end to end through the HTTP service in staging |
| 3 | Rerank and conflict detection measured. Hand-off intents done. Dashboard and alerts live. Privacy review started | q03 fixed or the reason documented; no regression on the 80 questions |
| 4 | Real eligibility service in staging. Load test and rollback drill done. Cost alarm tested. Judge validation done | Gate tests pass against the real service. Cost per 1,000 queries re-measured and inside the plan |
| 5 | Shadow-mode pilot with support staff (no member sees Copilot answers). Fixes from staff ratings. Security review complete | Staff rate at least 90% of sampled answers "correct and safe", no gate violations |
| 6 | Go/no-go review. Limited release (about 5% of members) with the canary procedure in C2. Daily monitoring, handover | Definition of done below met |

## c. Top risks and dependencies

| Risk | Likelihood and effect | Plan |
|---|---|---|
| **The eligibility service is late, changes its response, or its rules differ from the stub** (it is owned by another team and "not available yet") | High, blocking | Item 1 in week 1 with a named owner and a staging date. Contract tests catch changes. Escalate by end of week 2 if there is no date. **Fallback:** release without the eligibility path (eligibility questions hand off to staff with a ticket); the knowledge path is independent |
| The income threshold and other rules appear in the stub but not in the documents, so a real service may differ from what the knowledge base says | Medium, wrong answers | Ask the owner for the source of truth. Add it to the documents. Test that the docs and the service agree |
| Contradictory or unfinished documents (voting weight in 01 and 08, the unreleased fourth tier, missing Appendix A, a dangling reference in 06) | High, wrong answers | Content owners fix them in weeks 1 to 3; conflict detection (item 9) is the backstop |
| Member data goes to an external model provider (privacy, legal terms) | Medium, can block release | Start the review in week 1 (item 12). If refused, fall back to a provider or hosting the company approves, which costs a re-run of every eval |
| Backend capacity (50%, no slack) | Medium, schedule | Items in strict priority order; items 5 and the cache can move after release |
| Small and self-written eval set; unvalidated judge | High, false confidence | Items 8 and 11; the shadow pilot is the real test |
| Model deprecation or price change | Low to medium | Pinned model id, C2 procedure, monthly check of the provider's notices |
| The Associate's ramp-up on the safety fixes takes longer than planned | Medium, schedule | The 4 buffer days; I take item 10 if needed |
| Query volume unknown | Medium | Re-measure in week 4; autoscaling and the spend cap bound the damage |

**People dependencies:** the Support Lead (80-question set, week 5 ratings), the eligibility service team, the Content Owners, Security and Legal, and whoever owns the cloud account.

## d. Definition of done for production release
All must be true, and a person other than the builder checks each:
1. The full eval suite passes on the 80-question set with the agreed thresholds, every failure listed, and no previously passing question lost. Zero gate violations across all runs.
2. Eligibility replies are built by code and tested against the **real** service in staging, with contract tests in CI. The service owner has signed off the integration.
3. Fail-closed behaviour proven: with the eligibility service, the vector store and the model provider each switched off in turn, the member gets a safe reply and never a made-up figure.
4. Shadow pilot: at least 90% of at least 200 staff-rated answers "correct and safe", none harmful, and the reviewers' labels recorded.
5. Monitoring live: dashboard, alerts (gate violation pages the on-call), cost alarm with a spend cap, and a tested rollback (under 30 minutes).
6. Load test passed at 100x the expected peak rate, with p95 latency under 8 seconds (it is about 5 s at the worst of my runs).
7. Privacy and security review approved; no key or member data in the repository or the traces; injection tests run.
8. Runbooks (the two process documents, an incident guide, an on-call rota) handed over, and someone other than the author has done a release and a rollback using them.
9. Known gaps written down, accepted by the product owner, and put on the backlog.
