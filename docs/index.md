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
from fastapi_interactions import Bot, CommandRouter, option
from fastapi_interactions.responses import MessageResponse

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
@router.option(name="text", description="The text to echo", required=True)
async def echo(ctx, text: str):
    return text

bot.attach_router(router)

app = bot.app
```

## Next steps

- [Installation](guide/installation.md)
- [Quickstart](guide/quickstart.md)
- [Deploying to Vercel](guide/vercel.md)
