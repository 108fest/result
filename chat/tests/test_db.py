from db import functions
from sqlalchemy import create_engine

from db.models import Base


def test_create_user_creates_valid_session_token(monkeypatch, tmp_path) -> None:
	db_path = tmp_path / "test.db"
	database_url = f"sqlite+pysqlite:///{db_path}"
	monkeypatch.setenv("DATABASE_URL", database_url)
	functions._get_session_factory.cache_clear()

	engine = create_engine(database_url, future=True)
	Base.metadata.create_all(engine)

	new_user, new_session = functions.create_new_user()

	assert new_user.id == new_session.user_id
	assert isinstance(new_session.token, str)
	assert new_session.token != ""
	assert functions.is_session_token_valid(new_session.token) is True
	assert functions.is_session_token_valid("definitely-not-a-real-token") is False
