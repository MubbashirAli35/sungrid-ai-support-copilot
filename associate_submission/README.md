# SunGrid Copilot (Associate submission)

A RAG copilot for SunGrid Cooperative member questions.

## Run

```
pip install -r requirements.txt
python main.py
```

## How it works

1. The query is classified into a category.
2. Eligibility questions call `check_rebate_eligibility`.
3. Everything else is answered from the knowledge base.

Run `python eval.py` to evaluate.
