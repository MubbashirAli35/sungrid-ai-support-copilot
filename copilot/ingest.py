"""Ingestion: load docs, chunk, embed, upsert into a local Qdrant collection."""
import argparse
from functools import lru_cache

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from copilot import config
from copilot.chunking import chunk_markdown
from copilot.registry import load_registry


@lru_cache(maxsize=1)
def embedder() -> TextEmbedding:
    return TextEmbedding(config.EMBED_MODEL)


def build_records():
    registry = load_registry()
    records = []
    for name, entry in sorted(registry.documents.items()):
        text = (config.DOCS_DIR / name).read_text(encoding="utf-8")
        for chunk in chunk_markdown(name, text):
            override = entry.section_overrides.get(chunk.heading)
            records.append({
                "doc": name,
                "doc_id": name.split("_")[0],
                "doc_title": chunk.doc_title,
                "heading": chunk.heading,
                "part": chunk.part,
                "text": chunk.text,
                "categories": entry.categories,
                "primary_category": entry.primary,
                "status": override.status if override else "published",
            })
    return records


def ingest(client: QdrantClient | None = None) -> int:
    records = build_records()
    vectors = list(embedder().embed([r["text"] for r in records]))
    client = client or QdrantClient(path=str(config.QDRANT_PATH))
    if client.collection_exists(config.COLLECTION):
        client.delete_collection(config.COLLECTION)
    client.create_collection(
        config.COLLECTION,
        vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE),
    )
    client.upsert(
        config.COLLECTION,
        points=[
            models.PointStruct(id=i, vector=v.tolist(), payload=r)
            for i, (r, v) in enumerate(zip(records, vectors))
        ],
    )
    return len(records)


def main():
    parser = argparse.ArgumentParser(description="Ingest the knowledge base into Qdrant.")
    parser.add_argument("--show", action="store_true", help="print chunks and exit without embedding")
    args = parser.parse_args()
    if args.show:
        for i, r in enumerate(build_records()):
            print(f"[{i}] {r['doc']} | {r['heading']} | {r['categories']} | {r['status']} | "
                  f"{len(r['text'].split())} words")
        return
    print(f"ingested {ingest()} chunks into {config.QDRANT_PATH}")


if __name__ == "__main__":
    main()
