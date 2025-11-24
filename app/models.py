from pydantic import BaseModel


class InboundMessage(BaseModel):
    """Shape of messages received over WebSocket from the client."""

    text: str


class OutboundError(BaseModel):
    """Error messages returned to the client as JSON text frames."""

    error: str


class OutboundMetadata(BaseModel):
    """Optional metadata sent before the audio payload."""

    text: str
    model: str
