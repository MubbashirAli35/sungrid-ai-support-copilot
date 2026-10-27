"""Copilot agent: classify -> (eligibility tool | retrieve) -> compose."""
import re
from typing import Dict

from classifier import classify_query
from retriever import retrieve, compose_answer
from stub_tools import check_rebate_eligibility

ELIGIBILITY_WORDS = ("eligible", "eligibility", "qualify", "get a rebate", "am i entitled")

NON_RELEVANT_REPLY = "Sorry, I can only help with SunGrid Cooperative questions."


def is_eligibility_query(query: str) -> bool:
    q = query.lower()
    return any(w in q for w in ELIGIBILITY_WORDS)


def extract_params(query: str) -> Dict:
    """Pull eligibility inputs out of the member's message."""
    q = query.lower()

    zip_match = re.search(r"\b(9\d{4})\b", q)
    household_zip = zip_match.group(1) if zip_match else "94102"

    income_match = re.search(r"\$?\s*([\d,]+)\s*(k)?\s*(?:a year|per year|annually|income|salary)", q)
    income = 0.0
    if income_match:
        income = float(income_match.group(1).replace(",", ""))
        if income_match.group(2):
            income *= 1000

    size_match = re.search(r"([\d.]+)\s*kw", q)
    system_size = float(size_match.group(1)) if size_match else 5.0

    installer_approved = not re.search(r"non-approved|not approved|unapproved|not on the list", q)

    return {
        "household_zip": household_zip,
        "annual_income_usd": income,
        "system_size_kw": system_size,
        "installer_approved": installer_approved,
    }


def run_agent(query: str) -> str:
    # Step 1: classify
    category = classify_query(query)

    if category == "non_relevant":
        return NON_RELEVANT_REPLY

    # Step 2: eligibility questions go to the tool
    if is_eligibility_query(query):
        params = extract_params(query)
        print("eligibility params:", params)
        try:
            result = check_rebate_eligibility(**params)
        except Exception:
            # service is down, fall back to the documents
            chunks = retrieve(query, category)
            return compose_answer(query, chunks)

        chunks = retrieve("Rooftop Rebate Program eligibility and rebate amount", category)
        if result["eligible"]:
            extra = (
                f"The member IS eligible. Estimated rebate: "
                f"${result['estimated_rebate_usd']}."
            )
        else:
            extra = (
                f"The member is NOT eligible because: {result['reason']} "
                "Still, let them know what the program normally offers."
            )
        return compose_answer(query, chunks, extra)

    # Step 3: general knowledge, retrieval filtered by category
    chunks = retrieve(query, category)
    if not chunks:
        return "I don't know."
    return compose_answer(query, chunks)
