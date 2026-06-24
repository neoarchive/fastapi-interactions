from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import IntFlag
import asyncio


class MessageFlags(IntFlag):
    """Bit flags describing special message properties."""

    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPPRESS_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4
    HAS_THREAD = 1 << 5
    EPHEMERAL = 1 << 6
    LOADING = 1 << 7
    FAILED_TO_MENTION_SOME_ROLES_IN_THREAD = 1 << 8

    SUPPRESS_NOTIFICATIONS = 1 << 12
    IS_VOICE_MESSAGE = 1 << 13
    HAS_SNAPSHOT = 1 << 14
    IS_COMPONENTS_V2 = 1 << 15


class InteractionResponse(ABC):

    @abstractmethod
    def to_dict(self):
        pass


@dataclass(slots=True)
class MessageResponse(InteractionResponse):
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
        return {"type": 4, "data": self.to_payload()}

    async def __call__(self):
        return self.to_dict()


@dataclass(slots=True)
class DeferResponse(InteractionResponse):
    ephemeral: bool = False

    def __init__(self, ephemeral: bool = False, finish: callable = None):
        self.flags = MessageFlags.EPHEMERAL if ephemeral else MessageFlags(0)
        self.finish = finish

    def to_dict(self):
        return {
            "type": 5,
            "data": {"flags": int(self.flags)}
        }

    async def __call__(self):
        if self.finish:
            asyncio.create_task(self.finish())
        return self.to_dict()
