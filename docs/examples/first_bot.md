# First bot

```python
from fastapi_interactions import Bot
from fastapi_interactions.commands import CommandRouter, option
from environs import env

env.read_env()

APP_ID = env.int("APP_ID")
PUBLIC_KEY = env.str("PUBLIC_KEY")
BOT_TOKEN = env.str("BOT_TOKEN")

bot = Bot(app_id=APP_ID, public_key=PUBLIC_KEY, bot_token=BOT_TOKEN)

router = CommandRouter("router_a", "1514652977200369684")


@router.command("username", "Returns your username")
async def username(ctx):
    return f"Your username is {ctx.user.username!r}"


@router.command("echo", "Repeat after me")
@option("text", "Text to repeat back", required=True)
async def echo(ctx, text: str):
    return text


bot.attach_router(router)

""" run sync commands once; just execute this script directly with python to do so and then comment it out"""
# bot.sync_commands()
# bot.delete_all__commands()
app = bot.app

```