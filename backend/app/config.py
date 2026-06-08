"""Runtime configuration, read from the environment or a local .env file."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://tdc:tdc@localhost:5432/tdc"

    JWT_SECRET: str = "dev-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    # Access token lives one work shift (8h): a matchmaker logs in once a day and the
    # token expires overnight. With no refresh-token flow, this is the practical balance
    # between security (short theft window) and not interrupting a working day.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # 32-byte AES key (base64) for encrypting stored LLM keys. Falls back to a
    # SHA-256-derived dev key when unset — set a real one in production.
    ENCRYPTION_KEY: str = ""

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    SEED_ON_STARTUP: bool = True
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    MATCHMAKER_USERNAME: str = "priya"
    MATCHMAKER_PASSWORD: str = "priya123"
    MATCHMAKER2_USERNAME: str = "rahul"
    MATCHMAKER2_PASSWORD: str = "rahul123"

    # Optional default LLM, used only until an admin configures one in the app.
    LLM_PROVIDER: str | None = None
    LLM_API_KEY: str | None = None
    LLM_MODEL: str | None = None

    # SMTP for outgoing match emails (Mailpit in the demo).
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    MAIL_FROM: str = "matchmaker@saathiya.local"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
