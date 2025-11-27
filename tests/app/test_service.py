"""Tests for app/service.py."""

import pytest

from app import service


class DummyClient:
    async def generate_chat_response(self, user_text: str) -> str | None:
        return f"Echo: {user_text}"

    async def synthesize_speech(self, text: str) -> bytes | None:
        return b"FAKE-AUDIO-BYTES"


@pytest.mark.asyncio
async def test_generate_tts_for_prompt(monkeypatch):
    # Patch the openai_client used inside the service module
    monkeypatch.setattr(service, "openai_client", DummyClient())

    text, audio = await service.generate_tts_for_prompt("hello")
    assert text == "Echo: hello"
    assert audio == b"FAKE-AUDIO-BYTES"
