from dataclasses import dataclass
from abc import ABC, abstractmethod
from .models import MessageFlags


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
