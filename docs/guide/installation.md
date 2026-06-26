# Installation

## Requirements

- Python 3.13+
- A Discord application with an interactions endpoint URL configured in the [Developer Portal](https://discord.com/developers/applications)

## Install

```bash
pip install fastapi-interactions
```

This pulls in FastAPI, Starlette, httpx, pydantic, and PyNaCl as dependencies. No other packages are required.

## Running locally

For local development you can take advantage of the fastapi cli

```bash
fastapi dev myapp.py
```

Discord requires a publicly reachable HTTPS URL to deliver interaction webhooks. For local development, [ngrok](https://ngrok.com) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) are both straightforward options:

```bash
ngrok http 8000
```

Paste the resulting `https://` URL into the **Interactions Endpoint URL** field in your Discord application's settings, appending your interactions path (default: `/interactions`):

```
https://your-ngrok-url.ngrok.io/interactions
```

Discord will send a PING to verify the endpoint before saving. Once it confirms, you're ready to receive interactions.
