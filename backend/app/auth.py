from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import ADMIN_LOGIN, ADMIN_PASSWORD, JWT_SECRET


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=24)
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict[str, Any]:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except JWTError as exc:
        raise credentials_error from exc

    if payload.get("sub") != ADMIN_LOGIN:
        raise credentials_error

    return payload


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    return verify_token(token)


def authenticate_user(username: str, password: str) -> bool:
    return username == ADMIN_LOGIN and password == ADMIN_PASSWORD
