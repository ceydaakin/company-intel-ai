import pytest
from datetime import timedelta
from app.core.security import create_access_token, decode_token, TokenError


def test_round_trip_token():
    token = create_access_token(subject="admin", expires=timedelta(minutes=5))
    payload = decode_token(token)
    assert payload["sub"] == "admin"


def test_decode_rejects_garbage():
    with pytest.raises(TokenError):
        decode_token("not-a-real-token")
