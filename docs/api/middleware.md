# Middleware

Verifies the Ed25519 signature on every incoming request before it reaches the interactions endpoint. Discord requires this — requests that fail verification are rejected with a `401` response.

The raw request body is read once here and stored on `request.state.raw_body` for the route handler to consume directly, avoiding the need to re-read the stream downstream.

!!! note
    This middleware is added automatically when you instantiate `Bot`. You do not need to add it manually.

## Reference
### ::: fastapi_interactions.middleware.VerifySignatureMiddleware
