"""Verify three official KB Card pages, embed the curated documents, and load Firestore."""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.services.benefit_rag import (
    COLLECTION_NAME,
    VertexEmbedder,
    load_curated_documents,
)


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        del attrs
        if tag in {"script", "style", "noscript"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth and data.strip():
            self.parts.append(data.strip())


def fetch_visible_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "CouponKock-RAG-Ingestion/1.0"})
    with urlopen(request, timeout=30) as response:
        parser = VisibleTextParser()
        parser.feed(response.read().decode("utf-8", errors="replace"))
    return " ".join(" ".join(parser.parts).split())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-source-check", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    documents = [dict(document) for document in load_curated_documents()]
    for document in documents:
        if args.skip_source_check:
            source_text = ""
        else:
            source_text = fetch_visible_text(document["url"])
            missing = [marker for marker in document["source_markers"] if marker not in source_text]
            if missing:
                raise SystemExit(f"{document['source_id']}: 원문 표식 누락: {missing}")
        document.update(
            {
                "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
                "source_character_count": len(source_text),
            }
        )

    if args.verify_only:
        for document in documents:
            print(
                document["source_id"],
                document["source_character_count"],
                document["source_sha256"],
            )
        return

    if not settings.gcp_project_id:
        raise SystemExit("GCP_PROJECT_ID를 설정하세요.")

    embedder = VertexEmbedder()
    vectors = embedder.embed(
        [document["document_text"] for document in documents],
        "RETRIEVAL_DOCUMENT",
    )
    now = datetime.now(UTC).isoformat()
    for document, vector in zip(documents, vectors, strict=True):
        document.update(
            {
                "embedding": vector,
                "embedding_model": embedder.name,
                "ingested_at": now,
            }
        )

    if args.dry_run:
        for document in documents:
            print(document["source_id"], len(document["embedding"]), document["source_sha256"])
        return

    from google.cloud import firestore

    client = firestore.Client(
        project=settings.gcp_project_id,
        database=settings.firestore_database,
    )
    batch = client.batch()
    for document in documents:
        reference = client.collection(COLLECTION_NAME).document(document["source_id"])
        batch.set(reference, document)
    batch.commit()
    print(f"Firestore {COLLECTION_NAME} 컬렉션에 {len(documents)}개 문서를 적재했습니다.")


if __name__ == "__main__":
    main()
