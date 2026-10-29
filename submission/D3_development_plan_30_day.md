# 30-day development plan for the Associate

**Goal:** week 1, the Associate fixes their whole submission. Weeks 2 to 4, they train out four habits seen in it: handing over work they have not reread; using a model where code is enough; not asking what a choice/decision breaks; not counting what it costs. The code shows these habits; it is one submission, so on day 1 I ask them before treating any as settled.

## Week 1: fix everything (5 working days)

| Day | Fix | Done when |
|---|---|---|
| 1 | Restore `stub_tools.py`; remove the key from code and history and rotate it; add a pre-commit secret scan, ruff rules rejecting `print` and bare or blind `except`, and a test that fails if the stub changes | A planted fake key, `print` and bare `except` are each rejected |
| 2 | Eligibility and errors: no invented defaults, ask for missing inputs, reply built from a template, no figure unless the service says eligible, named exceptions with a safe reply, `logging` that never writes member text | Tests cover the cases in the review, a failed API call and a service timeout, with no API calls |
| 3 | Evaluation: 15 to 20 questions across every category, the ambiguous document, three eligibility cases, two non-relevant; score computed in code, failures listed | No typed numbers anywhere; a report with failures |
| 4 | Retrieval: build the index once at ingest; one shared client; heading-based chunks; several categories per document; validated label, soft filter with fallback; answers cite chunk ids checked in code | Embedding calls per question counted before and after; eval re-run |
| 5 | README (setup, key, eval, assumptions), pinned requirements, a self-review checklist written from the review; walk me through every change | Every review finding is closed or has a reason |

## Weeks 2 to 4: remove the habits

Four routines, each aimed at one habit, running through real work:

1. **Large seeded PR (daily).** To build the habit of reading everything under cognitive load, they review a long PR, 1000+ lines of mostly correct code, with 15 to 20 planted problems spread through it (debug prints, hardcoded numbers and keys, swallowed exceptions, a model used where a lookup would do, an index rebuilt per request, a default that invents an input, a missing failure path). They get 30 to 40 minutes and must say where each problem is and why it matters. I score found against planted, and note false alarms. A new PR each day, generated with an LLM and checked against my answer key. Week 2 sets their baseline, with no target. **By the end of week 3 they find at least 70%.** *Aims at: unread work.*
2. **LLM-use table.** For each model call in a design: what it does, why code cannot, what it risks. A PR that adds a model call without a row is not reviewed. *Aims at: model where code is enough.*
3. **Design note before building** (half a page): the choice, the alternative, what happens when the input is odd or the dependency is down, how we would know. My TDR failure register is the model. *Aims at: side effects and trade-offs.*
4. **Resource report in every PR:** model and embedding calls, tokens, seconds, CPU time and peak memory per question, before and after, measured on the same machine. *Aims at: uncounted resources.*

## Weekly review

Once every week we review their progress in 1:1 on everything above: the seeded-PR score, the LLM-use tables, the design notes and the resource reports.
