# Context

Every command callback receives a `ctx` argument — a `Context` object that wraps the incoming interaction and provides access to who invoked it, where, and with what options.

## Accessing the invoking user

```python
async def whoami(ctx):
    return f"You are {ctx.user.username}!"
```

`ctx.user` resolves correctly whether the command was invoked in a guild (where Discord sends `member.user`) or a DM (where Discord sends `user` directly).

## Accessing guild and channel

```python
async def where(ctx):
    if ctx.guild_id:
        return f"You're in guild {ctx.guild_id}, channel {ctx.channel_id}."
    return "You're in a DM."
```

Both `guild_id` and `channel_id` are `Optional[str]` — `guild_id` is `None` for DM interactions.

## Reading option values

Options are accessed via `ctx.options`, which is the parsed `ApplicationCommandData` for this interaction:

```python
async def echo(ctx):
    text = ctx.options.get_option_value("text")
    return text
```

`get_option_value` returns `None` if the option wasn't provided. Pass a `default` to control the fallback:

```python
count = ctx.options.get_option_value("count", default=1)
```

## Deferring

If your command needs more than 3 seconds to respond, defer immediately and send the real response when ready:

```python
async def slow(ctx):
    await ctx.defer()
    data = await fetch_something_slow()
    await ctx.send(data)
```

`await ctx.defer()` stages a `DeferResponse` that the framework returns to Discord as the initial ack. `await ctx.send(...)` then delivers the real content as a followup once the work is done.

For commands where the response should only be visible to the invoking user:

```python
await ctx.defer(ephemeral=True)
```

!!! warning "Ephemeral state is set at defer time"
    The ephemeral flag passed to `ctx.defer()` is locked in the moment Discord receives the initial ack. A later `ctx.send(..., ephemeral=False)` won't make the response public.

## Sending a followup

After responding (or deferring), you can send additional messages to the same interaction:

```python
async def multi(ctx):
    await ctx.send("First message.")
    await ctx.send("Second message.")
```

!!! note
    `ctx.send()` makes an outbound HTTP call to Discord's followup endpoint for every call after the first. Keep this in mind on serverless platforms where response time matters.
