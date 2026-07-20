from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Diffly"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./diffly.db"

    # Set on your GitHub App/webhook config. Every incoming webhook is
    # verified against this — requests that don't match are rejected before
    # any of their content is trusted or stored.
    GITHUB_WEBHOOK_SECRET: str = "CHANGE-ME"

    # A Personal Access Token with repo scope, used to fetch diffs/file
    # content and post review comments. v1 uses a PAT (simple, works against
    # any repo you have access to) rather than a full GitHub App (which
    # needs a private key + JWT exchange) — real trade-off, documented in
    # the README: a PAT posts comments *as your account*, a GitHub App would
    # post as its own bot identity and be installable on other people's repos.
    GITHUB_TOKEN: str = ""
    GITHUB_API_URL: str = "https://api.github.com"

    # Same free-local-first pattern as Vynera: Ollama by default, Anthropic
    # as a paid upgrade path, no code changes needed to switch.
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # How many changed files to fetch full content for, as review context.
    # Capped to keep the prompt a sane size — a PR touching 80 files
    # shouldn't mean dumping 80 full files into one LLM call.
    MAX_CONTEXT_FILES: int = 8

    ALLOWED_ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
