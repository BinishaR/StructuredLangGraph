from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-5.4-mini"

    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "bank_faqs"
    retriever_k: int = 4

    api_title: str = "Laxmi Sunrise Bank Assistant"
    update_api_key: str

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_ttl_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

settings = Settings()