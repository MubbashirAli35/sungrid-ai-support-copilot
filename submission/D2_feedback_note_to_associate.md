# Feedback note

**To:** the Associate. **From:** Lead, AI & DS. **Re:** your SunGrid Copilot submission.

Hi,

Thank you for the submission. Before the problems, what I liked: the flow is right (classify, then tool or retrieval, then compose), the tool call lives in the agent and never in retrieval, and the code is small and easy to read. I found every issue in under an hour because your modules are clean. That is a real strength and I want you to keep it.

I have to be direct about the rest, because several things would cause real harm to a member if this went live. The full review is in the repository with file and line numbers. These are the ones that matter most:

1. **The eligibility answers can be wrong in a way a member would act on.** When the message has no income, ZIP or installer, the code fills in defaults, so "Am I eligible? I live in 94103" returns "eligible, $2,000". When the income is written as "$85,000, 6 kW" the pattern misses it and uses 0, with the same result. And when the service says no, your prompt asks the model to "let them know what the program normally offers", which is the partial answer the brief forbids. For eligibility, the rule is: if anything is missing, ask; if the service says no, say no with the reason and nothing else; if the service is down, say so.
2. **`stub_tools.py` was changed** (a ZIP code added, the income limit raised from 120,000 to 150,000), and it is not ours to change. Please restore it. If a rule looks wrong, tell the team that owns it. I would like to hear why you changed it, because there may be a reason I should know.
3. **`config.py` has an API key in it,** and **`eval.py` prints "Overall accuracy: ~95%" as a fixed string.** I want to understand how those got there before assuming anything. A key goes in an environment variable. A score is a number the code computes, and one printed by hand is worse than no score, because it makes people trust the other numbers less. In this job, an honest "3 of 5 pass" is worth far more than an unmeasured 95%. The same goes for failures: I would rather see them listed than hidden.

Things I'd like you to do, in this order: restore the stub and move the key (today); fix the missing-input and gate behaviour and add tests for the cases in the review; build the evaluation set (15 to 20 questions across every category, the ambiguous document, three eligibility cases and two non-relevant ones) and report what fails. Then the retrieval items.

This is a fair amount of feedback and I know that is hard to read. None of it says you can't do this work. These are the mistakes people make the first time they build one of these systems, and they are fixable in a week. Let's go through it together in a 45-minute session: bring your questions, and tell me where you disagree with the review. I may be wrong on some points.

Best,
Lead, AI & DS
