<a href='https://fastapi-interactions.readthedocs.io/en/latest/' target='_blank'>Read the docs here</a>

# Install fastapi-interactions

```
pip install fastapi-interactions
```

# Quick example

```python
from fastapi_interactions import Bot
from fastapi_interactions.commands import (
    CommandRouter, option,
)

bot = Bot(app_id='DISCORD_APP_ID',
          public_key='DISCORD_PUBLIC_KEY',
          bot_token='DISCORD_BOT_TOKEN')

router = CommandRouter()


@router.command('helloworld', 'say hello')
async def hello(ctx):
    return 'hello'


@router.command('echo', 'echo a phrase back')
@option('text', 'the text to repeat')
async def echo(ctx, text: str):
    return text

bot.attach_router(router)

bot.sync_commands()  # Use only on build time if running on vercel
app = bot.app

```
---

> [!WARNING]
> ### SYNCING COMMANDS
> If you are on a serverless architecture like Vercel, make sure you only call `bot.sync_commands` during build time. You do not want this being executed every time you receive an interaction in production.

---