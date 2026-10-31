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

    def render(self, content: Any) -> bytes:
        if isinstance(content, InteractionResponse):
            content = content.to_dict()
        return super().render(content)


class InteractionResponse(ABC):

    @abstractmethod
    def to_dict(self):
        pass

    async def __call__(self) -> dict:
        return self.to_dict()


class PongResponse(InteractionResponse):
    callback_type = InteractionCallbackType.PONG

    def to_dict(self):
        return {"type": self.callback_type}


@dataclass(slots=True)
class MessageResponse(InteractionResponse):
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
    callback_type = InteractionCallbackType.DEFER
    ephemeral: InitVar[bool] = False
    finish: Callable | None = field(default=None, repr=None, compare=None)
    flags: MessageFlags = field(init=False)

    def __post_init__(self, ephemeral: bool):
        self.flags = MessageFlags.EPHEMERAL if ephemeral else MessageFlags(0)

    def to_dict(self):
        return {"type": self.callback_type, "data": {"flags": int(self.flags)}}
