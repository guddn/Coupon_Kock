# GCP / Firebase 배포

사전 조건은 GCP 프로젝트, Billing, `gcloud`, Firebase CLI입니다. 기본 리전은 서울 `asia-northeast3`입니다.

## 권장 서비스

- Cloud Run: FastAPI
- Firestore Native mode: users/coupons/stores/brand_aliases/benefits/recommendation_logs
- Cloud Storage: 공공데이터와 RAG 원문 스냅샷
- Vertex AI: Gemini와 embedding
- Secret Manager: 런타임 secret
- Firebase Hosting: Flutter Web demo

실제 리소스 생성과 과금은 명시적으로 프로젝트 ID를 정한 후 수행하세요. 먼저 `.env.example`을 참고해 로컬 값을 구성하고 `deploy-backend.ps1`의 placeholder를 검토합니다.

