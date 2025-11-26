from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables.

    Expected:
      - OPENAI_API_KEY: API key with access to Chat Completions + TTS.
      - Optional overrides for model names / voice / format.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str

    # Defaults can be overridden via environment variables:
    openai_base_url: str = "https://api.openai.com/v1"
    # TODO: which model is best for chat responses?
    chat_model: str = "gpt-4.1"  # "gpt-4o-mini"
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "alloy"
    tts_format: str = "mp3"  # e.g. mp3, wav


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return singleton Settings instance, failing fast if misconfigured."""
    global _settings
    if _settings is None:
        _settings = Settings()  # pyright: ignore
    return _settings
