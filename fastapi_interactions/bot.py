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
        """Initialize a bot client

        Args:
            app_id (int): APP ID Of your discord app
            public_key (str): PUBLIC KEY of your discord app
            bot_token (str): BOT TOKEN of your app's bot
            interactions_path (str, optional): Endpoint to listen for interaction webhooks on. Defaults to "/interactions".
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
        """Attach a router of commands to the bot

        Args:
            router (CommandRouter): The router object to include in the bot
        """
        if not isinstance(router, CommandRouter):
            raise TypeError(f"Expected a CommandRouter, got {type(router).__name__!r}")
        self.commands.update(router.commands)
        router.after_attach()

    def load_extension(self, extension_path: str) -> None:
        logger.info(f'Loading extension {extension_path!r}')
        extension = importlib.import_module(extension_path)

        logger.debug(f'Looking for routers defined in {extension_path!r}')
        routers = getattr(extension, "__routers__", [])
        if not routers:
            logger.debug(f'__routers__ unset in {extension_path!r}. searching manually')
            routers = [
                obj
                for obj in vars(extension).values()
                if isinstance(obj, CommandRouter)
            ]

        for router in routers:
            self.attach_router(router)

    def load_extensions(self, package_name: str) -> None:
        logger.info(f'Attempting to load extensions from {package_name!r}')
        package = importlib.import_module(package_name)
        if not hasattr(package, '__path__'):
            raise ValueError(
                f'{package_name!r} is a module not a package. '
                f'Use load_extension({package_name!r}) to load a single module'
            )
        for _, module_name, _ in pkgutil.walk_packages(
            package.__path__,
            package.__name__+"."
        ):
            self.load_extension(module_name)

    def sync_commands(self) -> None:
        payload = [cmd.meta.as_payload() for cmd in self.commands.values()]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bot {self.bot_token}",
        }

        api_url = f"{self.base_url}/commands"
        r = httpx.put(api_url, headers=headers, json=payload)
        if r.status_code != 200:
            detail = {"error": "registering commands failed", "data": r.json()}
            raise Exception(detail)
        print("Commands registered!")

    async def dispatch(self, command_name: str, ctx: Context) -> JSONResponse:
        command = self.commands.get(command_name)
        if command is None:
            return {"type": 4, "data": {"content": "Unknown command"}}

        result = await command.callback(ctx)
        if isinstance(result, InteractionResponse):
            return JSONResponse(result.to_dict())

        return JSONResponse(MessageResponse(str(result)).to_dict())
