from fastapi_interactions import Bot
from fastapi_interactions.router import (
    CommandRouter, option
)
from fastapi_interactions.responses import (
    MessageResponse,
    DeferResponse
)
from environs import env
import os

env.read_env()

APP_ID = env.int('APP_ID')
PUBLIC_KEY = env.str('PUBLIC_KEY') 
BOT_TOKEN = env.str('BOT_TOKEN')

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
app = bot.app