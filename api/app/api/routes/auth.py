from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.api.deps import COOKIE_NAME, require_admin
from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, MeResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(payload: LoginRequest, response: Response) -> Response:
    s = get_settings()
    if payload.username != s.admin_username or payload.password != s.admin_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    token = create_access_token(subject=payload.username)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # set True behind HTTPS
        max_age=s.jwt_expires_minutes * 60,
        path="/",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(COOKIE_NAME, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=MeResponse)
def me(username: str = Depends(require_admin)) -> MeResponse:
    return MeResponse(username=username)
