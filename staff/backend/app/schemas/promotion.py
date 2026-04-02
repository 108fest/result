from datetime import datetime

from pydantic import BaseModel


class PromotionRequestOut(BaseModel):
    status: str
    requested_at: datetime | None = None


class AutoApproveSettingsOut(BaseModel):
    auto_approve_promotions: bool


class AutoApproveSettingsUpdate(BaseModel):
    auto_approve_promotions: bool
