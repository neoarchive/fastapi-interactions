"""Command registration, routing, and option decorators.

Routers group commands and carry settings such as guild scope, integration
types, and interaction contexts. The :class:`Option` decorators attach option
metadata that is later bound to command callback parameters.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass, field

from .models import (
    ApplicationCommandOptionType,
    IntegrationType,
    InteractionContext,
    Snowflake,
)

OptionType = ApplicationCommandOptionType


@dataclass
class CommandOption:
    """A single option declared on a command."""

    name: str
    description: str
    type: OptionType = OptionType.STRING
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
    """Registration metadata sent to Discord for a command.

    ``integration_types`` and ``contexts`` control where the command can be
    installed and invoked. They are only valid for globally scoped commands.
    """

    name: str
    description: str
    options: list[CommandOption] = field(default_factory=list)
    type: int = 1
    integration_types: IntegrationType | None = None
    contexts: InteractionContext | None = None

    def as_payload(self):
        payload = {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "options": [option.as_payload() for option in self.options],
        }
        if self.integration_types is not None:
            payload["integration_types"] = self.integration_types.to_api()
        if self.contexts is not None:
            payload["contexts"] = self.contexts.to_api()
        return payload


@dataclass(slots=True)
class Command:
    """A command callback paired with its registration metadata."""

    callback: callable
    meta: CommandMeta
    guild_id: Snowflake | None = None


class CommandRouter:
    """A collection of commands that can be attached to a bot.

    Args:
        name: Optional router name used in logs. Inferred from the caller's
            module when omitted.
        guild_id: Scope every command in the router to a single guild. Guild
            scoped commands cannot set ``integration_types`` or ``contexts``.
        integration_types: Where commands can be installed. Use
            :class:`~fastapi_interactions.models.IntegrationType` flags.
        contexts: Where commands can be invoked. Use
            :class:`~fastapi_interactions.models.InteractionContext` flags.

    Raises:
        ValueError: If a guild-scoped router also sets ``integration_types`` or
            ``contexts``, or if either flag value is empty.
    """

    def __init__(
        self,
        name: str | None = None,
        guild_id: Snowflake | None = None,
        *,
        integration_types: IntegrationType | None = None,
        contexts: InteractionContext | None = None,
    ):
        self.name = name or self.__infer_name()
        self.guild_id = guild_id

        if guild_id is not None and (
            integration_types is not None or contexts is not None
        ):
            raise ValueError(
                f"Router {self.name} is guild scoped. Cannt bind integration/interaction types"
            )

        if integration_types is not None and not integration_types:
            raise ValueError("integration types cannot be empty;")

        if contexts is not None and not contexts:
            raise ValueError("contexts cannot be empty")

        self.integration_types = integration_types
        self.contexts = contexts
        self.commands: dict[str, Command] = {}

    def __infer_name(self) -> str:
        frame = sys._getframe(2)
        return frame.f_globals.get("__name__", "Unknown")

    def __len__(self) -> int:
        return len(list(self.commands.keys()))

    def __str__(self) -> str:
        return f"{list(self.commands.keys())}"

    def command(self, name: str, description: str) -> None:
        """
        Add a slash command to this router.

        The decorated function is registered as the handler for the command
        and will be included when the router is attached to the application.

        Args:
            name: Unique command name.
            description: User-facing command description.

        Example:
            ```python
            @router.command("hello", "Say hello")
            async def hello(ctx):
                return "Hello!"
            ```
        """

        def decorator(func):
            meta = getattr(
                func, "_command_meta", CommandMeta(name="", description="", type=1)
            )
            meta.name = name
            meta.description = description
            meta.integration_types = self.integration_types
            meta.contexts = self.contexts
            self.commands[name] = Command(
                callback=func, meta=meta, guild_id=self.guild_id
            )
            func.__dict__.pop("_command_meta", None)
            return func

        return decorator


class Option:
    """Decorators that attach typed options to command callbacks.

    Each static method registers one Discord option type. Decorate the command
    below ``@router.command(...)`` so the option metadata is collected before
    the command is registered.
    """

    @staticmethod
    def __create_operation_decorator(
        name: str, description: str, option_type: OptionType, required: bool = True
    ):
        def decorator(func):
            meta = getattr(
                func, "_command_meta", CommandMeta(name="", description="", type=1)
            )

            meta.options.insert(
                0,
                CommandOption(
                    name=name,
                    description=description,
                    type=option_type,
                    required=required,
                ),
            )
            func._command_meta = meta
            return func

        return decorator

    @staticmethod
    def string(name: str, description: str, required: bool = True) -> Callable:
        """Register a string option on a command.

        Decorates a command callback to add a string option parameter. The option name
        must match a parameter name in the callback for automatic value binding.

        Args:
            name: The option name. Must match a callback parameter name.
            description: Human-readable description shown to Discord users.
            required: Whether the option is required. Defaults to True.

        Returns:
            A decorator that attaches the option metadata to the function.

        Example:
        ```python
        @router.command(name="echo", description="Echo text")
        @Option.string(name="text", description="Text to echo", required=True)
        async def echo(ctx, text: str):
            return text
        ```
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.STRING,
            required=required,
        )

    @staticmethod
    def integer(name: str, description: str, required: bool = True) -> Callable:
        """Register an integer option on a command.

        Decorates a command callback to add an integer option parameter. The option name
        must match a parameter name in the callback for automatic value binding.

        Args:
            name: The option name. Must match a callback parameter name.
            description: Human-readable description shown to Discord users.
            required: Whether the option is required. Defaults to True.

        Returns:
            A decorator that attaches the option metadata to the function.

        Example:
        ```python
        @router.command(name="echo", description="Echo integer")
        @Option.integer(name="number", description="Integer to echo", required=True)
        async def echo(ctx, number: int):
            return int
        ```
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.INTEGER,
            required=required,
        )

    @staticmethod
    def user(name: str, description: str, required: bool = True) -> Callable:
        """Register a user option on a command.

        Decorates a command callback to add a user option parameter. The option name
        must match a parameter name in the callback for automatic value binding.

        Args:
            name: The option name. Must match a callback parameter name.
            description: Human-readable description shown to Discord users.
            required: Whether the option is required. Defaults to True.

        Returns:
            A decorator that attaches the option metadata to the function.

        Example:
        ```python
        @router.command(name="kick", description="Kick a user")
        @Option.user(name="user", description="Target user to kick", required=True)
        async def kick(ctx, user: Snowflake):
            ...
            return 'User kicked'
        ```
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.USER,
            required=required,
        )

    @staticmethod
    def channel(name: str, description: str, required: bool = True) -> Callable:
        """Register a channel option on a command.

        Decorates a command callback to add a channel option parameter. The option name
        must match a parameter name in the callback for automatic value binding.

        Args:
            name: The option name. Must match a callback parameter name.
            description: Human-readable description shown to Discord users.
            required: Whether the option is required. Defaults to True.

        Returns:
            A decorator that attaches the option metadata to the function.

        Example:
        ```python
        @router.command(name="purge", description="Purge a channel")
        @Option.user(name="channel", description="Target channel to purge", required=True)
        async def purge(ctx, channel: Snowflake):
            ...
            return 'Channel purged'
        ```
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.CHANNEL,
            required=required,
        )

    @staticmethod
    def role(name: str, description: str, required: bool = True) -> Callable:
        """Register a role option on a command.

        Decorates a command callback to add a channel option parameter. The option name
        must match a parameter name in the callback for automatic value binding.

        Args:
            name: The option name. Must match a callback parameter name.
            description: Human-readable description shown to Discord users.
            required: Whether the option is required. Defaults to True.

        Returns:
            A decorator that attaches the option metadata to the function.

        Example:
        ```python
        @router.command(name="rmrole", description="Delete a role")
        @Option.role(name="role", description="role to delete", required=True)
        async def purge(ctx, role: Snowflake):
            ...
            return 'Role purged'
        ```
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.ROLE,
            required=required,
        )

    @staticmethod
    def mentionable(name: str, description: str, required: bool = True) -> Callable:
        """Register a mentionable option on a command.

        Decorates a command callback to add a channel option parameter. The option name
        must match a parameter name in the callback for automatic value binding.

        Args:
            name: The option name. Must match a callback parameter name.
            description: Human-readable description shown to Discord users.
            required: Whether the option is required. Defaults to True.

        Returns:
            A decorator that attaches the option metadata to the function.

        Example:
        ```python
        @router.command(name="warn", description="Warn a user or role")
        @Option.mentionable(name="target", description="User or role to warn", required=True)
        async def warn(ctx, target: Snowflake):
            return f"⚠️ Warning issued to <@&{target}>"
        ```
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.MENTIONABLE,
            required=required,
        )

    @staticmethod
    def boolean(name: str, description: str, required: bool = True) -> Callable:
        """Register a boolean option on a command.

        Decorates a command callback to add a boolean option parameter. The option name
        must match a parameter name in the callback for automatic value binding.

        Args:
            name: The option name. Must match a callback parameter name.
            description: Human-readable description shown to Discord users.
            required: Whether the option is required. Defaults to True.

        Returns:
            A decorator that attaches the option metadata to the function.

        Example:
        ```python
        @router.command(name="ban", description="Ban a user")
        @Option.user(name="target", description="User to ban", required=True)
        @Option.boolean(name="soft", description="Is this a softban", required=True)
        async def warn(ctx, target: Snowflake, soft: bool):
            if soft:
                ...
            else:
                ...
            return 'Command executed'
        ```
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.BOOLEAN,
            required=required,
        )

    @staticmethod
    def number(name: str, description: str, required: bool = True) -> Callable:
        """Register a number option on a command.

        Decorates a command callback to add a number option parameter. The option name
        must match a parameter name in the callback for automatic value binding.
        This is a float in python.

        Args:
            name: The option name. Must match a callback parameter name.
            description: Human-readable description shown to Discord users.
            required: Whether the option is required. Defaults to True.

        Returns:
            A decorator that attaches the option metadata to the function.

        Example:
        ```python
        @router.command(name="rate", description="Rate something")
        @Option.number(name="score", description="Rating from 0 to 10", required=True)
        async def rate(ctx, score: float):
            return f"Rating: {score}/10 ⭐"
        ```
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.NUMBER,
            required=required,
        )
