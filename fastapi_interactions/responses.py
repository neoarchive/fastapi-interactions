from dataclasses import dataclass
from abc import ABC, abstractmethod
from .models import (
    InteractionCallbackType,
    MessageFlags,
)
import asyncio


class InteractionResponse(ABC):

    @abstractmethod
    def to_dict(self):
        pass

    async def __call__(self) -> dict:
        return self.to_dict()

    def __await__(self):
        return self.__call__().__await__()


class PongResponse(InteractionResponse):
    callback_type = InteractionCallbackType.PONG

    def to_dict(self):
        return {
            'type': self.callback_type
        }


@dataclass(slots=True)
class MessageResponse(InteractionResponse):
    callback_type = InteractionCallbackType.MESSAGE
    content: str
    ephemeral: bool = False

    def __init__(self, content: str, ephemeral: bool = False):
        self.content = content
        self.flags = MessageFlags.EPHEMERAL if ephemeral else MessageFlags(0)

    def to_payload(self):
        return {
            'content': self.content,
            'flags': int(self.flags)
        }

    def to_dict(self):
        return {
            "type": self.callback_type,
            "data": self.to_payload()
        }


@dataclass(slots=True)
class DeferResponse(InteractionResponse):
    callback_type = InteractionCallbackType.DEFER

    def __init__(self, ephemeral: bool = False, finish: callable = None):
        self.flags = MessageFlags.EPHEMERAL if ephemeral else MessageFlags(0)
        self.finish = finish

    def to_dict(self):
        return {
            "type": self.callback_type,
            "data": {"flags": int(self.flags)}
        }

    async def __call__(self):
        if self.finish:
            asyncio.create_task(self.finish())
        return self.to_dict()
