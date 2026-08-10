# 4일 MVP 구현 순서

## Day 1 - 위험 우선 검증

- 저장소/환경 구성
- 상가 CSV 샘플 전처리, nearby store, Brand Resolver spike
- 대표 혜택 규칙과 calculator fixture 작성

## Day 2 - AI와 Backend

- coupon parser JSON schema와 Vertex AI adapter
- RAG 문서 정제/embedding/vector index
- `/health`, `/api/coupons/parse`, `/api/recommendations`

## Day 3 - Flutter 연결

- Android ML Kit OCR와 민감 문자열 마스킹
- 쿠폰 등록/목록, 위치 또는 매장 프리셋
- 추천 카드, 대안, 공식 출처 상세

## Day 4 - 배포와 검증

- Cloud Run/Firebase Hosting 배포
- TC-01~TC-05, 계산 fixture 20개, RAG 질문 5개
- 응답 시간과 3~5명 사용자 과업 테스트
- 기획서에 실제 URL, 결과, 화면, commit hash 반영

