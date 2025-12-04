# LLM → TTS WebSocket Demo (Engineered Arts Take‑Home)

This repository implements a small WebSocket service that:

1. Receives text from a client over WebSocket.
2. Sends the text to an OpenAI Chat model.
3. Sends the Chat response text to an OpenAI Text‑to‑Speech (TTS) model.
4. Returns the synthesized audio bytes to the client over the same WebSocket connection.

## Project Structure

```text
app/
  __init__.py
  config.py           # Settings and OpenAI configuration
  models.py           # Pydantic models for WS messages
  openai_client.py    # Async HTTP client for Chat + TTS
  service.py          # Text → LLM → TTS orchestration
  websocket_server.py # FastAPI + WebSocket endpoint

client/
  simple_client.py    # Tiny Python WebSocket client

tests/                # Unit tests

MakeFile
requirements.txt
pyproject.toml
README.md
```

## Prerequisites

- Python 3.11+ (recommended)
- An OpenAI API key with access to **Chat Responses** and **TTS** endpoints.

## 🚀 Installation

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
.venv\Scripts\activate
# install dependencies using pyproject.toml
pip install .

Set the environment variable for your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-..."   # macOS / Linux
# or on Windows (PowerShell):
# $env:OPENAI_API_KEY="sk-..."
```

You can optionally override the default models / voice / format:

```bash
export OPENAI_CHAT_MODEL="gpt-4.1"
export OPENAI_TTS_MODEL="gpt-4o-mini-tts"
export OPENAI_TTS_VOICE="alloy"
export OPENAI_TTS_FORMAT="mp3"
```

## Running the Server

From the project root (with the virtual environment activated):

```bash
uvicorn app.websocket_server:app --reload
```

Or running via MakeFile

    make dev


This starts the FastAPI app on `http://127.0.0.1:8000` by default.

- Health check: `GET /health`
- WebSocket endpoint: `ws://127.0.0.1:8000/ws/chat`

## Testing the WebSocket (Python Client)

With the server running, in another terminal:

```bash
source .venv/bin/activate
python client/simple_client.py "Hello robot"
```

The client will:

1. Connect to `ws://localhost:8000/ws/chat`.
2. Send a JSON message: `{"text": "Hello robot"}`.
3. Print the metadata frame received from the server.
4. Write the audio frame to `out.mp3` in the project root.

You can then play `out.mp3` with any standard media player.

## Running tests from terminal (Requires dev install)

    python -m pytest

Or running via MakeFile

    make test

## Optional Developer Tooling (Requires dev install)

This project includes optional pre-commit hooks for Black, Ruff, and isort.
These are not required to run or review the project.

To enable them locally:

    pip install pre-commit
    pre-commit install

This will run formatting and linting automatically on each commit.

Optional: See MakeFile for other useful commands.


