"""Application settings loaded from environment / .env (pydantic-settings)."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "OneForAll"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""

    database_url: str = ""

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    llm_max_iterations: int = 5
    llm_max_tokens: int = 2048

    mcp_sheets_server_name: str = "gsheets"
    sheets_spreadsheet_id: str = ""
    sheets_range: str = "Inventory!A1:H1000"
    mcp_tool_timeout_seconds: int = 30

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [origin.strip() for origin in v.strip("[]").split(",") if origin.strip()]
        return v

    @property
    def db_dsn(self) -> str:
        """SQLAlchemy async DSN: DATABASE_URL, else SUPABASE_URL (Postgres DSN)."""
        dsn = self.database_url or self.supabase_url
        if not dsn:
            return "sqlite+aiosqlite:///:memory:"
        if dsn.startswith("postgres://"):
            dsn = dsn.replace("postgres://", "postgresql+asyncpg://", 1)
        elif dsn.startswith("postgresql://"):
            dsn = dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
        return dsn

    @property
    def supabase_rest_url(self) -> str:
        """REST project URL for the supabase-py client, derived from the DSN host."""
        if self.supabase_url.startswith("postgres") and "@" in self.supabase_url:
            host = self.supabase_url.split("@", 1)[1].split(":", 1)[0]
            return f"https://{host}"
        return self.supabase_url


settings = Settings()
