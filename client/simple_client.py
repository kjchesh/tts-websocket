"""Very small Python WebSocket client to exercise the service.

Usage (in another terminal, with the server running):

    python client/simple_client.py "Hello from my test client"
"""

import asyncio
import json
import sys

import websockets


async def main() -> None:
    uri = "ws://localhost:8000/ws/chat"
    text = "Hello from the simple client"
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"text": text}))

        # Expect metadata first
        meta = await ws.recv()
        print("Received metadata frame:")
        print(meta)

        # Then expect audio as binary frame
        audio = await ws.recv()
        if isinstance(audio, str):
            print("Expected binary audio but received text frame instead.")
            print(audio)
            return

        out_path = "out.mp3"
        with open(out_path, "wb") as f:
            f.write(audio)

        print(f"Wrote audio response to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
