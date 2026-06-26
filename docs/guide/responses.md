# Responses

Commands respond to interactions in several ways. The framework handles all the low-level Discord protocol details — you just return what you want to say.

## Plain string

The simplest response is a plain string:

```python
@router.command(name="ping", description="Check bot latency")
async def ping(ctx):
    return "Pong!"
```

The framework automatically wraps this in a `MessageResponse` and sends it back to Discord.

## MessageResponse

For more control, return a `MessageResponse` explicitly:

```python
from fastapi_interactions.responses import MessageResponse

@router.command(name="hello", description="Say hello")
async def hello(ctx):
    return MessageResponse(f"Hello, {ctx.user.username}!")
```

### Ephemeral messages

Ephemeral messages are only visible to the user who invoked the command:

```python
@router.command(name="secret", description="A secret message")
async def secret(ctx):
    return MessageResponse("Only you can see this.", ephemeral=True)
```

## DeferResponse

Use `DeferResponse` when your command needs to do work that takes longer than Discord's 3-second response window. The framework acknowledges the interaction immediately with a "thinking..." indicator, then runs your work in the background.

### How it works

1. Your command returns `DeferResponse`
2. The framework sends the defer acknowledgement to Discord within 3 seconds
3. Discord shows "thinking..." to the user
4. Your `finish` function runs in the background
5. Once the work is done, call `ctx.send()` to deliver the actual response

### Example

```python
import asyncio
from fastapi_interactions.responses import DeferResponse

@router.command(name="slow", description="A slow command")
async def slow(ctx):
    async def finish():
        # Do slow work here — fetching data, calling APIs, etc.
        await asyncio.sleep(10)  # simulate slow operation
        await ctx.send("Done! Here's your result.")
    
    return DeferResponse(finish=finish)
```

When a user invokes `/slow`:
1. They immediately see "thinking..." (the defer)
2. Your command's `finish` function runs in the background
3. After 10 seconds, they see "Done! Here's your result."

### Ephemeral defers

Defer ephemeral messages the same way:

```python
return DeferResponse(ephemeral=True, finish=finish)
```

!!! warning "Ephemeral state is locked"
    The ephemeral flag is set at defer time. A later `ctx.send(..., ephemeral=False)` will still produce an ephemeral message if you deferred with `ephemeral=True`.

### Multiple followups

You can call `ctx.send()` multiple times in a `finish` function:

```python
async def finish():
    await asyncio.sleep(5)
    await ctx.send("First message.")
    await asyncio.sleep(5)
    await ctx.send("Second message.")
    await ctx.send("Third message.")
```

Each call sends a separate message.

## Accessing context in finish

The `finish` function is a closure that has access to `ctx`:

```python
@router.command(name="personalized", description="Personalized message")
async def personalized(ctx):
    async def finish():
        user = ctx.user.username
        await ctx.send(f"This is personalized for {user}!")
    
    return DeferResponse(finish=finish)
```

This works because `ctx` is captured from the enclosing scope.

## Other response types

| Response type | When to use |
|---|---|
| `MessageResponse` | Reply immediately with a message |
| `DeferResponse` | Acknowledge while doing async work |
| `UpdateMessageResponse` | Update a message that a component is attached to (for buttons/selects) |
| `AutocompleteResponse` | Provide autocomplete choices for an option |
| `ModalResponse` | Open a modal dialog |
| `PongResponse` | Respond to a PING (automatic, you don't need to use this) |

Full API documentation is available in the [API reference](../api/responses.md).