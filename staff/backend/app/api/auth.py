from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserOut
from app.services.auth import build_session_expiry, get_current_user
from app.services.security import generate_session_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _authenticate_user(identifier: str, password: str, db: Session) -> User | None:
    """Аутентификация по email или username."""
    # Сначала ищем по email
    user = db.execute(select(User).where(User.email == identifier)).scalar_one_or_none()
    if user and verify_password(password, user.password_hash):
        return user
    
    # Затем по username (для db-auth пользователей)
    user = db.execute(select(User).where(User.username == identifier)).scalar_one_or_none()
    if user:
        # Для db-auth пользователей проверяем plaintext пароль
        if user.password_plain and user.password_plain == password:
            return user
        # Или hashed пароль
        if verify_password(password, user.password_hash):
            return user
    
    return None


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    identifier = payload.email or payload.username
    if not identifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username required")
    
    user = db.execute(select(User).where(User.username == identifier)).scalar_one_or_none()
    
    if not user or user.password_plain != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate token and save to DB
    import base64
    import random
    random_bytes = bytes(random.randint(0, 255) for _ in range(32))
    token = base64.b64encode(random_bytes).decode("utf-8")
    
    from datetime import datetime, UTC
    session = UserSession(token=token, user_id=user.id, created_at=datetime.now(UTC))
    db.add(session)
    db.commit()

    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=settings.session_ttl_hours * 3600,
    )

    return LoginResponse(user_id=user.id, full_name=user.full_name, role=user.role)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    del current_user
    cookie_token = request.cookies.get(settings.session_cookie_name)
    if cookie_token:
        # Удаляем сессию по обоим полям (session_token и token)
        db.execute(
            delete(UserSession).where(
                or_(
                    UserSession.session_token == cookie_token,
                    UserSession.token == cookie_token
                )
            )
        )
    db.commit()
    response.delete_cookie(settings.session_cookie_name)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return current_user
