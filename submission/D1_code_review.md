# Code Review: `associate_submission/`


The structure is right (classify, then tool or retrieve, then compose; the tool call is kept out of retrieval code). The problems are in what the structure does: it can tell a member "you are eligible for $2,000" on no information, it changes a service it does not own, and it reports an accuracy it did not measure. Severity: **Blocker** (must fix before anything else), **High**, **Medium**, **Low**.

## Blockers

- **API key committed.** `config.py:5` holds an `OPENAI_API_KEY` string in source. It looks like a placeholder, but keys belong in environment variables or a secrets manager, and the habit is the problem: 
    - Anything committed stays in Git history after it is removed. 


- **The eligibility service was edited.** `stub_tools.py` differs from the kit in two lines: `94110` was added to `APPROVED_ZIP_CODES` and `INCOME_THRESHOLD_USD` went from 120,000 to 150,000. 
    - The brief says to wire into the service, not rewrite it. 

- **The hard gate does not exist.** The brief says a failed eligibility condition must never get a partial or estimated answer that ignores the failure. Three places break it:
    - `agent.py:70-75`: for an ineligible member the prompt adds "Still, let them know what the program normally offers", so the reply mixes "not eligible" with program benefits and amounts from the documents.
    - `agent.py:57-62`: if the service raises, the code answers from the documents instead. The member gets a general rebate description with no mention that the check never happened. Failing open on an outage is the reverse of what a gate is for.
    - `agent.py:66-69`: the dollar figure is placed in a prompt and the model writes the reply. The model can drop, change or soften either the "no" or the amount.


- **Missing inputs are invented, so members are told they are eligible on no information.** `agent.py:23-36` defaults ZIP to `94102`, system size to `5.0` kW, installer to approved, and income to `0.0`. 

- **The reported accuracy is not a measurement.** `eval.py:18` prints "Overall accuracy: ~95%" as a literal string, whatever the tests do. The test list has 3 questions, none for eligibility, ambiguity, or four of the five categories; the brief asks for 15 to 20 covering every category, the ambiguous document, three eligibility cases including a failure, and two non-relevant. 

## High

- **The eligibility router matches words, so unrelated questions reach the tool.** `agent.py:9-16`. No Concept of Query Intent

- **The index is rebuilt and re-embedded on every query.** `retriever.py:20` calls `build_index()` inside `retrieve()`, so every question pays an embedding call for all chunks of all 14 documents. This is a cost and latency bug (it grows with the corpus) and the opposite of an ingest step. Build once, persist, rebuild on document change.

- **A wrong category label returns nothing, with no fallback.** `retriever.py:26-27` is a hard filter. The label is raw model text, `classifier.py:27` strips it but never checks it is in `CATEGORIES`, and `agent.py:50` compares by exact string. A label of "Billing and Account" or "Billing & Account." silently matches no chunk and the member gets "I don't know". 

- **The ambiguous document is not handled.** `config.py:29` maps document 06 to Billing & Account only, so a question about a rebate clawback, classified as Incentive, cannot find it. 

- **Fixed 500-character chunks.** `ingest.py:26-28` cuts mid-sentence and mid-word, drops headings, and puts a table row's header in a different chunk. The document title is never attached to the chunk, so "what is the threshold?" has no idea which program it came from. 

- **Answers are not grounded.** `retriever.py:12-15` says to use the context but not to refuse when it is missing or to say which document each claim came from; temperature is 0.2. `retriever.py:46` prints "Sources:" as every file retrieved, not the ones the answer used, which looks like a citation and is not one.

## Medium

- Errors are not handled anywhere: a failed embedding or chat call raises through `agent.py` and kills the session. `except Exception` at `agent.py:59` hides which error. 
- `requirements.txt` lists `openai` and `numpy` with no versions; results and failures cannot be reproduced. 
- No tests, no logging or traces; the `print` calls (`classifier.py:28`, `agent.py:56`) are the only record of what happened and would print member data in production.
- `DOC_CATEGORY[prefix]` (`ingest.py:19`) raises `KeyError` for any new document, and category data lives in the code, so adding a document is a code change.
- The classifier prompt gives only category names, no definitions, no examples and no output format check. It has to guess at the boundary between "Incentive & Rebate" and "Billing & Account".

## Low
- Module-level `OpenAI(...)` clients are created three times, at import. One shared client, created in a function, is easier to test.
- `main.py` has no error exit and `eval.py` runs on import. Wrap in `if __name__ == "__main__"`.
- Substring matching in `eval.py:13` passes an answer that contains the word "March" in any context; it cannot find a wrong answer that also contains the right word.

## What is good
- The shape is right: classify, branch, tool or retrieve, compose. The agent has more than two steps, and the tool is called from `agent.py` and never from retrieval code, as the brief asks.
- Small readable modules, type hints, a docstring on each module, and no framework hiding the logic. This is a good base to build on, and I found each issue quickly because of it.
- The non-relevant reply is correct and checked before any retrieval happens.
- The category list and chunk size sit in one config file, and not scattered through the code.

