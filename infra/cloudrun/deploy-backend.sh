#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:?Usage: deploy-backend.sh PROJECT_ID [REGION] [SERVICE_NAME]}"
REGION="${2:-asia-northeast3}"
SERVICE_NAME="${3:-coupon-kock-api}"

gcloud run deploy "$SERVICE_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --source "../../backend" \
  --platform managed \
  --no-allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION,APP_ENV=production"
