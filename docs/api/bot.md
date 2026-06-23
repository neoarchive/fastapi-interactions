# Bot

The `Bot` class is the central object of every FastAPI Interactions app. It owns the FastAPI instance, the command registry, and the interactions endpoint.

## Usage

```python
from fastapi_interactions import Bot

bot = Bot(
    app_id=123456789,
    public_key="your_public_key",
    bot_token="Bot your_token",
)

bot.load_commands("commands")

app = bot.app
```

## Reference

### ::: fastapi_interactions.bot.Bot

---

### ::: fastapi_interactions.bot.call_with_options
    options:
        show_source: True
