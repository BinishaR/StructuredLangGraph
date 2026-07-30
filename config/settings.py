# config/settings.py
"""
Centralized application configuration.

All environment variables are read here ONCE and exposed via the `settings`
object. No other file should call os.getenv() directly — import `settings`
from this module instead.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- OpenAI / LLM ---
    openai_api_key: str
    openai_model: str = "gpt-5.4-mini"

    # --- Chroma vector store ---
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "bank_faqs"
    retriever_k: int = 4

    # --- API metadata ---
    api_title: str = "Laxmi Sunrise Bank Assistant"
    
    update_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()