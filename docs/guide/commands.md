# Commands

## Defining a command

Commands are defined using a `CommandRouter`. Each module in your commands package creates its own router and decorates functions against it.

```python
from fastapi_interactions import CommandRouter

router = CommandRouter()

@router.command(name="ping", description="Check bot latency")
async def ping(ctx):
    return "Pong!"
```

`bot.load_extension("commands")` discovers and registers all routers automatically. You can also register a router directly:

```python
bot.attach_router(router)
```

## Adding options

Options are the parameters a user fills in when invoking a slash command. Decorate below `@router.command`:

```python
@router.command(name="echo", description="Echo a message back")
@router.option(name="text", description="The text to echo", required=True)
async def echo(ctx, text: str):
    return f"Your phrase is {text!r}"
```

Option values are automatically bound to matching parameters in your function signature. The dispatcher inspects the callback's parameters and fills in values from the interaction data — no manual lookups needed.

!!! note "Decorator order"
    `@router.option` must appear **below** `@router.command`. Python executes decorators bottom-up, so options are attached to the function before the command decorator reads them.

### Multiple options

```python
@router.command(name="greet", description="Greet someone")
@router.option(name="name", description="Who to greet", required=True)
@router.option(name="greeting", description="Custom greeting", required=False)
async def greet(ctx, name: str, greeting: str = "Hello"):
    return f"{greeting}, {name}!"
```

Parameter names must match registered option names exactly. Discord rejects command registrations where optional options appear before required ones.

### Option types

The `type` parameter maps to Discord's [application command option types](https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-type).

| Type value | Discord type | Python value |
|---|---|---|
| `3` (default) | `STRING` | `str` |
| `4` | `INTEGER` | `int` |
| `10` | `NUMBER` | `float` |
| `5` | `BOOLEAN` | `bool` |
| `6` | `USER` | snowflake `str` |
| `7` | `CHANNEL` | snowflake `str` |
| `8` | `ROLE` | snowflake `str` |

```python
@router.option(name="count", description="How many times", type=4, required=True)
async def repeat(ctx, count: int):
    return f"Repeating {count} times."
```

## Reading option values programmatically

Most of the time, you access options through the function signature. For dynamic lookups — checking which options were actually provided, reading nested subcommand options — use `ctx.get_option_value()`:

```python
@router.command(name="config", description="Configure settings")
@router.option(name="setting", description="Which setting", required=True)
@router.option(name="value", description="New value", required=False)
async def config(ctx, setting: str):
    value = ctx.get_option_value("value")
    if value is None:
        return f"Current value for {setting}: (not set)"
    return f"Set {setting} to {value}"
```

`ctx.get_option_value()` returns `None` if the option wasn't provided. Pass a `default` to use a fallback:

```python
count = ctx.get_option_value("count", default=1)
```

## Returning a response

The simplest response is a plain string:

```python
async def ping(ctx):
    return "Pong!"
```

For more control, return a response object directly. See [Responses](responses.md).

## Command loading

`bot.load_extension("commands")` walks the given package and merges every module's routers into the bot's command registry:

```python
bot.load_extension("commands")
```

Each module can expose routers in two ways.

### Explicit registration

Define a `__routers__` list at module level containing the routers you want to register:

```python
# commands/general.py
from fastapi_interactions import CommandRouter

router1 = CommandRouter(name="ping")
router2 = CommandRouter(name="echo")

__routers__ = [router1, router2]

@router1.command(...)
async def some_command(ctx): ...
```

### Automatic discovery

If `__routers__` is not defined, `load_extension` scans the module for all `CommandRouter` instances and registers them automatically:

```python
# commands/general.py
from fastapi_interactions import CommandRouter

router = CommandRouter()

@router.command(...)
async def some_command(ctx): ...
```

The router is discovered and registered without needing an explicit `__routers__` list.

You can also load a single module directly:

```python
bot.load_extension("commands.admin")
```

If a module contains no routers and no `__routers__` attribute, a warning is logged and the module is skipped.

## Guild commands

Commands can be scoped to a specific guild for instant propagation during development. Global commands can take up to an hour to appear everywhere, making guild-scoped commands ideal for testing.

Pass a `guild_id` when creating the router:

```python
from fastapi_interactions import CommandRouter

dev_router = CommandRouter(guild_id="123456789")

@dev_router.command(name="test", description="A test command")
async def test(ctx):
    return "This command only exists in the test server."
```

Guild-scoped commands appear immediately in the specified server. When ready for production, create a separate router without a `guild_id`:

```python
prod_router = CommandRouter()

@prod_router.command(name="test", description="A test command")
async def test(ctx):
    return "This command is global."
```

Both routers can coexist — `bot.include_router(dev_router)` and `bot.include_router(prod_router)` will register commands to both their respective scopes. When syncing with `bot.sync_commands()`, guild-scoped commands are PUT to the guild endpoint, and global commands to the global endpoint.