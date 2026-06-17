from dataclasses import dataclass, field
from typing import List
from enum import IntEnum, IntFlag

@dataclass
class Option:
    name: str
    description: str
    type: int = 3
    required: bool = True

    def as_payload(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "required": self.required
        }

@dataclass(slots=True)
class CommandMeta:
    name: str
    description: str
    options: list[Option] = field(default_factory=list) 
    type: int = 1

    def as_payload(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "options": [
                option.as_payload() for option in self.options
            ]
        }

@dataclass
class Command:
    callback: callable
    meta: CommandMeta

class InteractionType(IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5

class MessageFlags(IntFlag):
    EPHEMERAL = 1 << 6