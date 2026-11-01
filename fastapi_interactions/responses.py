"""Interaction response objects returned by command handlers.

Each response serializes itself into the callback payload Discord expects. The
bot converts returned strings into :class:`MessageResponse` instances and wraps
responses in a JSON HTTP response.
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import InitVar, dataclass, field
from typing import Any

from fastapi.responses import JSONResponse

from .models import (
    InteractionCallbackType,
    MessageFlags,
)


class _JSONResponse(JSONResponse):
    """A JSON response that serializes :class:`InteractionResponse` objects."""

    def render(self, content: Any) -> bytes:
        if isinstance(content, InteractionResponse):
            content = content.to_dict()
        return super().render(content)


class InteractionResponse(ABC):
    """Base class for all interaction callback responses."""

    @abstractmethod
    def to_dict(self):
        """Return the Discord callback payload for this response."""
        pass

    async def __call__(self) -> dict:
        return self.to_dict()


class PongResponse(InteractionResponse):
    """Acknowledge a PING interaction.

    The bot sends this automatically when Discord verifies the interactions
    endpoint, so handlers normally never need to create it.
    """

    callback_type = InteractionCallbackType.PONG

    def to_dict(self):
        return {"type": self.callback_type}


@dataclass(slots=True)
class MessageResponse(InteractionResponse):
    """Send a message in the interaction's channel.

    Args:
        content: The message text.
        ephemeral: Whether only the invoking user can see the message.
            Defaults to ``False``.
    """

    callback_type = InteractionCallbackType.MESSAGE
    content: str
    ephemeral: InitVar[bool] = False
    flags: MessageFlags = field(init=False)

    def __post_init__(self, ephemeral: bool):
        self.flags = MessageFlags.EPHEMERAL if ephemeral else MessageFlags(0)

    def to_payload(self):
        return {"content": self.content, "flags": int(self.flags)}

    def to_dict(self):
        return {"type": self.callback_type, "data": self.to_payload()}


@dataclass(slots=True)
class DeferResponse(InteractionResponse):
    """Acknowledge an interaction now and deliver the real response later.

    The bot sends the defer acknowledgement before running ``finish`` as a
    background task. Use :meth:`fastapi_interactions.context.Context.send`
    inside ``finish`` to deliver followup messages.

    Args:
        ephemeral: Whether followup messages should be ephemeral. Defaults to
            ``False``.
        finish: Optional callback run in the background after the defer is sent.
    """

    callback_type = InteractionCallbackType.DEFER
    ephemeral: InitVar[bool] = False
    finish: Callable | None = field(default=None, repr=None, compare=None)
    flags: MessageFlags = field(init=False)

    def __post_init__(self, ephemeral: bool):
        self.flags = MessageFlags.EPHEMERAL if ephemeral else MessageFlags(0)

    def to_dict(self):
        return {"type": self.callback_type, "data": {"flags": int(self.flags)}}
