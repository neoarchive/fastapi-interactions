from fastapi import FastAPI, Request
from .middleware import VerifySignatureMiddleware
from .responses import InteractionResponse, MessageResponse
from fastapi.responses import JSONResponse
from .models import (
    InteractionType,
    ApplicationCommandData,
    Interaction,
    Context,
)
from .commands import Command
from pydantic import ValidationError
from .commands import CommandRouter
import json
import httpx
import importlib
import pkgutil
from loguru import logger


class Bot:
    def __init__(
        self,
        app_id: int,
        public_key: str,
        bot_token: str,
        interactions_path: str = "/interactions",
    ):
        """Initialize a new Discord HTTP webhook bot.

        Args:
            app_id (int): The Discord Application ID.
            public_key (str): Public key used to validate incoming webhook signatures
                from Discord.
            bot_token (str): Bot token used for authenticated API calls to Discord
                (command registration, message sending, etc.).
            interactions_path (str, optional): The route path where the bot listens
                for interaction webhooks. Defaults to "/interactions".
        """
        self.app_id: int = app_id
        self.public_key: str = public_key
        self.bot_token: str = bot_token
        self.interactions_path: str = interactions_path
        self.base_url: str = f"https://discord.com/api/v10/applications/{app_id}"
        self.commands: dict[str, Command] = {}

        self.app = FastAPI()
        self._register_routes()

    def _register_routes(self) -> None:
        self.app.add_middleware(VerifySignatureMiddleware, public_key=self.public_key)

        @self.app.post(self.interactions_path)
        async def interactions(request: Request):
            payload = json.loads(request.state.raw_body)

            if payload["type"] == InteractionType.PING:
                return {"type": 1}

            if payload["type"] == InteractionType.APPLICATION_COMMAND:
                """Construct Context"""
                try:
                    interaction = Interaction.model_validate(payload)
                    application_command = ApplicationCommandData.model_validate(
                        interaction.data
                    )
                except ValidationError as e:
                    print(e.errors())
                    response = MessageResponse(
                        "Unexpected error occurred", ephemeral=True
                    )
                    return JSONResponse(response.to_dict())

                context = Context(interaction=interaction, options=application_command)

                return await self.dispatch(
                    command_name=application_command.name, ctx=context
                )

    def attach_router(self, router: CommandRouter) -> None:
        """Attach a CommandRouter to the bot.

        Registers a CommandRouter with this Discord webhook bot, enabling it to
        handle slash commands, message components, modals, and other interactions
        defined within the router.

        Args:
            router (CommandRouter): The router instance containing command
                registrations and handler mappings.

        Raises:
            TypeError: If the provided router is not an instance of CommandRouter.
        """
        if not isinstance(router, CommandRouter):
            raise TypeError(f"Expected a CommandRouter, got {type(router).__name__!r}")
        self.commands.update(router.commands)

    def __load_routers_from_module(self, module) -> None:
        routers = getattr(module, "__routers__", None)

        if routers is None:
            routers = [
                obj for obj in vars(module).values() if isinstance(obj, CommandRouter)
            ]

        if not routers:
            logger.warning(f"No routers configured in {module.__name__!r}")
            return

        logger.debug(f"{len(routers)} routers discovered in {module.__name__!r}")
        for router in routers:
            self.attach_router(router)

    def load_extension(self, path: str) -> None:
        """Load extension(s) from a module or package.

        Dynamically imports the given Python path and registers all `CommandRouter`
        instances by calling the internal `__load_routers_from_module` method.

        Behavior:
            - If `path` points to a **module**: Loads routers from that single module.
            - If `path` points to a **package**: Recursively discovers and loads
              all non-package modules within it (and its subpackages).

        Args:
            path (str): Dot-separated import path to a module or package.

        Raises:
            ModuleNotFoundError: If the module or package does not exist.
            ImportError: If an error occurs while importing any module.

        Examples:
            Load a single module:
            ```python
            bot.load_extension("my_bot.extensions.moderation")
            ```
            Load all modules from a package(recursive):
            ```python
            bot.load_extension('my_bot.extensions')
            ```
        """
        module = importlib.import_module(path)
        if hasattr(module, "__path__"):
            # This is a package, lets recurisvely find modules
            logger.info(f"Scanning packages {path!r} for extensions")
            walked_packages = pkgutil.walk_packages(
                module.__path__, module.__name__ + "."
            )
            for _, module_name, is_package in walked_packages:
                print(module_name, is_package)
                if not is_package:
                    imported = importlib.import_module(module_name)
                    self.__load_routers_from_module(imported)
        else:
            self.__load_routers_from_module(module)

    def sync_commands(self) -> None:
        """Sync all registered commands with Discord's API.

        Sends a bulk overwrite of the bot's slash commands using the Discord
        Application Commands endpoint.

        Raises:
            Exception: If the API request fails.
        """
        global_payloads = []
        guild_payloads: dict[int, list] = {}

        for command in self.commands.values():
            if command.guild_id is not None:
                guild_payloads.setdefault(command.guild_id, []).append(command.meta.as_payload())
            else:
                global_payloads.append(command.meta.as_payload())

        if global_payloads:
            self.__put__commands(f'{self.base_url}/commands', global_payloads)

        for guild_id, payload in guild_payloads.items():
            self.__put__commands(f'{self.base_url}/guilds/{guild_id}/commands', payload)

    def __put__commands(self, url: str, payload: list) -> None:
        headers = {
            'Authorization': f'Bot {self.bot_token}'
        }
        with httpx.Client() as client:
            response = client.put(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception({"error": "registering commands failed", "data": response.json()})
        logger.info(f'Synced {len(payload)} commands to {url!r}')

    async def dispatch(self, command_name: str, ctx: Context) -> JSONResponse:
        command = self.commands.get(command_name)
        if command is None:
            return {"type": 4, "data": {"content": "Unknown command"}}

        result = await command.callback(ctx)
        if isinstance(result, InteractionResponse):
            return JSONResponse(result.to_dict())

        return JSONResponse(MessageResponse(str(result)).to_dict())
