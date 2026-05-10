from fastapi import Cookie, HTTPException, status
from app.core.security import TokenError, decode_token
from app.services.ai import get_ai_provider
from app.services.ai.provider import AIProvider

COOKIE_NAME = "cia_session"


def require_admin(cia_session: str | None = Cookie(default=None, alias=COOKIE_NAME)) -> str:
    if not cia_session:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not authenticated")
    try:
        payload = decode_token(cia_session)
    except TokenError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token") from e
    return payload["sub"]


def get_ai() -> AIProvider:
    return get_ai_provider()
