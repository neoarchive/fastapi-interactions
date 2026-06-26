# First bot

This example demonstrates a complete Discord bot using FastAPI Interactions, including environment variable configuration, multiple commands, and deferred responses with followups.

## Setup

Environment variables are loaded from a `.env` file. Store your Discord credentials there:

```
APP_ID=123456789
PUBLIC_KEY=your_public_key_here
BOT_TOKEN=Bot your_bot_token_here
```

## The bot

```python
from fastapi_interactions import Bot
from fastapi_interactions.commands import CommandRouter, option
from fastapi_interactions.responses import DeferResponse
from environs import env
import asyncio

env.read_env()

APP_ID = env.int("APP_ID")
PUBLIC_KEY = env.str("PUBLIC_KEY")
BOT_TOKEN = env.str("BOT_TOKEN")

bot = Bot(app_id=APP_ID, public_key=PUBLIC_KEY, bot_token=BOT_TOKEN)

router = CommandRouter("router_a")

@router.command("username", "Returns your username")
async def username(ctx):
    return f"Your username is {ctx.user.username!r}"


@router.command("echo", "Repeat after me")
@option("text", "Text to repeat back", required=True)
async def echo(ctx, text: str):
    async def finish():
        await asyncio.sleep(2)
        await ctx.send(f'Edits the original interaction message - {text!r}') # follow up message (edits the original interaction msg)
        await asyncio.sleep(2)
        await ctx.send('Sends a new message as response') # Follow up message sent as a reply to the original interaction msg
    return DeferResponse(finish=finish)


bot.attach_router(router)

""" run sync commands once; just execute this script directly with python to do so and then comment it out"""
# bot.sync_commands()
# bot.delete_all__commands()
app = bot.app

```

## What's happening

**`username` command** — The simplest case. Returns immediately with a plain string, which the framework wraps in a `MessageResponse` automatically. `ctx.user` gives you the invoking user's data.

**`echo` command** — Demonstrates deferred responses. When invoked, Discord immediately receives a defer acknowledgement and shows "thinking..." to the user. Meanwhile, the `finish` async function runs in the background — it sleeps 2 seconds (simulating work), sends a followup message, sleeps again, then sends another followup. Each `ctx.send()` is a separate message, not edits.

**Command syncing** — `bot.sync_commands()` registers your commands with Discord. Run this once during deployment (it's skipped on preview builds), then comment it out. Global command registration can take up to an hour to propagate.