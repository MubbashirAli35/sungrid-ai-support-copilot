"""Load the knowledge base, chunk it, and embed it."""
from typing import List, Dict

import numpy as np
from openai import OpenAI

import config

client = OpenAI(api_key=config.OPENAI_API_KEY)


def load_docs() -> List[Dict]:
    docs = []
    for path in sorted(config.DOCS_DIR.glob("*.md")):
        prefix = path.name[:2]
        docs.append(
            {
                "name": path.name,
                "category": config.DOC_CATEGORY[prefix],
                "text": path.read_text(),
            }
        )
    return docs


def chunk_text(text: str, size: int = config.CHUNK_SIZE) -> List[str]:
    """Split text into fixed-size chunks."""
    return [text[i : i + size] for i in range(0, len(text), size)]


def embed(texts: List[str]) -> np.ndarray:
    resp = client.embeddings.create(model=config.EMBED_MODEL, input=texts)
    return np.array([d.embedding for d in resp.data])


def build_index() -> Dict:
    """Chunk and embed every document. Returns an in-memory index."""
    chunks = []
    for doc in load_docs():
        for piece in chunk_text(doc["text"]):
            chunks.append(
                {"text": piece, "source": doc["name"], "category": doc["category"]}
            )
    vectors = embed([c["text"] for c in chunks])
    print(f"Indexed {len(chunks)} chunks")
    return {"chunks": chunks, "vectors": vectors}
