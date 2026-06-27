# Commands

`CommandRouter` decouples command declaration from the `Bot` instance. Each command module creates its own router and registers commands against it. The bot merges routers into its registry via `attach_router` or `load_extension`.

## Usage

```python
from fastapi_interactions import CommandRouter

router = CommandRouter()

@router.command(name="ping", description="Check bot latency")
async def ping(ctx):
    return "Pong!"
```

## Guild Commands

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
from fastapi_interactions import CommandRouter

prod_router = CommandRouter()

@prod_router.command(name="test", description="A test command")
async def test(ctx):
    return "This command is global."
```

Both routers can coexist:

```python
bot.include_router(dev_router)
bot.include_router(prod_router)
```

When syncing with `bot.sync_commands()`, guild-scoped commands are sent to the guild endpoint while global commands are sent to the global endpoint.

## Reference

### ::: fastapi_interactions.commands.CommandRouter

### ::: fastapi_interactions.commands.Option

### ::: fastapi_interactions.commands.Command

### ::: fastapi_interactions.commands.CommandMeta

### ::: fastapi_interactions.commands.CommandOption