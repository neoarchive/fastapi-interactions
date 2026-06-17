from fastapi import FastAPI, Request
from fastapi_interactions import Bot
from fastapi_interactions.router import CommandRouter, option
from fastapi_interactions.responses import (
    MessageResponse,
    DeferResponse
)
from dotenv import load_dotenv
import os

load_dotenv()

APP_ID = int(os.getenv('APP_ID'))
PUBLIC_KEY = str(os.getenv('PUBLIC_KEY'))
BOT_TOKEN = str(os.getenv('BOT_TOKEN'))

app = FastAPI()

bot = Bot(
    app_id=APP_ID,
    public_key=PUBLIC_KEY,
    bot_token=BOT_TOKEN
)

router = CommandRouter()

@router.command(name='echo', description='echo a message')
@option(name='text', description='Text to echo', required=True)
async def echo(ctx):
    return MessageResponse('Hello world!')

bot.include_router(router=router)
bot.sync_commands()
bot.mount(app)