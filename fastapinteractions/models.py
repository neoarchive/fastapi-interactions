from dataclasses import dataclass, field
from typing import List

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
    options: list = field(default_factory=list) 
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

