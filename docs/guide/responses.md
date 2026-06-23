# Responses

Commands can respond to interactions in several ways. The simplest is returning a plain string; for more control, return a response object.

## Plain string

```python
async def ping(ctx):
    return "Pong!"
```

The framework wraps this in a `MessageResponse` automatically.

## MessageResponse

Sends a message visible to everyone in the channel by default.

```python
from fastapi_interactions.responses import MessageResponse

async def ping(ctx):
    return MessageResponse("Pong!")
```

### Ephemeral messages

An ephemeral message is only visible to the user who invoked the command.

```python
return MessageResponse("Only you can see this.", ephemeral=True)
```

## DeferResponse

Use `DeferResponse` when your command needs more than Discord's 3-second response window to complete its work. Discord shows a "thinking..." indicator to the user while you finish processing, and you then deliver the real response as a followup via `ctx.send()`.

```python
from fastapi_interactions.responses import DeferResponse

async def slow_command(ctx):
    await ctx.defer()
    result = await some_slow_operation()
    await ctx.send(result)
```

Returning `DeferResponse` directly is equivalent:

```python
return DeferResponse()
```

Ephemeral defers are supported — the final response inherits the ephemeral state set at defer time:

```python
return DeferResponse(ephemeral=True)
```

!!! warning
    Once deferred, the ephemeral state is locked. Passing `ephemeral=False` to a later `ctx.send()` has no effect if the defer was ephemeral.

## Response reference

| Class | Discord type | Use when |
|---|---|---|
| `MessageResponse` | `4` | Replying immediately with a message |
| `DeferResponse` | `5` | Acknowledging while work continues |
| `UpdateMessageResponse` | `7` | Updating the message a component is attached to |
| `AutocompleteResponse` | `8` | Returning autocomplete choices |
| `ModalResponse` | `9` | Opening a modal dialog |
