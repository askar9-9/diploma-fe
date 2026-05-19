from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status

from backend.app.auth import authenticate_user, create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest) -> dict[str, str]:
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token({"sub": payload.username})
    return {"access_token": token, "token_type": "bearer"}
