# Extensions

Extensions let you organize commands into separate modules that get loaded automatically. This keeps your bot's code clean and scalable as you add more commands.

## Project structure

Organize commands into a package:

```
my-bot/
├── main.py
├── sync_commands.py
├── commands/
│   ├── __init__.py
│   ├── general.py
│   ├── moderation.py
│   └── fun.py
```

Each module in the `commands/` package defines one or more routers.

!!! warning
    Subdirectories containing routers must have `__init__.py` files to be recognized as packages. The top-level `commands` directory can omit it (Python treats it as a namespace package), but it's recommended to include one for clarity.

## Defining a router in a module

Create `commands/general.py`:

```python
from fastapi_interactions.commands import CommandRouter

router = CommandRouter()

@router.command(name="ping", description="Check bot latency")
async def ping(ctx):
    return "Pong!"

@router.command(name="echo", description="Echo a message")
@router.option(name="text", description="Text to echo", required=True)
async def echo(ctx, text: str):
    return text
```

The module exposes a `router` attribute. The router name is inferred from the module name automatically — in this case, `"commands.general"`.

## Loading extensions

In your `main.py`, load all routers from the commands package:

```python
from fastapi_interactions import Bot

bot = Bot(...)

bot.load_extension("commands")

app = bot.app
```

`bot.load_extension("commands")` walks the entire `commands/` package and discovers all routers, registering them automatically. On startup, you'll see log output like:

```
Router 'commands.general' attached with 2 commands
Router 'commands.moderation' attached with 5 commands
Router 'commands.fun' attached with 3 commands
```

## Loading a single module

You can also load a specific module instead of the whole package:

```python
bot.load_extension("commands.moderation")
```

This is useful during development when you want to test changes to just one module.

## Automatic discovery vs. explicit registration

By default, `load_extension` scans a module for all `CommandRouter` instances and registers them automatically.

If a module has only one router, this is fine:

```python
# commands/general.py
router = CommandRouter()

@router.command(...)
async def some_command(ctx): ...
```

If a module has multiple routers, you can be explicit:

```python
# commands/admin.py
from fastapi_interactions.commands import CommandRouter

mod_router = CommandRouter(name="moderation")
admin_router = CommandRouter(name="admin")

__routers__ = [mod_router, admin_router]

@mod_router.command(...)
async def warn(ctx): ...

@admin_router.command(...)
async def ban(ctx): ...
```

Define a `__routers__` list at module level containing the routers you want to register. If `__routers__` is present, the framework uses it. Otherwise, it scans the module for all `CommandRouter` instances.

## Router naming

Each router gets a name, either inferred or explicit. The name appears in logs when the router attaches, making it easy to see what got loaded:

```python
# Automatic naming (inferred from module path)
router = CommandRouter()
# name: "commands.general"

# Explicit naming
router = CommandRouter(name="my_commands")
# name: "my_commands"
```

For routers in the same module, use explicit names to avoid confusion:

```python
# commands/admin.py
mod_router = CommandRouter(name="moderation")
admin_router = CommandRouter(name="admin")
```

## Guild-scoped extensions

You can scope all commands in a router to a specific guild for rapid development iteration:

```python
# commands/dev.py
from fastapi_interactions.commands import CommandRouter

dev_router = CommandRouter(guild_id="123456789")

@dev_router.command(name="test", description="Test command")
async def test(ctx):
    return "Testing in the dev server!"
```

Guild-scoped commands appear instantly. When ready for production, create a separate router without `guild_id`:

```python
# commands/general.py
router = CommandRouter()

@router.command(name="test", description="Test command")
async def test(ctx):
    return "This is the production version!"
```

Both routers can coexist. When you sync commands with `bot.sync_commands()`, guild-scoped commands go to the guild endpoint and global commands go to the global endpoint.

## Syncing extensions

After you've created your extensions, sync them with Discord once during deployment:

```python
# sync_commands.py
from fastapi_interactions import Bot
from environs import env

env.read_env()

DISCORD_APP_ID = env.int("DISCORD_APP_ID")
DISCORD_PUBLIC_KEY = env.str("DISCORD_PUBLIC_KEY")
DISCORD_BOT_TOKEN = env.str("DISCORD_BOT_TOKEN")

bot = Bot(app_id=DISCORD_APP_ID, public_key=DISCORD_PUBLIC_KEY, bot_token=DISCORD_BOT_TOKEN)

bot.load_extension("commands")
bot.sync_commands()
```

Run this once:

```bash
python sync_commands.py
```

 Organizing large bots

For bots with many commands, consider grouping by feature:

```
commands/
├── general/
│   ├── __init__.py
│   ├── info.py
│   └── utility.py
├── moderation/
│   ├── __init__.py
│   ├── warns.py
│   └── bans.py
└── fun/
    ├── __init__.py
    └── games.py
```

Load subpackages the same way:

```python
bot.load_extension("commands.general")
bot.load_extension("commands.moderation")
bot.load_extension("commands.fun")
```

Or load the entire `commands/` package and all subpackages are discovered recursively.