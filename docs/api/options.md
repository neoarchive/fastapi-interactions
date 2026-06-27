# Options
 
The `Option` class provides type-safe decorators for registering command options. Each static method corresponds to a Discord option type and ensures type correctness at the Python level.
 
## Using options
 
Options are registered using `Option` static methods as decorators on command callbacks:
 
```python
from fastapi_interactions.commands import CommandRouter, Option
 
@router.command(name="greet", description="Greet someone")
@Option.string(name="name", description="Who to greet", required=True)
async def greet(ctx, name: str):
    return f"Hello, {name}!"
```
 
The parameter name in your function must match the option name. The framework automatically binds option values to function parameters.
 
## Available options
 
### String options
 
```python
@Option.string(name="text", description="Some text", required=True)
```
 
Accepts any text input. Default option type if no specific type is needed.
 
### Integer options
 
```python
@Option.integer(name="count", description="A number", required=True)
```
 
Accepts whole numbers only. Discord enforces integer validation client-side.
 
### Number options
 
```python
@Option.number(name="price", description="A decimal", required=True)
```
 
Accepts decimal numbers (floats). Use for prices, ratings, percentages, or any fractional value.
 
### Boolean options
 
```python
@Option.boolean(name="enabled", description="Toggle this", required=True)
```
 
Presents a true/false toggle to the user.
 
### User options
 
```python
@Option.user(name="target", description="Pick a user", required=True)
```
 
Discord's user picker. The parameter receives a snowflake ID (string) of the selected user.
 
### Channel options
 
```python
@Option.channel(name="target", description="Pick a channel", required=True)
```
 
Discord's channel picker. The parameter receives a snowflake ID (string) of the selected channel.
 
### Role options
 
```python
@Option.role(name="role", description="Pick a role", required=True)
```
 
Discord's role picker. The parameter receives a snowflake ID (string) of the selected role.
 
### Mentionable options
 
```python
@Option.mentionable(name="target", description="User or role", required=True)
```
 
Combines user and role pickers. The parameter receives a snowflake ID (string) that can be either a user or role.
 
## Reference
 
::: fastapi_interactions.commands.Option
    options:
      show_source: true