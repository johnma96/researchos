"""Centralized configuration — single source of truth for all settings.

Usage:
    from researchos.config import settings
    client = Anthropic(api_key=settings.anthropic_api_key)
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env and environment variables.

    All fields are populated from the ``.env`` file at the project root or
    from environment variables (case-insensitive).  Each section maps to a
    specific external service or runtime concern:

    - **Environment:** controls the execution mode (development / staging / production).
    - **LLM:** Anthropic credentials and generation parameters.
    - **Vector store:** backend selection (Chroma | Vertex) and persistence path.
    - **Memory:** conversation history backend (in-memory | SQLite).
    - **Embeddings:** sentence-transformer model used for embedding.
    - **Telegram:** bot token and target chat for morning briefings.
    - **API:** host and port for the FastAPI server.
    - **News (V2):** NewsAPI key for RSS / news sources.
    - **Monitoring (V3):** Langfuse credentials for LLM observability.
    - **GCP (V4):** Google Cloud project for Vertex AI and BigQuery.

    Example:
        >>> from researchos.config import settings
        >>> print(settings.default_model)
        claude-haiku-4-5-20251001
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Environment ──
    environment: Literal["development", "staging", "production"] = "development"

    # ── LLM ──
    anthropic_api_key: str = ""
    default_model: str = "claude-haiku-4-5-20251001"
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
    # Set to an absolute local path to load the model from disk (no HuggingFace needed).
    embedding_model_local_path: str = ""

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
        """Absolute path to the repository root.

        Computed by walking three levels up from this file
        (``src/researchos/config.py`` → ``src/researchos/`` → ``src/`` → root).

        Returns:
            Path: Absolute ``Path`` object pointing to the project root directory.
        """
        return Path(__file__).resolve().parent.parent.parent


settings = Settings()
