from datetime import datetime

from pydantic import BaseModel


class NewsOut(BaseModel):
    id: int
    title: str
    summary: str
    created_at: datetime

    model_config = {"from_attributes": True}
