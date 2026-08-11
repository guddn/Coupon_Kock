# 쿠폰콕 (Coupon Kock)

위치 기반으로 보유 모바일 쿠폰과 카드·통신사 혜택을 주변 매장에 매칭하고, 공식 근거와 함께 예상 최저 결제 금액을 추천하는 MVP입니다.

## 프로젝트 구성

```text
frontend/           Flutter Android/Web 클라이언트
backend/            Cloud Run 배포용 FastAPI 서비스
data/               공공데이터 원본·가공 데이터 경계와 샘플
rag_sources/        카드·통신사 공식 혜택 문서 수집 manifest
infra/              GCP/Firebase 배포 설정과 스크립트
docs/               아키텍처, API, 데이터, 구현 계획
```

핵심 원칙은 다음과 같습니다.

- 쿠폰 이미지는 서버로 보내지 않고 Android 기기에서 OCR합니다.
- 쿠폰 PIN·바코드로 의심되는 문자열은 서버 전송 전에 마스킹합니다.
- Gemini는 쿠폰 구조화와 도구 호출/설명에만 사용합니다.
- 거리와 할인 금액은 결정적(deterministic) 코드가 계산합니다.
- 공식 출처와 유효기간이 없는 카드·통신사 혜택은 추천에 적용하지 않습니다.
- 정확한 위치, 카드번호, 결제내역은 저장하지 않습니다.

## 빠른 시작

### Backend

Python 3.11 이상이 필요합니다.

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

- 상태 확인: `GET http://localhost:8080/health`
- API 문서: `http://localhost:8080/docs`
- ADK 정보: `GET http://localhost:8080/api/agent`
- ADK 추천 실행: `POST http://localhost:8080/api/agent/recommendations`

### Flutter

```bash
cd frontend
flutter pub get

# Android: frontend/android/local.properties에 MAPS_API_KEY를 추가한 뒤 실행
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8080

# Web: API 키를 저장소에 쓰지 않고 런타임에 Maps SDK 로드
flutter run -d chrome --web-port=5000 \
  --dart-define=API_BASE_URL=http://localhost:8080 \
  --dart-define=GOOGLE_MAPS_API_KEY="$GOOGLE_MAPS_API_KEY"
```

Google Cloud Console에서 Android용 `Maps SDK for Android`, Web용 `Maps JavaScript API`를 활성화해야 합니다. 플랫폼별로 키를 분리하고 Android 패키지/SHA-1 또는 Web HTTP referrer 제한을 적용하세요. 현재 쿠폰 등록은 수동 입력이며 이미지 OCR은 후속 ML Kit 어댑터 범위입니다.

## 공공데이터 준비

1. 공공데이터포털에서 `소상공인시장진흥공단_상가(상권)정보_20260630` CSV를 내려받습니다.
2. 원본은 Git에 올리지 않고 `data/raw/stores/`에 둡니다.
3. `python backend/scripts/ingest_stores.py <csv-path> --output data/processed/stores.sample.jsonl`을 실행합니다.
4. 공정위 브랜드별 위치정보는 대표 브랜드 alias 보조로, 전국지역화폐가맹점표준데이터는 교차검증용으로 사용합니다.

상세 출처와 필드/품질 규칙은 [docs/public-data.md](docs/public-data.md), 전체 구성은 [docs/architecture.md](docs/architecture.md)를 확인하세요.

## 배포

- Backend: Cloud Run (`asia-northeast3` 기본)
- Web demo: Firebase Hosting
- 데이터: Firestore + Firestore Vector Search
- 원본 스냅샷/RAG 원문: Cloud Storage
- 비밀값: Secret Manager

실제 프로젝트 ID와 과금 계정이 필요한 생성/배포 명령은 [infra/README.md](infra/README.md)에 분리되어 있습니다.

## MVP 완료 기준

- 대표 쿠폰 이미지 필수 필드 추출 성공률 90% 이상
- 매장 매칭 정확도 90% 이상
- 20개 계산 fixture 일치율 100%
- RAG 핵심 근거 Top-5 포함률 80% 이상
- 추천 API 중앙값 5초 이하
- 사용자 과업 성공률 80% 이상
