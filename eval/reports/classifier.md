# Classifier results
Generated 2026-10-28 by `python -m eval.run_eval classifier`. Model claude-haiku-5-5, prompt classifier_v1, 20 questions x 3 runs.

- Category accuracy: 60/60 (100%)
- Intent accuracy: 60/60 (100%)
- Questions with identical output in all 3 runs: 20/20
- Cost of this run: $0.0115 for 60 calls ($0.19 per 1,000 classifier calls)

| id | expected category / intent | predicted per run (category/confidence/intent) | note |
|---|---|---|---|
| q01 | program_policies / knowledge | program_policies/high/knowledge; program_policies/high/knowledge; program_policies/high/knowledge | |
| q02 | program_policies / knowledge | program_policies/high/knowledge; program_policies/high/knowledge; program_policies/high/knowledge | |
| q03 | program_policies / knowledge | program_policies/high/knowledge; program_policies/high/knowledge; program_policies/high/knowledge | |
| q04 | incentive_rebate / knowledge | incentive_rebate/high/knowledge; incentive_rebate/high/knowledge; incentive_rebate/high/knowledge | |
| q05 | incentive_rebate / knowledge | incentive_rebate/high/knowledge; incentive_rebate/high/knowledge; incentive_rebate/high/knowledge | |
| q06 | incentive_rebate / knowledge | incentive_rebate/high/knowledge; incentive_rebate/high/knowledge; incentive_rebate/high/knowledge | |
| q07 | billing_account / knowledge | billing_account/high/knowledge; billing_account/high/knowledge; billing_account/high/knowledge | |
| q08 | billing_account / knowledge | billing_account/high/knowledge; billing_account/high/knowledge; billing_account/high/knowledge | |
| q09 | technical_installation / knowledge | technical_installation/high/knowledge; technical_installation/high/knowledge; technical_installation/high/knowledge | |
| q10 | technical_installation / knowledge | technical_installation/high/knowledge; technical_installation/high/knowledge; technical_installation/high/knowledge | |
| q11 | company_updates / knowledge | company_updates/high/knowledge; company_updates/high/knowledge; company_updates/high/knowledge | |
| q12 | company_updates / knowledge | company_updates/medium/knowledge; company_updates/medium/knowledge; company_updates/medium/knowledge | |
| q13 | incentive_rebate / knowledge | incentive_rebate/high/knowledge; incentive_rebate/high/knowledge; incentive_rebate/high/knowledge | both labels covered: 3/3. |
| q14 | incentive_rebate / knowledge | incentive_rebate/high/knowledge; incentive_rebate/high/knowledge; incentive_rebate/high/knowledge | both labels covered: 0/3. |
| q15 | incentive_rebate / eligibility_check | incentive_rebate/high/eligibility_check; incentive_rebate/high/eligibility_check; incentive_rebate/high/eligibility_check | |
| q16 | incentive_rebate / eligibility_check | incentive_rebate/high/eligibility_check; incentive_rebate/high/eligibility_check; incentive_rebate/high/eligibility_check | |
| q17 | incentive_rebate / eligibility_check | incentive_rebate/high/eligibility_check; incentive_rebate/high/eligibility_check; incentive_rebate/high/eligibility_check | |
| q18 | incentive_rebate / eligibility_check | incentive_rebate/high/eligibility_check; incentive_rebate/high/eligibility_check; incentive_rebate/high/eligibility_check | |
| q19 | non_relevant / out_of_scope | non_relevant/high/out_of_scope; non_relevant/high/out_of_scope; non_relevant/high/out_of_scope | |
| q20 | non_relevant / out_of_scope | non_relevant/high/out_of_scope; non_relevant/high/out_of_scope; non_relevant/high/out_of_scope | |

Caveats: 20 questions, written by the same person who wrote the prompt. The prompt contains no eval questions as examples, but its category definitions were written after reading the docs. Sampling parameters cannot be fixed on this model, so runs differ.
