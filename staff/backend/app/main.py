from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.api.auth import router as auth_router
from app.api.home import router as home_router
from app.api.leaderboard import router as leaderboard_router
from app.api.promotions import admin_promotions_router, router as promotions_router
from app.api.tasks import router as tasks_router
from app.api.users import admin_router, router as users_router
from app.api.email_templates import router as email_templates_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.admin_settings import AdminSettings
from app.models.news import News
from app.models.session import UserSession
from app.models.task import Task
from app.models.user import User
from app.services.security import hash_password
import os

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(home_router, prefix=settings.api_prefix)
app.include_router(leaderboard_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(tasks_router, prefix=settings.api_prefix)
app.include_router(promotions_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)

app.include_router(admin_promotions_router, prefix=settings.api_prefix)
app.include_router(email_templates_router, prefix=settings.api_prefix)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def apply_bootstrap_migrations() -> None:
    # Keep existing local volumes working without dropping data.
    statements = [
        # Существующие миграции
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS promotion_requested BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS promotion_requested_at TIMESTAMP NULL",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS break_until TIMESTAMP NULL",
        "ALTER TABLE admin_settings ADD COLUMN IF NOT EXISTS auto_approve_promotions BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE admin_settings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT NOW()",
        # Миграции для db-auth интеграции
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255) NOT NULL DEFAULT 'Unknown'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255) NULL",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500) NULL",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(32) NOT NULL DEFAULT 'junior_dev'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_source VARCHAR(32) NOT NULL DEFAULT 'portal'",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT NOW()",
        "ALTER TABLE sessions ADD COLUMN IF NOT EXISTS session_token VARCHAR(128) NULL",
        "ALTER TABLE sessions ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP NULL",
        "ALTER TABLE sessions ALTER COLUMN token DROP NOT NULL",
    ]
    for sql in statements:
        try:
            # Run each statement in its own transaction.
            # This avoids PostgreSQL's "transaction is aborted" cascade when one step fails.
            with engine.begin() as conn:
                conn.execute(text(sql))
        except Exception:
            # Игнорируем ошибки если constraint/index уже существует
            pass


def seed_initial_data(db: Session) -> None:
    if not db.execute(select(AdminSettings).where(AdminSettings.id == 1)).scalar_one_or_none():
        db.add(AdminSettings(id=1, auto_approve_promotions=False))

    news_count = db.scalar(select(func.count()).select_from(News))
    if not news_count:
        db.add_all(
            [
                News(title="Quarter Results", summary="Q1 closed with stable KPI growth across teams."),
                News(title="Townhall", summary="General townhall scheduled for next Friday at 11:00."),
                News(title="Hiring", summary="Engineering team opened 3 new positions for backend and QA."),
            ]
        )

    db.commit()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    apply_bootstrap_migrations()
    with SessionLocal() as db:
        seed_initial_data(db)
        

from fastapi.responses import FileResponse
import os

@app.get("/{catchall:path}")
def serve_frontend(catchall: str):
    dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    file_path = os.path.join(dist_path, catchall)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(dist_path, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not built yet."}
