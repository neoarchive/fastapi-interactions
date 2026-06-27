# FastAPI Interactions

A lightweight Python framework for building Discord bots using Discord's webhook-based interactions API, built on top of FastAPI.

## Why webhook-based?

Traditional Discord bots maintain a persistent WebSocket connection to Discord's gateway. This works well but means your bot process must run continuously, making serverless deployment impractical.

Discord's interactions API is different — Discord POSTs to your HTTP endpoint each time a user invokes a command. Your app handles the request and responds, with no persistent connection required. This maps naturally onto serverless platforms like Vercel, where your bot only consumes resources when it's actually being used.

## Features

- **FastAPI-native** — your interactions endpoint is a standard ASGI app, deployable anywhere FastAPI runs.
- **Decorator-based commands** — register slash commands with `@router.command()` and `@router.option()`.
- **Automatic command loading** — point the bot at a package and it discovers commands automatically.
- **Clean response API** — return a string or a `MessageResponse` from your command; the framework handles the rest.
- **Serverless-friendly** — command syncing runs at deploy time, not on every cold start.
- **Async HTTP** — followup messages and response edits use `httpx.AsyncClient` throughout.

## At a glance

```python
from fastapi_interactions import Bot, CommandRouter, Option

bot = Bot(
    app_id=123456789,
    public_key="your_public_key",
    bot_token="Bot your_token",
)

router = CommandRouter()

@router.command(name="ping", description="Check bot latency")
async def ping(ctx):
    return "Pong!"

@router.command(name="echo", description="Echo a message back")
@Option.string(name="text", description="The text to echo", required=True)
async def echo(ctx, text: str):
    return text

bot.attach_router(router)

app = bot.app
```

## Deferred Responses

You can respond with a DeferredResponse if you have more complex work to do behind the scenes.

```python
from fastapi_interactions.responses import DeferredResponse
import asyncio

@router.command(name='process', description="Process some text")
@Option.string(name='text', description='text to process')
async def process(ctx, text: str):
    async def finish():
        await ctx.send('Beginning processing')
        asyncio.sleep(5) # simulate something slow 
        awat ctx.send(f'Processed text is {text!r}')

    return DeferredResponse(finish=finish)
```

!!! warning
    Long-running operations don't work with deferred responses on serverless because the container terminates after the HTTP response is sent. If a command needs more than 3 seconds, either complete the work within the response window, or use a traditional hosting setup. Most Discord bots don't need this pattern.

## Sync commands

fastapi-interactions supports registering your commands with discord automatically with a function call `bot.sync_commands()`

!!! warning
    The sync commands should only be called during build time on a serverless architecture. You don't want to make an outbound http request
    everytime you receive an interaction from discord.

```python
from fastapi_interactions import Bot, CommandRouter, Option

bot = Bot(
    app_id=123456789,
    public_key="your_public_key",
    bot_token="Bot your_token",
)

router = CommandRouter()

@router.command(name="ping", description="Check bot latency")
async def ping(ctx):
    return "Pong!"

@router.command(name="echo", description="Echo a message back")
@Option.string(name="text", description="The text to echo", required=True)
async def echo(ctx, text: str):
    return text

bot.attach_router(router)
bot.sync_commands()
app = bot.app
```



## Next steps

- [Installation](guide/installation.md)
- [Quickstart](guide/quickstart.md)
- [Deploying to Vercel](guide/vercel.md)
