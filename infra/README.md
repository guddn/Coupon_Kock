# GCP / Firebase 배포

사전 조건은 GCP 프로젝트, Billing, `gcloud`, Firebase CLI입니다. 기본 리전은 서울 `asia-northeast3`입니다.

## 권장 서비스

- Cloud Run: FastAPI
- Firestore Native mode: users/coupons/stores/brand_aliases/benefits/recommendation_logs
- Cloud Storage: 공공데이터와 RAG 원문 스냅샷
- Vertex AI: Gemini와 embedding
- Secret Manager: 런타임 secret
- Firebase Hosting: Flutter Web demo

실제 리소스 생성과 과금은 명시적으로 프로젝트 ID를 정한 후 수행하세요. 먼저 `.env.example`을 참고해 로컬 값을 구성하고 `infra/cloudrun/deploy-backend.sh`의 인자를 확인합니다.

## ADK / Vertex AI 인증

로컬 실행에서는 먼저 Application Default Credentials를 준비합니다.

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

Cloud Run에서는 서비스에 연결된 런타임 서비스 계정에 `Vertex AI 사용자` 역할이 필요합니다.

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_CLOUD_RUN_SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```

ADK 확인 엔드포인트는 `GET /api/agent`, 실행 엔드포인트는 `POST /api/agent/recommendations`입니다.
