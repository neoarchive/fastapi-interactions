from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import IntFlag


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

    def to_dict(self):
        data = {"content": self.content}

        if self.ephemeral:
            data["flags"] = MessageFlags.EPHEMERAL

        return {"type": 4, "data": data}


@dataclass(slots=True)
class DeferResponse(InteractionResponse):
    ephemeral: bool = False

    def to_dict(self):

        payload = {"type": 5}

        if self.ephemeral:
            payload["data"] = {"flags": MessageFlags.EPHEMERAL}

        return payload
