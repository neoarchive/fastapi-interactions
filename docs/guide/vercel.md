# Deploying to Vercel

FastAPI Interactions is designed for Vercel's serverless Python runtime. Each interaction is handled as a stateless HTTP request with no persistent connections or startup overhead.

## Project structure

Vercel's Python runtime automatically detects a FastAPI instance named `app` at your entrypoint. Since `bot.app` exposes a FastAPI instance, you just need to export it.

```
my-bot/
├── main.py
├── commands.py
├── sync_commands.py
├── .env
```

See [Vercel's FastAPI documentation](https://vercel.com/docs/frameworks/backend/fastapi#exporting-the-fastapi-application) for more details.

## Environment variables

Your bot needs Discord credentials. Never hardcode these — use environment variables instead.

**Local Development:** Create a `.env` file and use `environs` to load it:

```bash
pip install environs
```

`.env`:
```
DISCORD_APP_ID=123
DISCORD_PUBLIC_KEY=456
DISCORD_BOT_TOKEN=567
```

**Production (Vercel):** Configure variables in the Vercel dashboard under **Settings → Environment Variables**. Scope `DISCORD_BOT_TOKEN` and `DISCORD_PUBLIC_KEY` to **Production only** so preview deployments don't affect your live bot.

| Variable | Description |
|---|---|
| `DISCORD_APP_ID` | Your Discord application ID |
| `DISCORD_PUBLIC_KEY` | Ed25519 public key from the Developer Portal |
| `DISCORD_BOT_TOKEN` | Bot token, prefixed with `Bot ` |

## Application setup

### Entrypoint

Create `main.py` to initialize your bot and expose the FastAPI app:

```python
# main.py
from fastapi_interactions import Bot
from .commands import router
from environs import env

env.read_env()

bot = Bot(
    app_id=env.int('DISCORD_APP_ID'),
    public_key=env.str(DISCORD_PUBLIC_KEY'),
    bot_token=env.star('DISCORD_BOT_TOKEN')
)

bot.attach_router(router)
app = bot.app

```

!!! warning
    The variable must be named `app` and must be a `FastAPI` instance. Vercel's runtime detects it by name.

### Commands

Define your commands in `commands.py`:

```python
#commands.py
from fastapi_interactions.commands import CommandRouter, Option

router = CommandRouter('my-router')

@router.command(name='username', description='Retrieve your username')
async def username(ctx):
    return f'Hello {ctx.user.username}'

@router.command(name='echo', description='Echo a text')
@Option.string(name='text', description='Text to echo')
async def echo(ctx, text: str):
    return text

```

## Syncing commands

Command syncing happens at deploy time, not at runtime. Create `sync_commands.py`:

```python
# sync_commands.py
from fastapi_interactions import Bot
from .commands import router
from environs import env
import sys

env.read_env()

vercel_env = env.str('VERCEL_ENV')

if vercel_env != 'Production':
    print(f'Skipping command sync: VERCEL_ENV={vercel_env!r}')
    sys.exit(0)

bot = Bot(
    app_id=env.int('DISCORD_APP_ID'),
    public_key=env.str(DISCORD_PUBLIC_KEY'),
    bot_token=env.star('DISCORD_BOT_TOKEN')
)

bot.attach_router(router)
bot.sync_commands()

```

This script skips syncing on preview builds, preventing them from overwriting your live commands.

### Configure build command

In the Vercel dashboard under **Settings → Build & Development Settings**, set the build command to:

```
python sync_commands.py
```

Commands are synced automatically on every production deploy. Global command registration can take up to an hour to propagate. During development, use guild-scoped routers for instant updates:

```python
router = CommandRouter(guild_id="123456789")
```

## After deployment

Once your app is live, set your Discord interactions endpoint URL in the [Developer Portal](https://discord.com/developers/applications):

```
https://your-project.vercel.app/interactions
```

Discord will verify the endpoint by sending a PING handshake. Once confirmed, your bot is ready.

## Performance

Vercel's serverless functions spin up on demand. Discord requires a response within **3 seconds**. The framework adds minimal overhead — no database connections, no gateway handshakes — so cold starts are typically well within that window.

!!! warning
    Long-running operations don't work with deferred responses on serverless because the container terminates after the HTTP response is sent. If a command needs more than 3 seconds, either complete the work within the response window, or deploy to traditional hosting. Most Discord bots don't need this pattern.