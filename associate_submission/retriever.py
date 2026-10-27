"""Retrieval and answer composition."""
from typing import List, Dict, Optional

import numpy as np
from openai import OpenAI

import config
from ingest import build_index, embed

client = OpenAI(api_key=config.OPENAI_API_KEY)

SYSTEM = (
    "You are the SunGrid Cooperative support copilot. Answer the member's "
    "question using the context below. Be concise and friendly."
)


def retrieve(query: str, category: Optional[str] = None) -> List[Dict]:
    """Return the top-k chunks, filtered to a category when one is given."""
    index = build_index()  # rebuild so edits to docs/ are always picked up
    q_vec = embed([query])[0]

    scores = index["vectors"] @ q_vec
    results = []
    for i in np.argsort(-scores):
        chunk = index["chunks"][i]
        if category and chunk["category"] != category:
            continue
        results.append(chunk)
        if len(results) == config.TOP_K:
            break
    return results


def compose_answer(query: str, chunks: List[Dict], extra: str = "") -> str:
    context = "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in chunks)
    resp = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\n{extra}\n\nQuestion: {query}"},
        ],
        temperature=0.2,
    )
    answer = resp.choices[0].message.content.strip()
    sources = sorted({c["source"] for c in chunks})
    return f"{answer}\n\nSources: {', '.join(sources)}"
