# Deploying to Vercel

FastAPI Interactions is designed with Vercel's serverless Python runtime in mind. There are no background threads, no gateway connections, and no startup side-effects — each interaction is handled as an independent HTTP request.

## Project structure

Vercel's Python runtime looks for a FastAPI instance named `app` at one of a set of recognised entrypoint paths. The simplest layout:

```
my-bot/
├── api/
│   └── index.py       ← Vercel serves this at /api, proxied to /interactions
├── commands/
│   ├── __init__.py
│   └── general.py
├── sync_commands.py
└── vercel.json
```

## Entrypoint

```python
# api/index.py
from fastapi_interactions import Bot

bot = Bot(
    app_id=123456789,
    public_key="your_public_key",
    bot_token="Bot your_token",
)

bot.load_commands("commands")

app = bot.app
```

!!! warning
    The variable must be named `app` and must be a `FastAPI` instance. Vercel's runtime detects it by name.

## vercel.json

```json
{
  "rewrites": [
    { "source": "/interactions", "destination": "/api/index" }
  ]
}
```

Set your Discord interactions endpoint URL to `https://your-project.vercel.app/interactions`.

## Syncing commands at build time

Add `sync_commands.py` to your Vercel build command so commands are registered automatically on every production deploy.

In the Vercel dashboard under **Settings → Build & Development Settings**:

```
Build Command: python sync_commands.py
```

```python
# sync_commands.py
import os
import sys
from fastapi_interactions import Bot

# Only sync on production deploys — prevents preview builds from
# overwriting the live global command set with work-in-progress commands.
if os.environ.get("VERCEL_ENV") != "production":
    print(f"Skipping command sync: VERCEL_ENV={os.environ.get('VERCEL_ENV')!r}")
    sys.exit(0)

bot = Bot(
    app_id=int(os.environ["DISCORD_APP_ID"]),
    public_key=os.environ["DISCORD_PUBLIC_KEY"],
    bot_token=os.environ["DISCORD_BOT_TOKEN"],
)

bot.load_commands("commands")
bot.sync_commands()
```

## Environment variables

Set these in the Vercel dashboard under **Settings → Environment Variables**. Scope `DISCORD_BOT_TOKEN` and `DISCORD_PUBLIC_KEY` to **Production only** so that preview deployments can't accidentally interact with your live bot.

| Variable | Description |
|---|---|
| `DISCORD_APP_ID` | Your Discord application ID |
| `DISCORD_PUBLIC_KEY` | Ed25519 public key from the Developer Portal |
| `DISCORD_BOT_TOKEN` | Bot token, prefixed with `Bot ` |

## Cold starts

Vercel's serverless functions spin up on demand. Discord requires a response within **3 seconds** of receiving an interaction. The framework adds minimal overhead — no database connections, no gateway handshakes — so cold starts are typically well within that window.

For commands that do meaningful work (API calls, database queries), use `ctx.defer()` to acknowledge the interaction immediately and deliver the real response as a followup once the work is done. See [Context](context.md#deferring) for details.
