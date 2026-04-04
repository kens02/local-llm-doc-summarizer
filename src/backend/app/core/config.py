import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "doc-summarizer"
    env: str = os.getenv("APP_ENV", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    llm_model: str = os.getenv("LLM_MODEL", "llama3.1:8b")
    llm_timeout_sec: int = int(os.getenv("LLM_TIMEOUT_SEC", "120"))

    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "20"))
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "ja")
    default_summary_style: str = os.getenv("DEFAULT_SUMMARY_STYLE", "bullet")
    default_reading_time_sec: int = int(os.getenv("DEFAULT_READING_TIME_SEC", "60"))


settings = Settings()
