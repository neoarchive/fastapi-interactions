# Integration Types

`IntegrationType` describes where an application command can be installed. Discord
calls this the command's **integration types**, and the selected values are sent in
the `integration_types` array when the command is registered.

`IntegrationType` is an `IntFlag`, so values can be combined with the `|` operator.
The framework converts the flags to Discord's integer array automatically.

## Values

| Member | Discord value | Description |
| --- | --- | --- |
| `IntegrationType.GUILD_INSTALL` | `0` | The command can be installed on a guild. |
| `IntegrationType.USER_INSTALL` | `1` | The command can be installed on a user account. |
| `IntegrationType.ALL` | `[0, 1]` | Shorthand for `GUILD_INSTALL \| USER_INSTALL`. |

## Usage

Pass integration types to a `CommandRouter` when the commands should be available
outside the default installation context:

```python
from fastapi_interactions import CommandRouter
from fastapi_interactions.models import IntegrationType

router = CommandRouter(
    integration_types=IntegrationType.GUILD_INSTALL | IntegrationType.USER_INSTALL,
)
```

`IntegrationType.ALL` is equivalent to the expression above:

```python
router = CommandRouter(integration_types=IntegrationType.ALL)
```

!!! note
    Integration types and interaction contexts only apply to **global** commands.
    A router created with `guild_id=...` cannot also set `integration_types` or
    `contexts`; the framework raises `ValueError` instead of registering an
    invalid command.

## Reference

::: fastapi_interactions.models.IntegrationType
    options:
      show_source: true
