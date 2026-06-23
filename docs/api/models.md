# Models

Pydantic models for parsing Discord's interaction payloads. These are used internally by the framework — you'll interact with them primarily through `ctx.interaction` and `ctx.options`.

The top-level envelope Discord sends to your interactions endpoint for every event.

## Reference
### ::: fastapi_interactions.models.Interaction

---

### ::: fastapi_interactions.models.InteractionType

---

The `data` field of an `APPLICATION_COMMAND` interaction, parsed into a typed model.

### ::: fastapi_interactions.models.ApplicationCommandData

---

A single option value supplied by the user when invoking a command. May nest further options for subcommand interactions.

### ::: fastapi_interactions.models.CommandInteractionOption

---

### ::: fastapi_interactions.models.ApplicationCommandOptionType

---

### ::: fastapi_interactions.models.Member

---

### ::: fastapi_interactions.models.User

---

`Context` is constructed by the framework for each incoming interaction and passed as the first argument to every command callback.

### ::: fastapi_interactions.models.Context
