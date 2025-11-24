import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from .models import InboundMessage, OutboundError, OutboundMetadata
from .service import generate_tts_for_prompt
from .openai_client import openai_client
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import asyncio

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    except asyncio.CancelledError:
        # Happens during reload in debugger – safe to ignore
        pass
    finally:
        print("Shutting down...")
        await openai_client.aclose()


app = FastAPI(lifespan=lifespan, title="Engineered Arts LLM → TTS WebSocket Demo")


@app.get("/health")
async def health() -> JSONResponse:
    """Lightweight health check endpoint."""
    return JSONResponse({"status": "ok"})


@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket) -> None:
    """WebSocket endpoint.

    Expected client flow:

    - Client sends JSON text frame: { "text": "Hello" }
    - Server responds with:
        1) JSON text frame (OutboundMetadata)
        2) Binary frame containing audio bytes (e.g. MP3)
    """

    await ws.accept()
    logger.info("WebSocket client connected")

    try:
        while True:
            raw = await ws.receive_text()

            # 1) Parse inbound payload
            try:
                inbound = InboundMessage.model_validate_json(raw)
            except Exception as exc:  # broad on purpose: this is an outer edge
                logger.warning("Invalid inbound payload: %s", exc)
                err = OutboundError(error=f"Invalid payload: {exc}")
                await ws.send_text(err.model_dump_json())
                continue

            # 2) Orchestrate LLM + TTS
            try:
                llm_text, audio_bytes = await generate_tts_for_prompt(inbound.text)
            except Exception as exc:  # don't leak internals to client
                logger.exception("Error while generating TTS")
                err = OutboundError(error="Internal error while generating audio.")
                await ws.send_text(err.model_dump_json())
                continue

            # 3) Send metadata then audio
            metadata = OutboundMetadata(text=llm_text, model="chat+tts")
            await ws.send_text(metadata.model_dump_json())
            await ws.send_bytes(audio_bytes)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
        return
