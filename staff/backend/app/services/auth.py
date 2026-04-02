from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.session import UserSession
from app.models.user import User


def _get_session_by_portal_token(token: str, db: Session) -> tuple[UserSession | None, User | None]:
    """Проверка сессии Staff Portal (по session_token с expires_at)."""
    stmt = (
        select(UserSession, User)
        .join(User, UserSession.user_id == User.id)
        .where(
            UserSession.session_token == token,
            UserSession.expires_at.is_not(None),
            UserSession.expires_at > datetime.utcnow()
        )
    )
    result = db.execute(stmt).first()
    if result:
        return result[0], result[1]
    return None, None


def _get_session_by_dbauth_token(token: str, db: Session) -> tuple[UserSession | None, User | None]:
    """Проверка сессии db-auth (по token с TTL 24ч от created_at)."""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    stmt = (
        select(UserSession, User)
        .join(User, UserSession.user_id == User.id)
        .where(
            UserSession.token == token,
            UserSession.created_at > cutoff
        )
    )
    result = db.execute(stmt).first()
    if result:
        return result[0], result[1]
    return None, None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    session_token = request.cookies.get(settings.session_cookie_name)
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Пробуем Staff Portal формат
    session, user = _get_session_by_portal_token(session_token, db)
    
    # Если не нашли, пробуем db-auth формат
    if not session or not user:
        session, user = _get_session_by_dbauth_token(session_token, db)
    
    if not session or not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    # Проверка expires_at для Staff Portal сессий
    if session.expires_at and session.expires_at <= datetime.utcnow():
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def require_privileged(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"admin", "senior_dev"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Privileged access required")
    return user


def build_session_expiry() -> datetime:
    return datetime.utcnow() + timedelta(hours=settings.session_ttl_hours)
