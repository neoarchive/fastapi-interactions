# Integration Types and Interaction Contexts

When you register a global command, Discord lets you control two separate things:

- **Integration types** — where users can *install* the app and its commands.
- **Interaction contexts** — where users can *invoke* the command after it is installed.

The framework exposes these as `IntegrationType` and `InteractionContext`. Both are
bit flags, so you can combine values with `|`.

## Integration types

`IntegrationType` maps to Discord's `integration_types` command field.

| Value | Discord value | Meaning |
| --- | --- | --- |
| `IntegrationType.GUILD_INSTALL` | `0` | Install and use the command on a guild. |
| `IntegrationType.USER_INSTALL` | `1` | Install and use the command on a user account. |
| `IntegrationType.ALL` | `[0, 1]` | Both installation surfaces. |

## Interaction contexts

`InteractionContext` maps to Discord's `contexts` command field.

| Value | Discord value | Meaning |
| --- | --- | --- |
| `InteractionContext.GUILD` | `0` | Guild channels. |
| `InteractionContext.BOT_DM` | `1` | Direct messages with the bot. |
| `InteractionContext.PRIVATE_CHANNEL` | `2` | Private channels such as group DMs. |
| `InteractionContext.ALL` | `[0, 1, 2]` | Every supported context. |

## Using the enums with a router

Pass the flags when you create a `CommandRouter`. Every command registered on that
router inherits the settings:

```python
from fastapi_interactions import CommandRouter, Option
from fastapi_interactions.models import IntegrationType, InteractionContext

router = CommandRouter(
    integration_types=IntegrationType.GUILD_INSTALL | IntegrationType.USER_INSTALL,
    contexts=InteractionContext.GUILD | InteractionContext.BOT_DM,
)


@router.command(name="profile", description="Show your profile")
async def profile(ctx):
    return f"Hello, {ctx.user.username}!"
```

The `ALL` members are convenient shorthands:

```python
router = CommandRouter(
    integration_types=IntegrationType.ALL,
    contexts=InteractionContext.ALL,
)
```

Combining flags works because both enums are `IntFlag` subclasses. When commands are
synced, the framework calls each flag's `to_api()` helper and sends the resulting
integer list to Discord. You do not need to build the payload yourself.

## Common configurations

### Guild-only command

Allow installation on guilds and invocation in guild channels:

```python
router = CommandRouter(
    integration_types=IntegrationType.GUILD_INSTALL,
    contexts=InteractionContext.GUILD,
)
```

### User-installable command

Allow installation on user accounts and invocation in DMs and private channels:

```python
router = CommandRouter(
    integration_types=IntegrationType.USER_INSTALL,
    contexts=InteractionContext.BOT_DM | InteractionContext.PRIVATE_CHANNEL,
)
```

### Available everywhere

```python
router = CommandRouter(
    integration_types=IntegrationType.ALL,
    contexts=InteractionContext.ALL,
)
```

### Leave the defaults to Discord

Omit both arguments to let Discord apply the defaults configured for your
application:

```python
router = CommandRouter()
```

## Guild-scoped commands

`integration_types` and `contexts` only apply to **global** commands. A router
created with `guild_id=...` is guild-scoped, so combining it with either setting is
invalid:

```python
# Raises ValueError
router = CommandRouter(
    guild_id="123456789",
    integration_types=IntegrationType.ALL,
)
```

Create a separate global router if you need integration types or contexts. See the
[Commands reference](../api/commands.md#guild-commands) for more about guild-scoped
commands.

## API reference

- [Integration Types](../api/integration_types.md)
- [Interaction Contexts](../api/interaction_contexts.md)
