"""Application settings loaded from environment / .env (pydantic-settings)."""

from __future__ import annotations

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "OneForAll "
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

    GROQ_API_KEY_INVENTORY: str = ""
    groq_central_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    llm_max_iterations: int = 10
    llm_max_tokens: int = 2048

    mcp_sheets_server_name: str = "inventory-analytics"
    sheets_spreadsheet_id: str = ""
    sheets_range: str = "Sheet1!A1:H1000"
    google_application_credentials: str = ""
    mcp_tool_timeout_seconds: int = 30

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("debug", mode="before")
    @classmethod
    def _parse_debug(cls, v: object) -> object:
        """Accept common environment labels as well as normal boolean values.

        Deployment dashboards often use values such as ``production`` or
        ``release`` for DEBUG.  Those should disable debug mode rather than
        preventing the whole application from starting.
        """
        if isinstance(v, str):
            value = v.strip().lower()
            if value in {"production", "prod", "release", "false", "0", "no", "off"}:
                return False
            if value in {"development", "dev", "debug", "true", "1", "yes", "on"}:
                return True
        return v

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
