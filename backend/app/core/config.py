import os
from dataclasses import dataclass


def _csv(name: str, default: str = "") -> tuple[str, ...]:
    return tuple(value.strip() for value in os.getenv(name, default).split(",") if value.strip())


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "")
    gcp_region: str = os.getenv("GCP_REGION", "asia-northeast3")
    vertex_location: str = os.getenv("VERTEX_LOCATION", "global")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    firestore_database: str = os.getenv("FIRESTORE_DATABASE", "(default)")
    storage_bucket: str = os.getenv("STORAGE_BUCKET", "")
    cors_origins: tuple[str, ...] = _csv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5000"
    )


settings = Settings()
