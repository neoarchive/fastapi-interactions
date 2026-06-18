from fastapi import FastAPI, Request
from .middleware import VerifySignatureMiddleware
from .responses import InteractionResponse, MessageResponse
from fastapi.responses import JSONResponse
from .models import Command, InteractionType, ApplicationCommandData
from pydantic import ValidationError
from .router import CommandRouter
import json
import requests


class Bot:
    def __init__(
        self,
        app_id: int,
        public_key: str,
        bot_token: str,
        interactions_path: str = "/interactions",
    ):
        self.app_id: int = app_id
        self.public_key: str = public_key
        self.bot_token: str = bot_token
        self.interactions_path: str = interactions_path
        self.base_url: str = f"https://discord.com/api/v10/applications/{app_id}"
        self.commands: dict[str, Command] = {}

        self.app = FastAPI()
        self._register_routes()

    def _register_routes(self):
        self.app.add_middleware(VerifySignatureMiddleware, public_key=self.public_key)

        @self.app.post(self.interactions_path)
        async def interactions(request: Request):
            payload = json.loads(request.state.raw_body)
            # payload = await request.json()

            if payload["type"] == InteractionType.PING:
                return {"type": 1}
            if payload["type"] == InteractionType.APPLICATION_COMMAND:
                try:
                    cmd_data = ApplicationCommandData.model_validate(payload["data"])
                except ValidationError:
                    return MessageResponse("Unexpected error occurred", ephemeral=True)

                return await self.dispatch(cmd_data)

    def include_router(self, router: CommandRouter):
        self.commands.update(router.commands)

    def sync_commands(self):
        payload = []
        for item in self.commands:
            cmd = self.commands[item]
            payload.append(cmd.meta.as_payload())
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bot {self.bot_token}",
        }

        api_url = f"{self.base_url}/commands"
        r = requests.put(api_url, headers=headers, json=payload)
        if r.status_code == 200:
            print("Commands registered!")
        else:
            raise Exception({"error": "registering commands failed", "data": r.json()})

    async def dispatch(self, data: ApplicationCommandData):
        command_name = data.name

        command = self.commands.get(command_name)

        if command is None:
            return {"type": 4, "data": {"content": "Unknown command"}}
        result = await command.callback(data)

        if isinstance(result, InteractionResponse):
            return JSONResponse(result.to_dict())

        return JSONResponse(MessageResponse(str(result)).to_dict())