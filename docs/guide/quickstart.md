# Quickstart

## Project layout

```
my-bot/
├── main.py
├── sync_commands.py
└── commands/
    ├── __init__.py
    └── general.py
```

## 1. Create your bot

```python
# main.py
from fastapi_interactions import Bot

bot = Bot(
    app_id=123456789,           # your Discord application ID
    public_key="your_public_key",   # from the Developer Portal
    bot_token="Bot your_token",
)

bot.load_commands("commands")

app = bot.app   # expose the FastAPI instance for your ASGI server
```

`app` is a plain FastAPI instance. Anything that can serve a FastAPI app — uvicorn locally, Vercel in production — works without any extra configuration.

## 2. Write your commands

Commands live in a package (here, `commands/`). Each module defines a `CommandRouter` and decorates functions against it.

```python
# commands/general.py
from fastapi_interactions import CommandRouter

router = CommandRouter()

@router.command(name="ping", description="Check bot latency")
async def ping(ctx):
    return "Pong!"

@router.command(name="echo", description="Echo a message back")
@router.option(name="text", description="The text to echo", required=True)
async def echo(ctx, text: str = "Default value"):
    return f"Your echo is {text!r}"
```

Returning a plain string sends a normal message response. See [Responses](responses.md) for richer reply types.

## 3. Sync commands to Discord

Command registration is separate from your app — run it once when deploying, not on every startup.

```python
# sync_commands.py
from fastapi_interactions import Bot

bot = Bot(
    app_id=123456789,
    public_key="your_public_key",
    bot_token="Bot your_token",
)

bot.load_commands("commands")
bot.sync_commands()
```

```bash
python sync_commands.py
# Commands registered!
```

!!! note
    Global command registration can take up to an hour to propagate to all Discord clients. During development, consider [guild-scoped commands](commands.md#guild-commands) for instant updates.

## 4. Run

```bash
uvicorn main:app --reload
```

Your bot's interactions endpoint is now live at `http://localhost:8000/interactions`.
