# Feedback note

Hey, thanks for the submission. The flow and overall design are right i.e. classify, then tool or retrieval, then compose (a smart choice not to route the whole pipeline on the classification category), the tool call lives in the agent and never in retrieval, and the code is small, modular and thus easy to read. I really appreciate and want you to keep it up. 

However, I found some serious critical errors that, had they gone live, would have caused considerable harm to the end customer and thus to the firm. The full review is attached in `D1_code_review.md`, but these were the most serious:


1. **The eligibility answers can be wrong in a way a member would act on.** 
    - When the message has no income, ZIP or installer, the code fills in defaults, so "Am I eligible? I live in 94103" returns "eligible, $2,000". 
    - When the income is written as "$85,000, 6 kW" the pattern misses it and uses 0, with the same result. 
    - And when the service says no, your prompt asks the model to "let them know what the program normally offers", which is the partial answer the brief forbids.
2. **`stub_tools.py` was changed** (a ZIP code added, the income limit raised from 120,000 to 150,000), and it is not ours to change. Please restore it. If a rule looks wrong, tell the team that owns it. I would like to hear why you changed it, because there may be a reason I should know.
3. **`config.py` has an API key in it,** and **`eval.py` prints "Overall accuracy: ~95%" as a fixed string.** These two look like slips rather than choices. I would like to understand how they got there so we can put a check in place that catches them for you. A key belongs in an environment variable (and this one should be rotated); a score should be a number the code computes, so people can trust your other numbers. 

Please restore the stub and move/rotate the key. Fix the missing-input and gate behaviour and add tests for the cases in the review, then build the evaluation set (15 to 20 questions across every category, the ambiguous document, three eligibility cases and two non-relevant ones) and report what fails. Then the retrieval items.

Let's go through it together in a 30-minute session: bring your questions, and tell me where you disagree with the review. I may be wrong on some points.

