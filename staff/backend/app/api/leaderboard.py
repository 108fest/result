from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[UserOut])
def leaderboard(
    limit: int = 20,
    offset: int = 0,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[UserOut]:
    stmt = select(User).order_by(desc(User.kpi_score), User.id).limit(limit).offset(offset)
    real_users = list(db.execute(stmt).scalars())
    
    from datetime import datetime
    placeholder = "https://placehold.co/256x256/png"
    
    fake_users = [
        UserOut(id=99991, full_name="Krutoy Rabotyaga", kpi_score=1337, role="senior_dev", photo_url=placeholder, level=0, promotion_requested=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        UserOut(id=99992, full_name="San Sanych", kpi_score=999, role="senior_dev", photo_url=placeholder, level=0, promotion_requested=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        UserOut(id=99993, full_name="Zavodchanin", kpi_score=666, role="junior_dev", photo_url=placeholder, level=0, promotion_requested=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        UserOut(id=99994, full_name="Oleg (Ne spit)", kpi_score=420, role="junior_dev", photo_url=placeholder, level=0, promotion_requested=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        UserOut(id=99995, full_name="Pasha Technik", kpi_score=300, role="junior_dev", photo_url=placeholder, level=0, promotion_requested=False, created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
    ]
    
    real_users_out = [UserOut.model_validate(u) for u in real_users]
    all_users = fake_users + real_users_out
    all_users.sort(key=lambda x: x.kpi_score, reverse=True)
    
    return all_users[:limit]
