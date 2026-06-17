from dataclasses import dataclass
from abc import ABC, abstractmethod


class InteractionResponse(ABC):

    @abstractmethod
    def to_dict(self):
        pass

    
@dataclass(slots=True)
class MessageResponse(InteractionResponse):
    content: str 
    ephemeral: bool = False

    def to_dict(self):
        data = {
            'content': self.content
        }

        if self.ephemeral:
            data['flags'] = 64

        return {
            'type': 4,
            'data': data
        }