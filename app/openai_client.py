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

    async def generate_chat_response(self, user_text: str) -> str | ValueError:
        """Call Chat Responses API and return assistant text."""

        payload = {
            "model": settings.chat_model,
            "input": user_text,
        }

        resp = await self._client.post("/responses", json=payload)
        resp.raise_for_status()
        data = resp.json()

        content = (data.get("output") or [{}])[0].get("content", [{}])[0]

        if content.get("text") is None:
            raise ValueError("No 'text' field found in chat response")

        return content.get("text")

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

        content_type = resp.headers.get("content-type", "")
        if not content_type.startswith("audio/"):
            raise ValueError(f"Unexpected content type: {content_type}")

        if not resp.content:
            raise ValueError("Received empty audio content from TTS API.")

        return resp.content


# Simple global client for this small demo application.
openai_client = OpenAIClient()
