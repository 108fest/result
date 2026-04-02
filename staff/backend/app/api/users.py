from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import KPIUpdateRequest, UserOut
from app.services.auth import get_current_user, require_admin, require_privileged

router = APIRouter(prefix="/users", tags=["users"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/me", response_model=UserOut)
def my_profile(current_user: User = Depends(get_current_user)) -> UserOut:
    return current_user


@router.get("/assignable", response_model=list[UserOut])
def get_assignable_users(privileged_user: User = Depends(require_privileged), db: Session = Depends(get_db)) -> list[UserOut]:
    allowed_roles = ["junior_dev"]
    if privileged_user.role == "admin":
        allowed_roles.append("senior_dev")
        allowed_roles.append("admin")

    stmt = select(User).where(User.role.in_(allowed_roles)).order_by(User.full_name)
    return list(db.execute(stmt).scalars())


@router.get("/{user_id}", response_model=UserOut)
def get_user_profile(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserOut:
    target_user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role != "admin" and current_user.id != target_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return target_user


@admin_router.get("/users", response_model=list[UserOut])
def admin_users(_admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[UserOut]:
    stmt = select(User).order_by(User.id)
    return list(db.execute(stmt).scalars())


@admin_router.get("/promotions/pending", response_model=list[UserOut])
def pending_promotions(_admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[UserOut]:
    stmt = select(User).where(User.promotion_requested.is_(True)).order_by(User.promotion_requested_at)
    return list(db.execute(stmt).scalars())


@admin_router.patch("/users/{user_id}/kpi", response_model=UserOut)
def update_user_kpi(
    user_id: int,
    payload: KPIUpdateRequest,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserOut:
    if payload.kpi_score < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="KPI must be non-negative")

    target_user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    target_user.kpi_score = payload.kpi_score
    db.add(target_user)
    db.commit()
    db.refresh(target_user)
    return target_user
