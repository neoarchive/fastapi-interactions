from fastapi import FastAPI, Request
from fastapinteractions import Bot 
from fastapinteractions.responses import MessageResponse
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

@bot.command(
    name='access',
    description='access the server'
)
@bot.option(
    name='password',
    description='enter the password',
    required=True,
    type=3
)
async def access(ctx):
    user = ctx['member']['user']['username']
    return MessageResponse(f'Hey {user}. How are ya?')


# bot.sync_commands() -- only call once during deployment if serverless.
bot.mount(app)