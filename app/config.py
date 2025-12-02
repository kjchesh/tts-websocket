from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables.

    Expected:
      - OPENAI_API_KEY: API key with access to Chat Completions + TTS.
      - Optional overrides for model names / voice / format.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    openai_api_key: str

    # Defaults can be overridden via environment variables:
    openai_base_url: str = "https://api.openai.com/v1"

    chat_model: str = "gpt-4.1"
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "alloy"
    tts_format: str = "mp3"


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return singleton Settings instance, failing fast if misconfigured."""
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg] # pyright: ignore
    return _settings
