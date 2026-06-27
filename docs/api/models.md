# Models

Pydantic models for parsing Discord's interaction payloads. These represent the data Discord sends to your interactions endpoint and the context available to command handlers.

## Enumerations

### InteractionType

Identifies what kind of interaction Discord is sending.

::: fastapi_interactions.models.InteractionType
    options:
      show_source: true

### CommandType

Specifies the type of application command.

::: fastapi_interactions.models.CommandType
    options:
      show_source: true

### InteractionCallbackType

The response type sent back to Discord. Includes shorter aliases for common types.

::: fastapi_interactions.models.InteractionCallbackType
    options:
      show_source: true

### ApplicationCommandOptionType

Describes the type of value an option accepts.

::: fastapi_interactions.models.ApplicationCommandOptionType
    options:
      show_source: true

### MessageFlags

Bit flags describing special message properties. Used to mark messages as ephemeral, loading, or with other special states.

::: fastapi_interactions.models.MessageFlags
    options:
      show_source: true

## Discord Payloads

These models represent data structures sent by Discord in interaction webhooks.

### User

Minimal user information — the member who invoked the command.

::: fastapi_interactions.models.User
    options:
      show_source: true

### Member

Guild member information, including roles and permissions. Present when a command is invoked in a guild.

::: fastapi_interactions.models.Member
    options:
      show_source: true

### Interaction

The top-level envelope Discord sends to your interactions endpoint. Contains the interaction type, token, data, and context about who invoked it and where.

::: fastapi_interactions.models.Interaction
    options:
      show_source: true

## Command Data

### ApplicationCommandData

The `data` field of an `APPLICATION_COMMAND` interaction, parsed into a typed model. Contains the command name, options supplied by the user, and metadata about which guild/channel it was invoked in.

::: fastapi_interactions.models.ApplicationCommandData
    options:
      show_source: true

### ApplicationCommandInteractionOption

A single option value supplied by the user when invoking a command. May nest further options for subcommand interactions.

::: fastapi_interactions.models.ApplicationCommandInteractionOption
    options:
      show_source: true
