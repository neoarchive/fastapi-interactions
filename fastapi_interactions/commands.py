from dataclasses import dataclass, field
from loguru import logger
from .models import Snowflake
from typing import Optional
import sys


@dataclass
class CommandOption:
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
        logger.debug(f'{self.name} router initialized')

    def __infer_name(self) -> str:
        frame = sys._getframe(2)
        return frame.f_globals.get("__name__", "Unknown")

    def after_attach(self):
        logger.info(
            f"{self.__name__} attached with commands {list(self.commands.keys())}"
        )

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
                func, "__command_meta__", CommandMeta(name="", description="", type=1)
            )
            meta.name = name
            meta.description = description
            self.commands[name] = Command(
                callback=func, meta=meta, guild_id=self.guild_id
            )
            func.__dict__.pop("__command_meta__", None)
            return func

        return decorator


def option(name: str, description: str, type: int = 3, required: bool = False) -> None:
    """
    Create an option with your slash command

    Args:
        name (str): name for your option field
        description (str): help description for the option field
        type (int, optional): option type. Defaults to 3.
        required (bool, optional): if option is required. Defaults to True.

    Example:
        ```python
        @router.command("echo", "Echo a string back")
        @option(name="phrase", description="Echo phrase", required=True)
        async def echo(ctx):
            return ctx.get_option_value(phrase)
        ```
    """

    def decorator(func):
        meta = getattr(
            func, "__command__meta__", CommandMeta(name="", description="", type=1)
        )

        meta.options.insert(
            0,
            CommandOption(
                name=name, description=description, type=type, required=required
            ),
        )
        func.__command_meta__ = meta
        return func

    return decorator
