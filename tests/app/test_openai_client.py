"""Tests for app/openai_client.py."""

import pytest

from app import openai_client


@pytest.mark.asyncio
async def test_generate_chat_response_correct_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test normal operation of generate_chat_response()."""

    # ARRANGE
    class DummyResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"output": [{"content": [{"text": "Hello!"}]}]}

    async def fake_post(path, json):
        return DummyResp()

    # Patch the client's post() method
    monkeypatch.setattr(openai_client.openai_client._client, "post", fake_post)
    # ACT
    result = await openai_client.openai_client.generate_chat_response("Hi")
    # ASSERT
    assert result == "Hello!"


@pytest.mark.asyncio
async def test_generate_chat_response_missing_output_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test generate_chat_response() when 'output' key is missing in response."""

    # ARRANGE
    class DummyResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {}

    async def fake_post(path, json):
        return DummyResp()

    # Patch the client's post() method
    monkeypatch.setattr(openai_client.openai_client._client, "post", fake_post)
    # ACT
    with pytest.raises(ValueError) as err:
        await openai_client.openai_client.generate_chat_response("Hi")
    # ASSERT
    assert "No 'text' field found in chat response" in str(err.value)


#
