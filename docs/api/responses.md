All response classes inherit from `InteractionResponse` and implement `to_dict()`, which produces the JSON payload Discord expects.

## Usage

```python
@router.command('username')
async def return_username(ctx):
    return MessageResponse(f'Hello {ctx.user.username}', ephemeral=True)
```

## Reference

### ::: fastapi_interactions.responses.InteractionResponse

---

### ::: fastapi_interactions.responses.MessageResponse

---

### ::: fastapi_interactions.responses.DeferResponse

<!--
---

## UpdateMessageResponse

::: fastapi_interactions.responses.UpdateMessageResponse

---

## AutocompleteResponse

::: fastapi_interactions.responses.AutocompleteResponse

---

## ModalResponse

::: fastapi_interactions.responses.ModalResponse

--- -->

### ::: fastapi_interactions.responses.MessageFlags