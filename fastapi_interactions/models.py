"""Enums and Pydantic models for Discord interaction payloads.

This module mirrors the parts of Discord's interaction and application command
objects that the framework needs. Enums use the same integer values Discord sends
and expects, while Pydantic models parse incoming payloads with unknown fields
ignored.
"""

from enum import IntEnum, IntFlag
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

Snowflake = str


class _ApiFlag(IntFlag):
    """Base class for flags that are serialized as Discord's integer lists.

    Each flag value is a bit position rather than the API integer itself. For
    example, the first flag in a subclass is ``1 << 0`` and is sent to Discord
    as ``0``. Use :meth:`to_api` to convert a combination of flags into the
    list of integers Discord expects.
    """

    def to_api(self) -> list[int]:
        """Bit positions set in this flag, e.g. GUILD|PRIVATE_CHANNEL -> [0, 2]."""
        return [i for i in range(self.bit_length()) if self & (1 << i)]


class IntegrationType(_ApiFlag):
    """Where a command can be installed and used.

    Discord calls these *integration types*. Combine values with ``|`` when a
    command should support more than one installation surface, or use
    :attr:`ALL` as a shorthand. The selected flags are serialized to the
    ``integration_types`` field when commands are registered.

    Attributes:
        GUILD_INSTALL: The command can be installed on a guild (API value ``0``).
        USER_INSTALL: The command can be installed on a user account (API value ``1``).
        ALL: Both guild and user installation (API values ``[0, 1]``).
    """

    GUILD_INSTALL = 1 << 0  # API VALUE 0
    USER_INSTALL = 1 << 1  # API VALUE 1
    ALL = GUILD_INSTALL | USER_INSTALL


class InteractionContext(_ApiFlag):
    """Where an application command can be invoked.

    Combine values with ``|`` to allow a command in several places, or use
    :attr:`ALL` as a shorthand. The selected flags are serialized to the
    ``contexts`` field when commands are registered.

    Attributes:
        GUILD: Usable in guild channels (API value ``0``).
        BOT_DM: Usable in direct messages with the bot (API value ``1``).
        PRIVATE_CHANNEL: Usable in private channels such as group DMs (API value ``2``).
        ALL: Usable in every supported context (API values ``[0, 1, 2]``).
    """

    GUILD = 1 << 0  # API VALUE 0
    BOT_DM = 1 << 1  # API VALUE 1
    PRIVATE_CHANNEL = 1 << 2  # VALUE VALUE 2
    ALL = GUILD | BOT_DM | PRIVATE_CHANNEL


class InteractionType(IntEnum):
    """Type of interaction delivered to the bot's webhook endpoint.

    Attributes:
        PING: Discord's endpoint verification request.
        APPLICATION_COMMAND: A slash command invocation.
        MESSAGE_COMPONENT: A button or select menu interaction.
        APPLICATION_COMMAND_AUTOCOMPLETE: An autocomplete request for a command option.
        MODAL_SUBMIT: A submitted modal dialog.
    """

    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class CommandType(IntEnum):
    """Type of application command registered with Discord.

    Attributes:
        CHAT_INPUT: A slash command (API value ``1``).
        USER: A user context menu command (API value ``2``).
        MESSAGE: A message context menu command (API value ``3``).
        PRIMARY_ENTRY_POINT: The application's primary entry point command (API value ``4``).
        CHAT: Alias for :attr:`CHAT_INPUT`.
        ENTRY: Alias for :attr:`PRIMARY_ENTRY_POINT`.
    """

    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3
    PRIMARY_ENTRY_POINT = 4

    CHAT = 1
    ENTRY = 4


class InteractionCallbackType(IntEnum):
    """Response type sent back to Discord for an interaction.

    Attributes:
        PONG: Acknowledge a PING interaction.
        CHANNEL_MESSAGE_WITH_SOURCE: Send a message in the interaction's channel.
        DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE: Acknowledge and send a message later.
        DEFERRED_UPDATE_MESSAGE: Acknowledge a component interaction and update later.
        UPDATE_MESSAGE: Update the message a component is attached to.
        APPLICATION_COMMAND_AUTOCOMPLETE_RESULT: Return autocomplete choices.
        MODAL: Open a modal dialog.
        PREMIUM_REQUIRED: Tell the user a premium upgrade is required.
        LAUNCH_ACTIVITY: Launch an embedded activity.
        MESSAGE: Alias for :attr:`CHANNEL_MESSAGE_WITH_SOURCE`.
        DEFER: Alias for :attr:`DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE`.
        UPDATE: Alias for :attr:`UPDATE_MESSAGE`.
        AUTOCOMPLETE: Alias for :attr:`APPLICATION_COMMAND_AUTOCOMPLETE_RESULT`.
    """

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
    """Type of value accepted by an application command option.

    Attributes:
        SUB_COMMAND: A nested subcommand.
        SUB_COMMAND_GROUP: A group of related subcommands.
        STRING: A free-form string.
        INTEGER: A whole number.
        BOOLEAN: A true/false value.
        USER: A Discord user.
        CHANNEL: A Discord channel.
        ROLE: A Discord role.
        MENTIONABLE: A user or role mention.
        NUMBER: A floating-point number.
        ATTACHMENT: A file attachment.
    """

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
    """Base model for Discord payload objects.

    Unknown fields are ignored so payloads can gain new properties without
    breaking existing bots.
    """

    model_config = ConfigDict(extra="ignore")


class User(DiscordModel):
    """A Discord user."""

    id: Snowflake
    username: str
    descriminator: Optional[str] = None
    global_name: Optional[str] = None
    avatar: Optional[str] = None
    bot: Optional[bool] = None


class Member(DiscordModel):
    """A guild member and their guild-specific attributes."""

    user: Optional[User] = None
    nick: Optional[str] = None
    roles: list[Snowflake] = Field(default_factory=list)
    permissions: Optional[str] = None


class ApplicationCommandInteractionOption(DiscordModel):
    """A command option value supplied with an interaction.

    Options may contain nested options for subcommands and subcommand groups.
    """

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
    """The command data attached to an application command interaction."""

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
    """An interaction payload received from Discord.

    The framework validates the raw webhook body into this model before building
    a :class:`fastapi_interactions.context.Context` for command handlers.
    """

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
