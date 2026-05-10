from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import get_settings

ALGORITHM = "HS256"


class TokenError(Exception):
    pass


def create_access_token(subject: str, expires: timedelta | None = None) -> str:
    s = get_settings()
    expire = datetime.now(timezone.utc) + (expires or timedelta(minutes=s.jwt_expires_minutes))
    return jwt.encode({"sub": subject, "exp": expire}, s.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_settings().jwt_secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise TokenError(str(e)) from e
