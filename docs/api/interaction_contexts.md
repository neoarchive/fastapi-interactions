# Interaction Contexts

`InteractionContext` describes where an application command can be invoked. Discord
calls these the command's **contexts**, and the selected values are sent in the
`contexts` array when the command is registered.

`InteractionContext` is an `IntFlag`, so values can be combined with the `|`
operator. The framework converts the flags to Discord's integer array automatically.

## Values

| Member | Discord value | Description |
| --- | --- | --- |
| `InteractionContext.GUILD` | `0` | Usable in guild channels. |
| `InteractionContext.BOT_DM` | `1` | Usable in direct messages with the bot. |
| `InteractionContext.PRIVATE_CHANNEL` | `2` | Usable in private channels such as group DMs. |
| `InteractionContext.ALL` | `[0, 1, 2]` | Shorthand for all supported contexts. |

## Usage

Pass contexts to a `CommandRouter` to control where its commands can be invoked:

```python
from fastapi_interactions import CommandRouter
from fastapi_interactions.models import InteractionContext

router = CommandRouter(
    contexts=InteractionContext.GUILD | InteractionContext.BOT_DM,
)
```

`InteractionContext.ALL` allows every supported context:

```python
router = CommandRouter(contexts=InteractionContext.ALL)
```

!!! note
    Interaction contexts only apply to **global** commands. A router created with
    `guild_id=...` cannot also set `contexts` or `integration_types`; the
    framework raises `ValueError` instead of registering an invalid command.

## Reference

::: fastapi_interactions.models.InteractionContext
    options:
      show_source: true
