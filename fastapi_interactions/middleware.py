from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


def verify_signature(public_key: str, signature: str, timestamp: str, body: bytes) -> bool:
    try:
        VerifyKey(bytes.fromhex(public_key)).verify(
            timestamp.encode() + body,
            bytes.fromhex(signature)
        )
        return True
    except (BadSignatureError, ValueError):
        return False


class VerifySignatureMiddleware(BaseHTTPMiddleware):
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
            body=body
        )
        if not verified_signature:
            return JSONResponse({"detail": "Invalid signature"}, status_code=401)
        else:
            request.state.raw_body = body
            return await call_next(request)
