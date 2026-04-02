from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.admin_settings import AdminSettings
from app.models.user import User
from app.schemas.promotion import AutoApproveSettingsOut, AutoApproveSettingsUpdate, PromotionRequestOut
from app.schemas.user import UserOut, UserRoleUpdateRequest
from app.services.auth import get_current_user, require_admin

router = APIRouter(prefix="/promotions", tags=["promotions"])
admin_promotions_router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)


def _get_or_create_settings(db: Session) -> AdminSettings:
    settings = db.execute(select(AdminSettings).where(AdminSettings.id == 1)).scalar_one_or_none()
    if settings:
        return settings

    settings = AdminSettings(id=1, auto_approve_promotions=False)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


@router.post("/request", response_model=PromotionRequestOut)
def request_promotion(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> PromotionRequestOut:
    if current_user.role != "junior_dev":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only junior developers can request promotion")

    if current_user.kpi_score < 100:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="KPI 100 is required")

    settings = _get_or_create_settings(db)
    current_user.promotion_requested = True
    current_user.promotion_requested_at = datetime.utcnow()

    if settings.auto_approve_promotions:
        current_user.role = "senior_dev"
        current_user.promotion_requested = False
        current_user.promotion_requested_at = None
        status_value = "approved"
    else:
        status_value = "pending"

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return PromotionRequestOut(status=status_value, requested_at=current_user.promotion_requested_at)


@router.get("/status", response_model=PromotionRequestOut)
def promotion_status(current_user: User = Depends(get_current_user)) -> PromotionRequestOut:
    if current_user.role == "senior_dev":
        return PromotionRequestOut(status="approved", requested_at=None)

    if current_user.promotion_requested:
        return PromotionRequestOut(status="pending", requested_at=current_user.promotion_requested_at)

    return PromotionRequestOut(status="none", requested_at=None)


@admin_promotions_router.post("/users/{user_id}/promote", response_model=UserOut)
def approve_promotion(
    user_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserOut:
    target_user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target_user.role != "junior_dev":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not junior developer")

    if target_user.kpi_score < 100:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="KPI 100 is required")

    if not target_user.promotion_requested:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending promotion request")

    target_user.role = "senior_dev"
    target_user.promotion_requested = False
    target_user.promotion_requested_at = None
    db.add(target_user)
    db.commit()
    db.refresh(target_user)
    return target_user


@admin_promotions_router.get("/settings/auto-approve", response_model=AutoApproveSettingsOut)
def get_auto_approve_settings(_admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> AutoApproveSettingsOut:
    settings = _get_or_create_settings(db)
    return AutoApproveSettingsOut(auto_approve_promotions=settings.auto_approve_promotions)


@admin_promotions_router.patch("/settings/auto-approve", response_model=AutoApproveSettingsOut)
def update_auto_approve_settings(
    payload: AutoApproveSettingsUpdate,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AutoApproveSettingsOut:
    settings = _get_or_create_settings(db)
    settings.auto_approve_promotions = payload.auto_approve_promotions
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return AutoApproveSettingsOut(auto_approve_promotions=settings.auto_approve_promotions)


@admin_promotions_router.patch("/users/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdateRequest,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserOut:
    target_user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin role cannot be changed")

    previous_role = target_user.role
    target_user.role = payload.role
    if payload.role != "junior_dev":
        target_user.promotion_requested = False
        target_user.promotion_requested_at = None

    db.add(target_user)
    db.commit()
    db.refresh(target_user)
    logger.info(
        "admin_role_change user_id=%s from_role=%s to_role=%s",
        target_user.id,
        previous_role,
        target_user.role,
    )
    return target_user
