from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import IntFlag
import asyncio
from enum import IntEnum


class InteractionCallbackType(IntEnum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9
    PREMIUM_REQUIRED = 10
    LAUNCH_ACTIVITY = 12

    """
    redefigning for ease of life
    aliases arent used because type checkers are annoying
    """
    # MESSAGE = 4
    # DEFER = 5
    # UPDATE = 7
    # AUTOCOMPLETE = 8
    MESSAGE = CHANNEL_MESSAGE_WITH_SOURCE
    DEFER = DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
    UPDATE = UPDATE_MESSAGE
    AUTOCOMPLETE = APPLICATION_COMMAND_AUTOCOMPLETE_RESULT


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
    callback_type: InteractionCallbackType.MESSAGE
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
