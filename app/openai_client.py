import httpx
from .config import get_settings

settings = get_settings()


class OpenAIClient:
    """Thin async wrapper around OpenAI's Chat + TTS HTTP APIs."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.openai_base_url,
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
            },
            timeout=30.0,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def generate_chat_completion(self, user_text: str) -> str:
        """Call OpenAI Chat Completions API and return assistant text."""

        payload = {
            "model": settings.chat_model,
            "messages": [
                {"role": "system", "content": "You are a concise, friendly assistant."},
                {"role": "user", "content": user_text},
            ],
        }

        resp = await self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def generate_chat_response(self, user_text: str) -> str:
        """Call Chat Responses API and return assistant text."""

        payload = {
            "model": settings.chat_model,
            "input": user_text,
        }

        resp = await self._client.post("/responses", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["output"][0]["content"][0].get("text")

    async def synthesize_speech(self, text: str) -> bytes:
        """Call OpenAI TTS API and return raw audio bytes."""

        payload = {
            "model": settings.tts_model,
            "input": text,
            "voice": settings.tts_voice,
            "format": settings.tts_format,
        }

        resp = await self._client.post("/audio/speech", json=payload)
        resp.raise_for_status()
        return resp.content


# Simple global client for this small demo application.
openai_client = OpenAIClient()
