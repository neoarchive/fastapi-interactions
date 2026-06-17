from fastapi import FastAPI, Request
from .middleware import VerifySignatureMiddleware
from .responses import InteractionResponse, MessageResponse
from fastapi.responses import JSONResponse
from .models import (
    Command,
    CommandMeta,
    Option,
    InteractionType
)
from .router import CommandRouter
import json
import requests


class Bot:
    def __init__(
            self,
            app_id: int,
            public_key: str,
            bot_token: str,
            interactions_path: str='/interactions'
    ):
        self.app_id = app_id
        self.public_key = public_key
        self.bot_token = bot_token
        self.interactions_path = interactions_path
        self.base_url = f'https://discord.com/api/v10/applications/{app_id}' 
        self.commands: dict[str, Command] = {}

    def include_router(self, router: CommandRouter):
        self.commands.update(router.commands)

    def sync_commands(self):
        payload = []
        for item in self.commands:
            cmd = self.commands[item]
            payload.append(cmd.meta.as_payload())
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bot {self.bot_token}'
        }

        api_url = f'{self.base_url}/commands'
        r = requests.put(api_url, headers=headers, json=payload)
        print(r.status_code)
        print(r.json())


    async def dispatch(self, interaction: dict):
        command_name = interaction['data']['name']

        command = self.commands.get(command_name)

        if command is None:
            return {
                "type": 4,
                "data": {
                    "content": "Unknown command"
                }
            }
        
        result = await command.callback(interaction)

        if isinstance(result, InteractionResponse):
            return JSONResponse(result.to_dict()) 

        return JSONResponse(
            MessageResponse(str(result)).to_dict()
        )
    
    def mount(self, app: FastAPI):
        app.add_middleware(VerifySignatureMiddleware, public_key=self.public_key)
        @app.post(self.interactions_path)
        async def interactions(request: Request):
            payload = json.loads(request.state.raw_body)
            # payload = await request.json()

            if payload['type'] == InteractionType.PING:
                return {
                    'type': 1
                }
            
            if payload['type'] == InteractionType.APPLICATION_COMMAND:
                return await self.dispatch(payload)