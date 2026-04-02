from datetime import datetime
from pydantic import BaseModel

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    started_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
