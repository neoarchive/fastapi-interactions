from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any
from enum import IntEnum, IntFlag

Snowflake = str


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


class DiscordModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class User(DiscordModel):
    id: Snowflake
    username: str
    descriminator: Optional[str] = None
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

    @property
    def options_by_name(self) -> dict[str, "CommandInteractionOption"]:
        return {opt.name for opt in self.options}

    def get_option_value(self, name: str, default: Any = None) -> Any:
        option = self.options_by_name.get(name)
        return option.value if option is not None else default


CommandInteractionOption.model_rebuild()


class ApplicationCommandData(DiscordModel):
    id: Snowflake
    name: str
    type: int
    guild_id: Optional[Snowflake] = None
    target_id: Optional[Snowflake] = None
    options: list[CommandInteractionOption] = Field(default_factory=list)

    @property
    def options_by_name(self) -> dict[str, "CommandInteractionOption"]:
        return {opt.name: opt for opt in self.options}

    def get_option_value(self, name: str, default: Any = None) -> Any:
        option = self.options_by_name.get(name)
        return option.value if option is not None else default


class Interaction(DiscordModel):
    id: Snowflake
    application_id: Snowflake
    type: InteractionType
    token: str
    version: int

    data: Optional[dict[str, Any]] = None

    guild_id: Optional[Snowflake] = None
    channel_id: Optional[Snowflake] = None
    member: Optional[Member] = None
    user: Optional[User] = None
    locale: Optional[str] = None
    guild_locale: Optional[str] = None


@dataclass
class Context:
    interaction: Interaction
    options: ApplicationCommandData

    @property
    def user(self) -> User:
        if self.interaction.user is not None:
            return self.interaction.user
        if (
            self.interaction.member is not None
            and self.interaction.member.user is not None
        ):
            return self.interaction.member.user
        raise ValueError("Interaction does not contain `user` or `member.user`")

    @property
    def guild_id(self) -> Optional[Snowflake]:
        return self.interaction.guild_id

    @property
    def channel_id(self) -> Optional[Snowflake]:
        return self.interaction.channel_id

    def get_option_value(self, name: str, default: Any = None) -> Any:
        option = self.options.options_by_name.get(name)
        return option.value if option is not None else default
