"""Application configuration for AL-KHALLAQI."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=True, extra="ignore",
    )

    APP_NAME: str = "AL-KHALLAQI"
    APP_NAME_AR: str = "الخلاقي"
    APP_VERSION: str = "1.0.0"
    DEVELOPER: str = "Hussein Ghallab"
    SLOGAN: str = "الإبداع بلا حدود"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    GEMINI_API_KEY: str = ""
    GEMINI_API_KEY_FALLBACK: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-flash"
    DEEPSEEK_THINKING: str = "enabled"
    DEEPSEEK_REASONING_EFFORT: str = "high"

    GITHUB_ACTIONS_TOKEN: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    ADMIN_PASSWORD: str = "hussein2026"

    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"

    MAX_AGENT_STEPS: int = 8
    REQUEST_TIMEOUT: int = 90

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL or "sqlite+aiosqlite:///./al_khallaqi.db"
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
