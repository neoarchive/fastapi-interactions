from dataclasses import dataclass, field
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from enum import IntEnum, IntFlag


Snowflake = str


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
            "required": self.required,
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
            "options": [option.as_payload() for option in self.options],
        }


@dataclass(slots=True)
class Command:
    callback: callable
    meta: CommandMeta


class InteractionType(IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class ApplicationCommandOptionType(IntEnum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10
    ATTACHMENT = 11


class MessageFlags(IntFlag):
    EPHEMERAL = 1 << 6


class DiscordModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class User(DiscordModel):
    id: Snowflake
    username: str
    descriminator: str
    global_name: Optional[str] = None
    avatar: Optional[str] = None
    bot: Optional[bool] = None


class Member(DiscordModel):
    user: Optional[User] = None
    nick: Optional[str] = None
    roles: list[Snowflake] = Field(default_factory=list)
    permissions: Optional[str] = None


class CommandInteractionOption(DiscordModel):
    name: str
    type: ApplicationCommandOptionType
    value: Optional[str | int | float | bool] = None
    options: list["CommandInteractionOption"] = Field(default_factory=list)
    focused: Optional[bool] = None


CommandInteractionOption.model_rebuild()


class ApplicationCommandData(DiscordModel):
    id: Snowflake
    name: str
    type: int
    guild_id: Optional[Snowflake] = None
    target_id: Optional[Snowflake] = None
    options: list[CommandInteractionOption] = Field(default_factory=list)