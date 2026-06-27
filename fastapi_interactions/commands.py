from dataclasses import dataclass, field
from .models import Snowflake, ApplicationCommandOptionType
from typing import Optional
import sys

OptionType = ApplicationCommandOptionType


@dataclass
class CommandOption:
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
    name: str
    description: str
    options: list[CommandOption] = field(default_factory=list)
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
    guild_id: Optional[Snowflake] = None


class CommandRouter:
    def __init__(self, name: str = None, guild_id: Optional[Snowflake] = None):
        self.name = name or self.__infer_name()
        self.guild_id: Optional[Snowflake] = guild_id
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
            self.commands[name] = Command(
                callback=func, meta=meta, guild_id=self.guild_id
            )
            func.__dict__.pop("_command_meta", None)
            return func

        return decorator


class Option:
    @staticmethod
    def __create_operation_decorator(name: str, description: str, option_type: OptionType, required: bool = True):
        def decorator(func):
            meta = getattr(
                func, '_command_meta', CommandMeta(name='', description='', type=1)
            )

            meta.options.insert(
                0,
                CommandOption(
                    name=name,
                    description=description,
                    type=option_type,
                    required=required
                )
            )
            func._command_meta = meta
            return func
        return decorator

    @staticmethod
    def string(name: str, description: str, required: bool = True):
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
            @router.command(name="echo", description="Echo text")
            @Option.string(name="text", description="Text to echo", required=True)
            async def echo(ctx, text: str):
                return text
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.STRING,
            required=required
        )

    @staticmethod
    def integer(name: str, description: str, required: bool = True):
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
            @router.command(name="echo", description="Echo integer")
            @Option.integer(name="number", description="Integer to echo", required=True)
            async def echo(ctx, number: int):
                return int
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.INTEGER,
            required=required
        )

    @staticmethod
    def user(name: str, description: str, required: bool = True):
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
            @router.command(name="kick", description="Kick a user")
            @Option.user(name="user", description="Target user to kick", required=True)
            async def kick(ctx, user: Snowflake):
                ...
                return 'User kicked'
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.USER,
            required=required
        )

    @staticmethod
    def channel(name: str, description: str, required: bool = True):
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
            @router.command(name="purge", description="Purge a channel")
            @Option.user(name="channel", description="Target channel to purge", required=True)
            async def purge(ctx, channel: Snowflake):
                ...
                return 'Channel purged'
        """
        return Option.__create_operation_decorator(
            name=name,
            description=description,
            option_type=OptionType.CHANNEL,
            required=required
        )

