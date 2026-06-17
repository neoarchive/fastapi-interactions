from fastapi import FastAPI, Request
from .middleware import VerifySignatureMiddleware
from .models import (
    Command,
    CommandMeta,
    Option
)
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
        self.commands = {}

    def command(
            self, 
            name: str,
            description: str,
            type: int = 1,
        ):
        def decorator(func):
            
            meta = getattr(
                    func, 
                    "__command_meta__", 
                    CommandMeta(name=name, description=description, type=type)
                )
            meta.name = name
            meta.description = description
            meta.type = type

            self.commands[name] = Command(callback=func, meta=meta)

            return func 
        return decorator

    def option(
            self,
            name: str,
            description: str,
            type: int = 3,
            required: bool = True
        ):
        def decorator(func):
            meta = getattr(
                    func, 
                    "__command_meta__",
                    CommandMeta(name="", description="", type=1)
                )
            option = Option(name=name, description=description, type=type, required=required)
            func.__command__meta = meta
            meta.options.append(option)
            func.__command_meta__ = meta 

            return func 
        return decorator

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
        
        return {
            "type": 4,
            "data": {
                "content": result
            }
        }
    
    def mount(self, app: FastAPI):
        app.add_middleware(VerifySignatureMiddleware, public_key=self.public_key)
        @app.post(self.interactions_path)
        async def interactions(request: Request):
            payload = await request.json()

            if payload['type'] == 1:
                return { "type": 1 }
            
            return await self.dispatch(payload)