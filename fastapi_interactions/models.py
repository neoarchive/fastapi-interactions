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


class CommandType(IntEnum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3
    PRIMARY_ENTRY_POINT = 4

    CHAT = 1
    ENTRY = 4


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


class ApplicationCommandInteractionOption(DiscordModel):
    name: str
    type: ApplicationCommandOptionType
    value: Optional[str | int | float | bool] = None
    options: list["ApplicationCommandInteractionOption"] = Field(default_factory=list)
    focused: Optional[bool] = None

    @property
    def options_by_name(self) -> dict[str, "ApplicationCommandInteractionOption"]:
        return {opt.name for opt in self.options}

    def get_option_value(self, name: str, default: Any = None) -> Any:
        option = self.options_by_name.get(name)
        return option.value if option is not None else default


ApplicationCommandInteractionOption.model_rebuild()


class ApplicationCommandData(DiscordModel):
    id: Snowflake
    name: str
    type: CommandType
    guild_id: Optional[Snowflake] = None
    target_id: Optional[Snowflake] = None
    options: list[ApplicationCommandInteractionOption] = Field(default_factory=list)

    @property
    def options_by_name(self) -> dict[str, "ApplicationCommandInteractionOption"]:
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
