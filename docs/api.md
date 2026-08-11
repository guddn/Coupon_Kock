# API 계약

모든 응답에는 추적 가능한 `request_id`를 포함하며, 서버 로그에는 OCR 원문과 정확한 위치를 남기지 않습니다.

## `GET /health`

서비스 프로세스 상태를 반환합니다.

## `POST /api/coupons/parse`

```json
{
  "user_id": "demo-user",
  "sanitized_raw_text": "스타카페 아메리카노 유효기간 2026-12-31"
}
```

응답은 `brand`, `product_name`, `coupon_type`, `face_value`, `expiry_date`, `confidence`, `needs_review`를 포함합니다. 현재 scaffold는 안전한 placeholder parser이며 Vertex AI adapter 연결 전에는 항상 사용자 확인을 요구합니다.

## `POST /api/coupons`

확정된 쿠폰 정보를 등록합니다. PIN과 바코드는 요청 스키마에 포함하지 않습니다.

```json
{
  "user_id": "demo-user",
  "brand": "스타카페",
  "product_name": "모바일 금액권",
  "coupon_type": "fixed",
  "face_value": 5000,
  "expiry_date": "2027-12-31"
}
```

저장소 어댑터는 로컬 기본값인 메모리와 운영용 Firestore를 지원합니다. Cloud Run에는 `COUPON_STORAGE_BACKEND=firestore`와 `GCP_PROJECT_ID`를 설정하고 런타임 서비스 계정에 Firestore 접근 권한을 부여해야 합니다.

## `GET /api/coupons?user_id=demo-user`

사용자의 등록 쿠폰을 유효기간 순으로 반환합니다.

## `GET /api/stores/nearby`

```text
/api/stores/nearby?latitude=37.2822&longitude=127.0437&radius_m=1000&limit=5
```

백엔드만 공공데이터포털의 소상공인시장진흥공단 `storeListInRadius` API를 호출합니다. 앱에는 공공데이터 인증키를 전달하지 않습니다. 결과는 현재 위치와의 거리 오름차순으로 정렬되며 기본적으로 가장 가까운 5개 매장을 반환합니다. `limit`은 1~20 범위에서 지정할 수 있습니다. 응답의 `data_source`는 실제 연동 시 `public_data`, 키가 없거나 호출에 실패하면 `fixture`이며 이 경우 `notice`도 함께 반환합니다.

## `POST /api/recommendations`

```json
{
  "user_id": "demo-user",
  "latitude": 37.5665,
  "longitude": 126.978,
  "purchase_amount": 10000
}
```

`store_id`를 생략하면 공공데이터 조회 결과에서 가장 가까운 매장을 선택하고, 지정하면 반경 1km 안의 해당 매장을 선택합니다. 선택된 매장명과 브랜드가 일치하고 만료되지 않은 Firestore 쿠폰을 각각 계산한 뒤 최종 결제금액이 낮은 순으로 정렬합니다. 여러 쿠폰을 임의로 합산하지 않습니다.

응답은 매장, 정렬된 후보, 추천 옵션과 확인이 필요한 조건을 반환합니다. 카드·통신사 RAG가 연결되기 전까지 검증되지 않은 카드 할인은 계산하지 않으며 `sources`는 빈 배열입니다. 이 엔드포인트는 Flutter용 결정적 계산 API이며 ADK 모델을 실행하지 않습니다.

## `GET /api/agent`

현재 Cloud Run에 포함된 ADK 에이전트의 이름, 모델, 도구 목록과 실행 엔드포인트를 반환합니다. 모델 호출은 발생하지 않습니다.

```json
{
  "agent_name": "coupon_kock_agent",
  "model": "gemini-2.5-flash",
  "framework": "Google ADK 2.6.3",
  "tools": [
    "match_nearby_store",
    "load_user_benefit_context",
    "retrieve_official_benefit_rules",
    "calculate_discount_options"
  ],
  "run_endpoint": "POST /api/agent/recommendations",
  "session_persistence": "ephemeral"
}
```

## `POST /api/agent/recommendations`

ADK Runner가 `gemini-2.5-flash`를 호출하고 함수 도구를 실행한 뒤 근거 기반 추천 설명을 반환합니다.

```json
{
  "user_id": "demo-user",
  "latitude": 37.2822,
  "longitude": 127.0437,
  "purchase_amount": 10000
}
```

응답 예시는 다음과 같습니다.

```json
{
  "request_id": "uuid",
  "session_id": "recommendation-uuid",
  "agent_name": "coupon_kock_agent",
  "model": "gemini-2.5-flash",
  "answer": "추천 결과에 대한 한국어 설명",
  "tool_trace": [
    "match_nearby_store:called",
    "match_nearby_store:completed"
  ],
  "session_persistence": "ephemeral"
}
```

정확한 위치가 ADK 세션에 남지 않도록 각 요청은 임시 세션에서 실행되고 응답 후 삭제됩니다. Vertex AI 인증이나 모델 호출이 실패하면 `503`을 반환합니다.
