from fastapi.testclient import TestClient

from app.main import app
from app.services.benefit_rag import BenefitRagService, LocalHashEmbedder, load_curated_documents


def test_corpus_contains_exactly_three_official_card_documents() -> None:
    documents = load_curated_documents()

    assert len(documents) == 3
    assert all(document["url"].startswith("https://card.kbcard.com/") for document in documents)
    assert {document["source_id"] for document in documents} == {
        "kbcard-my-wesh-09923",
        "kbcard-talktalk-with-09272",
        "kbcard-goodday-ollim-09063",
    }


def test_local_embedding_search_returns_selected_card_rule() -> None:
    service = BenefitRagService(embedder=LocalHashEmbedder(), backend="local")

    result = service.search(
        canonical_brand="스타벅스 수원점",
        merchant_category="커피 전문점",
        card_product="톡톡with카드",
    )

    assert result["status"] == "success"
    assert result["rules"][0]["rule_id"] == "talktalk-with-starbucks-50"
    assert result["rules"][0]["max_discount"] == 10_000
    assert result["sources"][0]["url"].startswith("https://card.kbcard.com/")


def test_rag_status_and_search_endpoints() -> None:
    client = TestClient(app)

    status_response = client.get("/api/benefits/status")
    search_response = client.get(
        "/api/benefits/search",
        params={
            "canonical_brand": "스타벅스 아주대점",
            "merchant_category": "카페",
            "card_product": "톡톡 with",
        },
    )

    assert status_response.status_code == 200
    assert status_response.json()["document_count"] == 3
    assert search_response.status_code == 200
    assert search_response.json()["rules"][0]["discount_percent"] == 50
