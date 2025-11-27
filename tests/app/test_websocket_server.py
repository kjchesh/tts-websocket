import json

from fastapi.testclient import TestClient

import app.websocket_server as main

client = TestClient(main.app)


async def _fake_generate_tts_for_prompt(prompt: str):
    assert prompt == "Hello"
    return "LLM reply", b"\x00\x01\x02"  # fake audio


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_websocket_happy_path(monkeypatch):
    # Patch the internal reference used inside websocket_chat
    monkeypatch.setattr(main, "generate_tts_for_prompt", _fake_generate_tts_for_prompt)

    with client.websocket_connect("/ws/chat") as ws:
        ws.send_text(json.dumps({"text": "Hello"}))

        # 1) metadata JSON frame
        raw_meta = ws.receive_text()
        meta = json.loads(raw_meta)
        assert set(meta.keys()) == {"text", "model"}
        assert meta["text"] == "LLM reply"
        assert meta["model"] == "chat+tts"

        # 2) audio bytes frame
        audio = ws.receive_bytes()
        assert audio == b"\x00\x01\x02"


def test_websocket_invalid_json(monkeypatch):
    # ensure TTS is never called
    async def _sentinel(*args, **kwargs):
        raise AssertionError("generate_tts_for_prompt should NOT be called")

    monkeypatch.setattr(main, "generate_tts_for_prompt", _sentinel)

    with client.websocket_connect("/ws/chat") as ws:
        ws.send_text("not-json")

        raw_err = ws.receive_text()
        err = json.loads(raw_err)

        assert set(err.keys()) == {"error"}
        assert "Invalid payload" in err["error"]


def test_websocket_invalid_shape(monkeypatch):
    async def _sentinel(*args, **kwargs):
        raise AssertionError("generate_tts_for_prompt should NOT be called")

    monkeypatch.setattr(main, "generate_tts_for_prompt", _sentinel)

    with client.websocket_connect("/ws/chat") as ws:
        ws.send_text(json.dumps({"foo": "bar"}))  # missing "text"

        raw_err = ws.receive_text()
        err = json.loads(raw_err)

        assert set(err.keys()) == {"error"}
        assert "Invalid payload" in err["error"]


def test_websocket_internal_error(monkeypatch):
    async def _boom(prompt: str):
        raise RuntimeError("Boom!")

    monkeypatch.setattr(main, "generate_tts_for_prompt", _boom)

    with client.websocket_connect("/ws/chat") as ws:
        ws.send_text(json.dumps({"text": "Hello"}))

        raw_err = ws.receive_text()
        err = json.loads(raw_err)

        assert set(err.keys()) == {"error"}
        assert err["error"] == "Internal error while generating audio."
