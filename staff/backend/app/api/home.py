from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.news import News
from app.schemas.news import NewsOut

router = APIRouter(prefix="/home", tags=["home"])


@router.get("/news", response_model=list[NewsOut])
def get_news(db: Session = Depends(get_db)) -> list[News]:
    return list(db.execute(select(News).order_by(desc(News.created_at)).limit(20)).scalars())
