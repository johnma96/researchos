"""Centralized configuration — single source of truth for all settings.

Usage:
    from researchos.config import settings
    client = Anthropic(api_key=settings.anthropic_api_key)
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Environment ──
    environment: Literal["development", "staging", "production"] = "development"

    # ── LLM ──
    anthropic_api_key: str = ""
    default_model: str = "claude-sonnet-4-20250514"
    fast_model: str = "claude-haiku-4-5-20251001"
    temperature: float = 0.5
    max_tokens: int = 1024

    # ── Vector store ──
    vector_store: Literal["chroma", "vertex"] = "chroma"
    chroma_persist_dir: str = "data/chroma"

    # ── Memory ──
    memory_store: Literal["in_memory", "sqlite"] = "in_memory"
    sqlite_db_path: str = "data/memory.db"

    # ── Embeddings ──
    embedding_model: str = "all-MiniLM-L6-v2"

    # ── Telegram ──
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # ── API ──
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ── News (V2) ──
    newsapi_key: str = ""

    # ── Monitoring (V3) ──
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://localhost:3000"

    # ── GCP (V4) ──
    google_cloud_project: str = ""

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent


settings = Settings()
