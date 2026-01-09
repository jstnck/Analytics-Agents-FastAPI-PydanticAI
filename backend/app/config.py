from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App settings
    app_name: str = "Analytics Agent API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    duckdb_path: str = "../data/analytics.duckdb"

    # LLM settings
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    default_llm_model: str = "anthropic:claude-sonnet-4-5-20250929"

    # Agent timeouts (seconds)
    sql_agent_timeout_seconds: int = 30
    orchestrator_timeout_seconds: int = 45

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]


settings = Settings()
