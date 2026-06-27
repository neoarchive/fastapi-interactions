# Commands

Commands are the core of your Discord bot — they're the slash commands users see and invoke.

## Defining a command

Use a `CommandRouter` and the `@command` decorator:

```python
from fastapi_interactions.commands import CommandRouter

router = CommandRouter()

@router.command(name="ping", description="Check bot latency")
async def ping(ctx):
    return "Pong!"
```

Every command is an async function that receives a `Context` object (`ctx`) as its first parameter. The context provides access to the invoking user, the guild/channel where the command was invoked, and the options they supplied.

Register the router with your bot:

```python
bot.attach_router(router)
```

## Adding options

Options are the parameters users fill in when invoking a command. Use the `Option` class with type-specific static methods:

```python
from fastapi_interactions.commands import CommandRouter, Option

@router.command(name="greet", description="Greet someone")
@Option.string(name="name", description="Who to greet", required=True)
async def greet(ctx, name: str):
    return f"Hello, {name}!"
```

The parameter name in your function (`name: str`) must match the option name you register (`name="name"`). This is how the framework automatically binds option values to function parameters.

### Multiple options

```python
@router.command(name="calculate", description="Add two numbers")
@Option.integer(name="a", description="First number", required=True)
@Option.integer(name="b", description="Second number", required=True)
async def calculate(ctx, a: int, b: int):
    return f"{a} + {b} = {a + b}"
```

Option values are passed directly to your function as keyword arguments. No manual lookups needed.

### Optional options

Use Python's default parameter syntax:

```python
@router.command(name="search", description="Search for something")
@Option.string(name="query", description="What to search for", required=True)
@Option.integer(name="limit", description="Result limit", required=False)
async def search(ctx, query: str, limit: int = 10):
    return f"Searching for {query!r} (limit: {limit})"
```

Required options must be declared before optional ones. Discord rejects command registrations that violate this ordering.

### Available option types

Each option type has a corresponding `Option` static method:

| Method | Type | Python type |
|---|---|---|
| `Option.string()` | STRING | `str` |
| `Option.integer()` | INTEGER | `int` |
| `Option.number()` | NUMBER | `float` |
| `Option.boolean()` | BOOLEAN | `bool` |
| `Option.user()` | USER | `str` (snowflake) |
| `Option.channel()` | CHANNEL | `str` (snowflake) |
| `Option.role()` | ROLE | `str` (snowflake) |
| `Option.mentionable()` | MENTIONABLE | `str` (snowflake) |

```python
from fastapi_interactions.commands import CommandRouter, Option

@router.command(name="configure", description="Configure settings")
@Option.integer(name="count", description="How many", required=True)
@Option.boolean(name="enabled", description="Enable it", required=True)
async def configure(ctx, count: int, enabled: bool):
    return f"Count: {count}, Enabled: {enabled}"
```

## Accessing context

The `ctx` parameter gives you information about the interaction:

```python
@router.command(name="whoami", description="Who are you")
async def whoami(ctx):
    user = ctx.user.username
    guild = ctx.guild_id or "DM"
    channel = ctx.channel_id or "N/A"
    return f"You're {user} in {guild}:{channel}"
```

**`ctx.user`** — The user who invoked the command (always available).

**`ctx.guild_id`** — The ID of the guild, or `None` if invoked in a DM.

**`ctx.channel_id`** — The ID of the channel where the command was invoked.

**`ctx.get_option_value(name, default=None)`** — Look up an option value by name. Used for dynamic lookups when you need to check if an optional option was provided:

```python
@router.command(name="config", description="Configure settings")
@Option.string(name="setting", description="Setting name", required=True)
@Option.string(name="value", description="Setting value", required=False)
async def config(ctx, setting: str):
    value = ctx.get_option_value("value")
    if value is None:
        return f"Current {setting}: (not set)"
    return f"Set {setting} to {value}"
```

## Returning responses

The simplest response is a plain string:

```python
@router.command(name="hello", description="Say hello")
async def hello(ctx):
    return "Hello!"
```

For more control, return a response object. See [Responses](responses.md) for the full reference.

## Decorator order

Decorators stack bottom-up. Make sure `@Option.*()` appears **below** `@router.command()`:

```python
@router.command(name="echo", description="Echo text")
@Option.string(name="text", description="Text to echo", required=True)
async def echo(ctx, text: str):
    return text
```

If you put `@router.command()` on the bottom, the decorators run in the wrong order and your options won't be attached.