from dataclasses import dataclass, field
from loguru import logger


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


class CommandRouter:
    def __init__(self, name: str = "Unnamed router"):
        self.name = self.__name__ = name
        self.commands: dict[str, Command] = {}

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
            @router.command("hello", "Say hello")
            async def hello(ctx):
                return "Hello!"
        """

        def decorator(func):
            meta = getattr(
                func, "__command_meta__", CommandMeta(name="", description="", type=1)
            )
            meta.name = name
            meta.description = description
            self.commands[name] = Command(callback=func, meta=meta)
            func.__dict__.pop("__command_meta__", None)
            return func

        return decorator


def option(name: str, description: str, type: int = 3, required: bool = True) -> None:
    """
    Create an option with your slash command

    Args:
        name (str): name for your option field
        description (str): help description for the option field
        type (int, optional): option type. Defaults to 3.
        required (bool, optional): if option is required. Defaults to True.
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
