# Quickstart

Get your first Discord bot running in 5 minutes.

## 1. Install

```bash
pip install fastapi-interactions environs
```

## 2. Create your bot

Create `main.py`:

```python
from fastapi_interactions import Bot
from fastapi_interactions.commands import CommandRouter, option
from environs import env

env.read_env()

DISCORD_APP_ID = env.int("DISCORD_APP_ID")
DISCORD_PUBLIC_KEY = env.str("DISCORD_PUBLIC_KEY")
DISCORD_BOT_TOKEN = env.str("DISCORD_BOT_TOKEN")

bot = Bot(app_id=DISCORD_APP_ID, public_key=DISCORD_PUBLIC_KEY, bot_token=DISCORD_BOT_TOKEN)

router = CommandRouter()

@router.command(name="hello", description="Say hello")
async def hello(ctx):
    return f"Hello, {ctx.user.username}!"

@router.command(name="echo", description="Echo a message")
@router.option(name="text", description="Text to echo", required=True)
async def echo(ctx, text: str):
    return f"You said: {text}"

bot.include_router(router)
bot.sync_commands() - # Call the script directly `python main.py` once to sync commands and then comment this line out. 
app = bot.app

```

## 3. Set up environment variables

Create `.env`:

```
DISCORD_APP_ID=123456789
DISCORD_PUBLIC_KEY=your_public_key_here
DISCORD_BOT_TOKEN=Bot your_bot_token_here
```

Find these in the [Discord Developer Portal](https://discord.com/developers/applications).

## 4. Run locally

```bash
fastapi dev main.py
```

Your bot is now listening on `http://localhost:8000/interactions`.

## 5. Make it reachable to Discord

Discord needs a public HTTPS URL to send interactions to. Use [ngrok](https://ngrok.com) for local development:

```bash
ngrok http 8000
```

Copy the `https://` URL and paste it into your Discord application's **Interactions Endpoint URL** field (in Developer Portal → Your App → General Information), appending `/interactions`: