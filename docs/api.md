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

## `POST /api/recommendations`

```json
{
  "user_id": "demo-user",
  "latitude": 37.5665,
  "longitude": 126.978,
  "purchase_amount": 10000,
  "store_id": "demo-store"
}
```

응답은 매장, 정렬된 후보, 추천 옵션, 확인이 필요한 조건과 공식 출처를 반환합니다. 개발용 scaffold에서는 고정 fixture를 사용하며 production adapter가 Firestore/RAG 결과를 주입하도록 경계를 분리했습니다.

