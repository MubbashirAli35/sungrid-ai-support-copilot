"""Classify a member query into a single primary category."""
from openai import OpenAI

import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

PROMPT = """You are a classifier for SunGrid Cooperative member questions.
Pick exactly ONE category from this list and reply with the category only:
{cats}

Question: {q}
Category:"""


def classify_query(query: str) -> str:
    resp = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": PROMPT.format(cats="\n".join(config.CATEGORIES), q=query),
            }
        ],
        temperature=0,
    )
    label = resp.choices[0].message.content.strip()
    print("category:", label)
    return label
