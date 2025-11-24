"""Orchestration logic: text → LLM → TTS audio."""

from .openai_client import openai_client


async def generate_tts_for_prompt(user_text: str) -> tuple[str, bytes]:
    """High-level service function.

    1. Send user_text to LLM.
    2. Send LLM response to TTS.
    3. Return (llm_text, audio_bytes).
    """

    llm_text = await openai_client.generate_chat_response(user_text)
    audio_bytes = await openai_client.synthesize_speech(llm_text)
    return llm_text, audio_bytes
