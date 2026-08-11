from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol

from app.core.config import settings

CORPUS_PATH = Path(__file__).resolve().parents[2] / "data" / "rag" / "kb_card_benefits.json"
COLLECTION_NAME = "benefit_rag_documents"


def _normalize(value: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", value.casefold())


def _cosine(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


class Embedder(Protocol):
    name: str

    def embed(self, texts: list[str], task_type: str) -> list[list[float]]: ...


class LocalHashEmbedder:
    """Credential-free embedding for local development and deterministic tests."""

    name = "local-hash-embedding-v1"

    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        del task_type
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        normalized = _normalize(text)
        tokens = re.findall(r"[0-9a-z]+|[가-힣]+", text.casefold())
        tokens.extend(normalized[index : index + 2] for index in range(len(normalized) - 1))
        vector = [0.0] * self.dimensions
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += -1.0 if digest[4] & 1 else 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class VertexEmbedder:
    name = settings.embedding_model

    def __init__(self) -> None:
        if not settings.gcp_project_id:
            raise RuntimeError("GCP_PROJECT_ID가 없어 Vertex AI 임베딩을 사용할 수 없습니다.")
        from google import genai

        self._client = genai.Client(
            vertexai=True,
            project=settings.gcp_project_id,
            location=settings.vertex_location,
        )

    def embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        from google.genai.types import EmbedContentConfig

        vectors: list[list[float]] = []
        for text in texts:
            response = self._client.models.embed_content(
                model=settings.embedding_model,
                contents=text,
                config=EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=settings.embedding_dimensions,
                ),
            )
            if not response.embeddings:
                raise RuntimeError("Vertex AI가 임베딩을 반환하지 않았습니다.")
            vectors.append(list(response.embeddings[0].values or []))
        return vectors


@dataclass(frozen=True)
class RankedDocument:
    document: dict[str, Any]
    score: float


@lru_cache(maxsize=1)
def load_curated_documents() -> tuple[dict[str, Any], ...]:
    payload = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    return tuple(payload["documents"])


class BenefitRagService:
    def __init__(self, embedder: Embedder | None = None, backend: str | None = None) -> None:
        selected_embedding_backend = settings.benefit_embedding_backend.casefold()
        self.embedder = embedder or (
            VertexEmbedder() if selected_embedding_backend == "vertex" else LocalHashEmbedder()
        )
        self.backend = (backend or settings.benefit_rag_backend).casefold()

    def _documents(self) -> list[dict[str, Any]]:
        if self.backend != "firestore":
            return [dict(document) for document in load_curated_documents()]

        from google.cloud import firestore

        client = firestore.Client(
            project=settings.gcp_project_id or None,
            database=settings.firestore_database,
        )
        documents = [snapshot.to_dict() for snapshot in client.collection(COLLECTION_NAME).stream()]
        if not documents:
            raise RuntimeError(
                "Firestore RAG 컬렉션이 비어 있습니다. 수집 스크립트를 먼저 실행하세요."
            )
        return documents

    def _rank(self, query: str, documents: list[dict[str, Any]]) -> list[RankedDocument]:
        query_vector = self.embedder.embed([query], "RETRIEVAL_QUERY")[0]
        missing = [document for document in documents if not document.get("embedding")]
        if missing:
            vectors = self.embedder.embed(
                [document["document_text"] for document in missing],
                "RETRIEVAL_DOCUMENT",
            )
            for document, vector in zip(missing, vectors, strict=True):
                document["embedding"] = vector
        return sorted(
            (
                RankedDocument(document, _cosine(query_vector, document["embedding"]))
                for document in documents
            ),
            key=lambda item: item.score,
            reverse=True,
        )

    @staticmethod
    def _card_matches(document: dict[str, Any], card_product: str) -> bool:
        needle = _normalize(card_product)
        candidates = [document["card_product"], *document.get("aliases", [])]
        return any(
            needle in _normalize(candidate) or _normalize(candidate) in needle
            for candidate in candidates
        )

    @staticmethod
    def _rule_matches(rule: dict[str, Any], canonical_brand: str, category: str) -> bool:
        brand = _normalize(canonical_brand)
        merchant_match = any(
            _normalize(pattern) in brand for pattern in rule.get("merchant_patterns", [])
        )
        normalized_category = _normalize(category)
        category_match = bool(normalized_category) and any(
            _normalize(pattern) in normalized_category or normalized_category in _normalize(pattern)
            for pattern in rule.get("category_patterns", [])
        )
        return merchant_match or category_match

    def search(
        self,
        canonical_brand: str,
        card_product: str = "",
        merchant_category: str = "",
        limit: int = 3,
    ) -> dict[str, Any]:
        documents = self._documents()
        query = f"매장 {canonical_brand} 업종 {merchant_category} 카드 {card_product} 적용 혜택"
        ranked = self._rank(query, documents)
        if not card_product.strip():
            return {
                "status": "card_product_required",
                "rules": [],
                "sources": [self._source(item) for item in ranked[:limit]],
                "message": "보유 카드 상품을 선택하면 검색 근거를 할인 계산에 사용할 수 있습니다.",
                "retrieval": self._retrieval_metadata(query, len(documents)),
            }

        selected = [item for item in ranked if self._card_matches(item.document, card_product)]
        matched_rules: list[dict[str, Any]] = []
        for item in selected[:limit]:
            for rule in item.document.get("rules", []):
                if self._rule_matches(rule, canonical_brand, merchant_category):
                    matched_rules.append(
                        {
                            **rule,
                            "source_id": item.document["source_id"],
                            "card_product": item.document["card_product"],
                            "retrieval_score": round(item.score, 4),
                        }
                    )
        sources = [self._source(item) for item in selected[:limit]]
        return {
            "status": "success" if matched_rules else "no_evidence",
            "rules": matched_rules,
            "sources": sources,
            "message": (
                "공식 카드 문서 임베딩에서 적용 후보를 검색했습니다."
                if matched_rules
                else "선택한 카드의 공식 문서에서 이 매장에 적용할 근거를 찾지 못했습니다."
            ),
            "retrieval": self._retrieval_metadata(query, len(documents)),
        }

    def status(self) -> dict[str, Any]:
        return {
            "status": "ready",
            "backend": self.backend,
            "embedding_model": self.embedder.name,
            "document_count": len(self._documents()),
            "source_policy": "official KB Card pages; three curated card documents",
        }

    def _retrieval_metadata(self, query: str, document_count: int) -> dict[str, Any]:
        return {
            "method": "cosine_similarity",
            "embedding_model": self.embedder.name,
            "backend": self.backend,
            "query": query,
            "document_count": document_count,
        }

    @staticmethod
    def _source(item: RankedDocument) -> dict[str, Any]:
        document = item.document
        return {
            "source_id": document["source_id"],
            "title": document["title"],
            "url": document["url"],
            "issuer": document["issuer"],
            "card_product": document["card_product"],
            "retrieval_score": round(item.score, 4),
        }


benefit_rag_service = BenefitRagService()
