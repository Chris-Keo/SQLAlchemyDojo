"""
Module 03 — Lesson 3: Pydantic BaseSettings
============================================
Python 3.11 · requires: pydantic>=2.7  pydantic-settings>=2.3

BaseSettings loads configuration from:
  1. Default values in the model
  2. Environment variables
  3. .env files
  4. Secret files (e.g. Docker secrets at /run/secrets/)

It validates and types every value — no more os.environ.get("PORT", "8080").
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# 1. Basic settings
# ---------------------------------------------------------------------------
class DatabaseSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    name: str = "app"
    user: str = "postgres"
    password: SecretStr = Field(default="changeme")   # SecretStr hides in logs
    pool_size: int = Field(default=5, ge=1, le=100)
    ssl: bool = False

    model_config = SettingsConfigDict(
        env_prefix="DB_",        # reads DB_HOST, DB_PORT, DB_NAME, etc.
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def url(self) -> str:
        pwd = self.password.get_secret_value()
        return f"postgresql://{self.user}:{pwd}@{self.host}:{self.port}/{self.name}"


# ---------------------------------------------------------------------------
# 2. Composite app settings
# ---------------------------------------------------------------------------
class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    ttl: int = 300

    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=".env")


class AppSettings(BaseSettings):
    app_name: str = "MyApp"
    environment: Literal["development", "staging", "production"] = "development"
    secret_key: SecretStr = Field(default="dev-secret-key")
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_hosts(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [h.strip() for h in v.split(",")]
        return v


# ---------------------------------------------------------------------------
# 3. Settings as a singleton (common pattern)
# ---------------------------------------------------------------------------
_db_settings: DatabaseSettings | None = None
_app_settings: AppSettings | None = None


def get_db_settings() -> DatabaseSettings:
    global _db_settings
    if _db_settings is None:
        _db_settings = DatabaseSettings()
    return _db_settings


def get_app_settings() -> AppSettings:
    global _app_settings
    if _app_settings is None:
        _app_settings = AppSettings()
    return _app_settings


# ---------------------------------------------------------------------------
# 4. Settings hierarchy: defaults → env file → env vars → code override
# ---------------------------------------------------------------------------
PRIORITY_DIAGRAM = """
Priority (highest wins):
  4. Explicit keyword arguments in constructor  ← e.g. AppSettings(debug=True)
  3. Environment variables                      ← export APP_DEBUG=true
  2. .env file                                  ← APP_DEBUG=true in .env
  1. Default values                             ← debug: bool = False
"""


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Demonstrate defaults (no env vars set)
    db = DatabaseSettings()
    print("DB host:", db.host)
    print("DB URL (schema only):", db.url.split("@")[1] if "@" in db.url else db.host)
    # SecretStr hides the value in __repr__ — call .get_secret_value() only when needed

    app = AppSettings()
    print("\nApp name:", app.app_name)
    print("Environment:", app.environment)
    print("Log level:", app.log_level)

    # Override via env vars (simulate)
    os.environ["APP_ENVIRONMENT"] = "production"
    os.environ["APP_DEBUG"] = "false"
    os.environ["APP_LOG_LEVEL"] = "WARNING"

    app2 = AppSettings()
    print("\nWith env vars:")
    print("  environment:", app2.environment)
    print("  debug:", app2.debug)
    print("  log_level:", app2.log_level)

    print(PRIORITY_DIAGRAM)
