"""Middleware for verifying Discord webhook signatures.

Discord signs every interaction request with Ed25519. The middleware validates
the signature before the bot parses or acts on the payload, and stores the raw
body on ``request.state.raw_body`` for handlers that need it.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


def verify_signature(
    public_key: str, signature: str, timestamp: str, body: bytes
) -> bool:
    """Verify a Discord interaction signature.

    Args:
        public_key: The application's public key as a hex string.
        signature: The ``x-signature-ed25519`` header value.
        timestamp: The ``x-signature-timestamp`` header value.
        body: The raw request body that was signed.

    Returns:
        ``True`` if the signature is valid, otherwise ``False``.
    """
    try:
        VerifyKey(bytes.fromhex(public_key)).verify(
            timestamp.encode() + body, bytes.fromhex(signature)
        )
        return True
    except (BadSignatureError, ValueError):
        return False


class VerifySignatureMiddleware(BaseHTTPMiddleware):
    """Reject interaction requests whose Discord signature is invalid.

    Requests to paths other than ``interaction_path`` pass through unchanged.
    Valid interaction requests have their raw body stored on
    ``request.state.raw_body`` for downstream handlers.
    """

    def __init__(self, app, public_key: str, interaction_path: str = "/interactions"):
        super().__init__(app)
        self.public_key = public_key
        self.interaction_path = interaction_path

    async def dispatch(self, request: Request, call_next):
        if request.url.path != self.interaction_path:
            return await call_next(request)

        signature = request.headers["x-signature-ed25519"]
        timestamp = request.headers["x-signature-timestamp"]
        if not signature or not timestamp:
            return JSONResponse({"detail": "Missing headers"}, status_code=401)

        body = await request.body()
        verified_signature = verify_signature(
            public_key=self.public_key,
            signature=signature,
            timestamp=timestamp,
            body=body,
        )
        if not verified_signature:
            return JSONResponse({"detail": "Invalid signature"}, status_code=401)
        else:
            request.state.raw_body = body
            return await call_next(request)
