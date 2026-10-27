"""Retrieval: dense search with a soft category filter, an unfiltered fallback,
and optional BM25 fusion."""
import re
from dataclasses import dataclass

from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi

from copilot import config
from copilot.ingest import embedder

RRF_K = 60
CANDIDATES = 20


@dataclass
class Hit:
    key: str  # "<doc number>#<heading>", the id the eval scores against
    doc: str
    heading: str
    text: str
    score: float
    categories: list[str]
    status: str


@dataclass
class SearchResult:
    hits: list[Hit]
    scope: str  # "filtered" | "unfiltered"
    fallback: bool = False


def _tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _hit(point) -> Hit:
    p = point.payload
    return Hit(f"{p['doc_id']}#{p['heading']}", p["doc"], p["heading"], p["text"],
               getattr(point, "score", None) or 0.0, p["categories"], p["status"])


class Retriever:
    def __init__(self, client: QdrantClient | None = None):
        self.client = client or QdrantClient(path=str(config.QDRANT_PATH))
        points, _ = self.client.scroll(config.COLLECTION, limit=10_000, with_payload=True)
        self._chunks = [_hit(p) for p in points]
        self._bm25 = BM25Okapi([_tokens(c.text) for c in self._chunks])

    def close(self):
        self.client.close()

    def _dense(self, query: str, categories: list[str] | None, limit: int) -> list[Hit]:
        vector = next(iter(embedder().embed([query]))).tolist()
        flt = None
        if categories:
            flt = models.Filter(must=[models.FieldCondition(
                key="categories", match=models.MatchAny(any=categories))])
        points = self.client.query_points(config.COLLECTION, query=vector,
                                          query_filter=flt, limit=limit).points
        return [_hit(p) for p in points]

    def _keyword(self, query: str, categories: list[str] | None, limit: int) -> list[Hit]:
        scores = self._bm25.get_scores(_tokens(query))
        ranked = sorted(zip(self._chunks, scores), key=lambda cs: cs[1], reverse=True)
        allowed = set(categories) if categories else None
        out = []
        for chunk, score in ranked:
            if score <= 0 or (allowed and not allowed & set(chunk.categories)):
                continue
            out.append(Hit(**{**chunk.__dict__, "score": float(score)}))
            if len(out) == limit:
                break
        return out

    def search(self, query: str, categories: list[str] | None = None, k: int = 5,
               hybrid: bool = False, fallback_margin: float | None = config.FALLBACK_MARGIN) -> SearchResult:
        """categories is a soft filter. If the best chunk anywhere scores clearly higher
        than the best chunk inside the filter, the label was probably wrong, so search
        everywhere (the margin is on cosine similarity). fallback_margin=None disables it."""
        scope, fallback = ("filtered" if categories else "unfiltered"), False
        if categories and fallback_margin is not None:
            inside = self._dense(query, categories, 1)
            anywhere = self._dense(query, None, 1)
            if not inside or anywhere[0].score - inside[0].score > fallback_margin:
                categories, scope, fallback = None, "unfiltered", True

        dense = self._dense(query, categories, CANDIDATES if hybrid else k)
        if not hybrid:
            return SearchResult(dense[:k], scope, fallback)

        fused: dict[str, float] = {}
        hits: dict[str, Hit] = {}
        for ranking in (dense, self._keyword(query, categories, CANDIDATES)):
            for rank, hit in enumerate(ranking, start=1):
                fused[hit.key] = fused.get(hit.key, 0.0) + 1.0 / (RRF_K + rank)
                hits.setdefault(hit.key, hit)
        top = sorted(fused, key=fused.get, reverse=True)[:k]
        return SearchResult([Hit(**{**hits[key].__dict__, "score": fused[key]}) for key in top],
                            scope, fallback)
