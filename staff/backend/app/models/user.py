from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("kpi >= 0", name="ck_users_kpi_nonnegative"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, default="Unknown")
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_plain: Mapped[str | None] = mapped_column("password", String(255), nullable=True)
    kpi_score: Mapped[float] = mapped_column("kpi", Float, default=0, nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="junior_dev", index=True)
    auth_source: Mapped[str] = mapped_column(String(32), nullable=False, default="portal")
    promotion_requested: Mapped[bool] = mapped_column(nullable=False, default=False)
    promotion_requested_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    break_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    sessions: Mapped[list["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
