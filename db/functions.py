import base64
import os
import random
import string
from datetime import UTC, datetime, timedelta
from functools import lru_cache

from db.models import User, UserSession
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_DEFAULT_DATABASE_URL = "sqlite:///chat.db"


@lru_cache(maxsize=1)
def _get_session_factory() -> sessionmaker[Session]:
	database_url = os.getenv("DATABASE_URL", _DEFAULT_DATABASE_URL)
	engine = create_engine(database_url, future=True, pool_pre_ping=True, pool_size=20, max_overflow=30)
	return sessionmaker(bind=engine, expire_on_commit=False)


def generate_random_id() -> int:
	return random.randint(1000, 999999)


def generate_random_username() -> str:
	adjectives = ["hollow", "sorrowful", "grim", "bleak", "melancholic", "forsaken", "weary", "shadowed", "broken", "twisted"]
	nouns = ["raven", "phantom", "specter", "void", "abyss", "cemetery", "tomb", "wraith", "corpse", "skull"]
	number = random.randint(100, 9999)
	return f"{random.choice(adjectives)}_{random.choice(nouns)}{number}"


def generate_random_password() -> str:
	length = random.randint(12, 20)
	characters = string.ascii_letters + string.digits + "!@#$%^&*"
	return "".join(random.choice(characters) for _ in range(length))


def generate_random_token() -> str:
	random_bytes = bytes(random.randint(0, 255) for _ in range(32))
	return base64.b64encode(random_bytes).decode("utf-8")


def generate_random_fullname() -> str:
	adjectives = ["Oiled", "Sweaty", "Depressed", "Crying", "Angry", "Tired", "Lost", "Doomed", "Cursed", "Based", "Sigma", "Gigachad"]
	nouns = ["Fox", "Raccoon", "Hamster", "Cat", "Dog", "Wolf", "Bear", "Rat", "Pigeon", "Sloth", "Capybara", "Hedgehog"]
	import random
	return f"{random.choice(adjectives)} {random.choice(nouns)}"

def create_new_user() -> tuple[User, UserSession]:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		user_id = generate_random_id()
		username = generate_random_username()
		password = generate_random_password()
		kpi = 0

		new_user = User(
			id=user_id,
			username=username,
			full_name=generate_random_fullname(),
			password=password,
			level=0,
			kpi=kpi,
			created_at=datetime.now(UTC),
		)

		db.add(new_user)
		db.flush()

		new_session = UserSession(
			user_id=user_id,
			token=generate_random_token(),
			created_at=datetime.now(UTC),
		)
		db.add(new_session)
		db.commit()

		db.expunge(new_user)
		db.expunge(new_session)

		return new_user, new_session


def cleanup_expired_users(hours: int = 24) -> int:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		cutoff_time = datetime.now(UTC) - timedelta(hours=hours)

		users_to_delete = db.query(User).filter(User.created_at < cutoff_time).all()

		deleted_count = len(users_to_delete)
		for user in users_to_delete:
			db.delete(user)

		db.commit()

		return deleted_count


def is_session_token_valid(token: str, ttl_hours: int = 24) -> bool:
	if not token:
		return False

	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		cutoff_time = datetime.now(UTC) - timedelta(hours=ttl_hours)

		session = (
			db.query(UserSession)
			.filter(UserSession.token == token, UserSession.created_at >= cutoff_time)
			.first()
		)

		return session is not None
