param(
    [Parameter(Mandatory = $true)][string]$ProjectId,
    [string]$Region = "asia-northeast3",
    [string]$ServiceName = "coupon-knock-api"
)

$ErrorActionPreference = "Stop"

gcloud run deploy $ServiceName `
    --project $ProjectId `
    --region $Region `
    --source "../../backend" `
    --platform managed `
    --no-allow-unauthenticated `
    --set-env-vars "GCP_PROJECT_ID=$ProjectId,GCP_REGION=$Region,APP_ENV=production"

