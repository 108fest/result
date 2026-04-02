from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr | None = None
    username: str | None = None
    kpi_score: float
    photo_url: str | None = None
    role: str
    level: int | None = 0
    promotion_requested: bool | None = False
    promotion_requested_at: datetime | None = None
    break_until: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KPIUpdateRequest(BaseModel):
    kpi_score: float


class UserRoleUpdateRequest(BaseModel):
    role: Literal["junior_dev", "senior_dev"]
