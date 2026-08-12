# 공식 카드 혜택 RAG

MVP는 KB국민카드 공식 상품 페이지에서 검수한 카드 문서 3개만 사용합니다.

| 문서 | 대표 검색 범위 | 공식 원문 |
|---|---|---|
| My WE:SH | 음식점, 편의점, 커피 | `cooperationcode=09923` |
| 톡톡 with | 스타벅스, 간편결제, 구독 | `cooperationcode=09272` |
| 굿데이올림 | 음식, 커피, 편의점, 약국 | `cooperationcode=09063` |

검수한 구조화 문서는 `backend/data/rag/kb_card_benefits.json`, 수집·임베딩 스크립트는
`backend/scripts/ingest_card_benefits.py`, 검색 구현은
`backend/app/services/benefit_rag.py`에 있습니다. 원문 HTML 전체를 서비스 응답이나 Git에
복제하지 않고, 혜택 규칙·출처 URL·수집 시점의 SHA-256만 Firestore에 저장합니다.

## 로컬 확인

로컬 기본값은 자격증명이 필요 없는 256차원 해시 임베딩입니다. 문서 검색, 코사인 유사도,
카드/매장 필터, 공식 출처 반환까지 운영과 같은 흐름을 재현합니다.
프로젝트는 Python 3.11~3.13을 지원하며 저장소의 `.venv`는 Python 3.12입니다.

```bash
cd backend
.venv/Scripts/python.exe -m pip install -e '.[gcp]'
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8080

curl -sS 'http://localhost:8080/api/benefits/status'
curl -sS -G 'http://localhost:8080/api/benefits/search' \
  --data-urlencode 'canonical_brand=스타벅스 아주대점' \
  --data-urlencode 'merchant_category=커피 전문점' \
  --data-urlencode 'card_product=톡톡 with카드'
```

## Vertex AI 임베딩 및 Firestore 적재

Cloud Shell 또는 ADC가 설정된 Bash에서 실행합니다.

```bash
PROJECT_ID='proj-aj25-211200020328'

gcloud config set project "$PROJECT_ID"
gcloud services enable aiplatform.googleapis.com firestore.googleapis.com

cd ~/Coupon_Kock/backend
python -m pip install -e '.[gcp]'

export GCP_PROJECT_ID="$PROJECT_ID"
export VERTEX_LOCATION='global'
export EMBEDDING_MODEL='gemini-embedding-001'
export EMBEDDING_DIMENSIONS='768'

gcloud auth application-default login
gcloud auth application-default set-quota-project "$PROJECT_ID"

python scripts/ingest_card_benefits.py --verify-only
python scripts/ingest_card_benefits.py --dry-run
python scripts/ingest_card_benefits.py
```

첫 명령은 GCP 호출 없이 공식 페이지의 표식과 원문 해시를 확인합니다. 두 번째 명령은
Vertex AI 임베딩 차원을 검증하고, 세 번째 명령은 Firestore의
`benefit_rag_documents` 컬렉션에 정확히 3개 문서를 적재합니다.

Cloud Run 런타임을 실제 임베딩 저장소로 전환합니다.

```bash
gcloud run services update coupon-kock \
  --project="$PROJECT_ID" \
  --region='asia-northeast3' \
  --update-env-vars='BENEFIT_RAG_BACKEND=firestore,BENEFIT_EMBEDDING_BACKEND=vertex,EMBEDDING_MODEL=gemini-embedding-001,EMBEDDING_DIMENSIONS=768,DEMO_CARD_PRODUCT=톡톡 with카드'
```

Cloud Run 런타임 서비스 계정에는 최소한 Vertex AI 사용자와 Firestore 읽기 권한이 필요합니다.
수집을 실행하는 계정에는 Firestore 쓰기 권한이 추가로 필요합니다.

## 안전한 계산 규칙

- 선택한 카드 상품과 매장명/업종이 모두 맞는 규칙만 계산기로 전달합니다.
- 공식 `source_id`가 없는 혜택은 계산하지 않습니다.
- 쿠폰 중복 할인은 공식 문서에 명시되지 않아 기본적으로 허용하지 않습니다.
- 전월 실적과 월 잔여 한도는 확인 필요 조건으로 표시합니다.
- 카드사 원문이 바뀌어 표식 검증이 실패하면 적재를 중단하고 사람이 다시 검수합니다.
