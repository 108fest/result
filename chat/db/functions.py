import base64
import os
import random
import string
from datetime import UTC, datetime, timedelta
from functools import lru_cache

from db.models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

_DEFAULT_DATABASE_URL = "sqlite:///chat.db"


@lru_cache(maxsize=1)
def _get_session_factory() -> sessionmaker[Session]:
	"""Create (once) and return a SQLAlchemy session factory."""
	database_url = os.getenv("DATABASE_URL", _DEFAULT_DATABASE_URL)
	engine = create_engine(database_url, future=True)
	return sessionmaker(bind=engine, expire_on_commit=False)


def generate_random_id() -> int:
	"""Generate a random user ID between 1000 and 999999."""
	return random.randint(1000, 999999)


def generate_random_username() -> str:
	"""Generate a random username with gloomy/depressive vibes."""
	adjectives = ["hollow", "sorrowful", "grim", "bleak", "melancholic", "forsaken", "weary", "shadowed", "broken", "twisted"]
	nouns = ["raven", "phantom", "specter", "void", "abyss", "cemetery", "tomb", "wraith", "corpse", "skull"]
	number = random.randint(100, 9999)
	return f"{random.choice(adjectives)}_{random.choice(nouns)}{number}"


def generate_random_password() -> str:
	"""Generate a random password."""
	length = random.randint(12, 20)
	characters = string.ascii_letters + string.digits + "!@#$%^&*"
	return "".join(random.choice(characters) for _ in range(length))


def generate_random_token() -> str:
	"""Generate a random token."""
	random_bytes = bytes(random.randint(0, 255) for _ in range(32))
	return base64.b64encode(random_bytes).decode("utf-8")


def create_user(
		user_id: int,
		username: str,
		password: str,
		level: int = 0,
		kpi: int = 0,
):
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		# Generate random data

		# Create new user
		new_user = User(
			id=user_id,
			username=username,
			password=password,
			level=level,
			kpi=kpi,
			created_at=datetime.now(UTC),
		)

		db.add(new_user)
		db.flush()  # Ensure the user is inserted before creating the session

		# Create new session for the user
		new_session = UserSession(
			user_id=user_id,
			token=generate_random_token(),
			created_at=datetime.now(UTC),
		)
		db.add(new_session)
		db.commit()

		# Keep returned ORM objects usable after session closes.
		db.expunge(new_user)
		db.expunge(new_session)

		return new_user, new_session


def get_user_by_session(session: UserSession) -> User:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		user = db.query(User).filter(User.id == session.user_id).one()
		db.expunge(user)
		return user


def get_user_by_id(user_id: int) -> User:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		user = db.query(User).filter(User.id == user_id).one()
		db.expunge(user)
		return user
	

def get_chat_by_id(chat_id: int) -> Chat | None:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		chat = db.query(Chat).filter(Chat.id == chat_id).first()
		if chat:
			db.expunge(chat)
		return chat


def get_user_session_by_token(token: str) -> UserSession | None:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		session = db.query(UserSession).filter(UserSession.token == token).first()
		if session:
			db.expunge(session)
		return session



def promote_user(user_id: int) -> User:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		user = db.query(User).filter(User.id == user_id).one()
		if user.kpi >= 10 and user.level < 1:
			user.level = 1
			db.commit()
			db.expunge(user)
			return user
		else:
			raise ValueError("User does not meet promotion criteria")


def create_random_support_user() -> tuple[User, UserSession]:
	"""
	Create a new user with random data.
	
	The user will have:
	- Random ID (unique)
	- Random username
	- Random password (not hashed)
	- level = 0
	- kpi between 8 and 16
	- A new session created for the user
	
	Returns:
		User: The newly created user
	"""
	for _ in range(10):
		try:
			user_id = generate_random_id()
			username = generate_random_username()
			password = generate_random_password()
			kpi = random.randint(8, 16)
			return create_user(user_id, username, password, kpi)
		except IntegrityError:
			continue  # retry on collision
	else:
		raise RuntimeError("Could not create user, 10 collisions in a row :O ")



def find_chat(user1_id: int, user2_id: int) -> Chat | None:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		user1_id, user2_id = sorted((user1_id, user2_id))  # Ensure consistent ordering
		chat = db.query(Chat).filter(Chat.user1_id == user1_id, Chat.user2_id == user2_id).first()
		if chat:
			db.expunge(chat)
		return chat

def create_chat(user1_id: int, user2_id: int) -> Chat:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		user1_id, user2_id = sorted((user1_id, user2_id))  # Ensure consistent ordering
		new_chat = Chat(
			user1_id=user1_id,
			user2_id=user2_id,
		)
		db.add(new_chat)
		db.commit()
		db.expunge(new_chat)
		return new_chat


def create_message(chat_id: int, sender_id: int, content: str) -> ChatMessage:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		new_message = ChatMessage(
			chat_id=chat_id,
			sender_id=sender_id,
			message_text=content,
		)
		db.add(new_message)
		db.commit()
		db.expunge(new_message)
		return new_message


def cleanup_expired_users(hours: int = 24) -> int:
	"""
	Delete users and their sessions that were created more than 'hours' ago.
	
	This function deletes:
	- All users created more than 'hours' hours ago
	- Their associated sessions (cascade delete)
	- Their associated chat messages (cascade delete)
	- Their memberships in chats (cascade delete)
	
	Args:
		hours: Number of hours to wait before deletion (default: 24)
		
	Returns:
		int: Number of users deleted
	"""
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		cutoff_time = datetime.now(UTC) - timedelta(hours=hours)

		# Find users to delete
		users_to_delete = db.query(User).filter(User.created_at < cutoff_time).all()

		# Delete users (cascade will handle sessions and related data)
		deleted_count = len(users_to_delete)
		for user in users_to_delete:
			db.delete(user)

		db.commit()

		return deleted_count


def is_session_token_valid(token: str, ttl_hours: int = 24) -> bool:
	"""
	Check whether a session token exists and is still valid.

	A token is considered valid when:
	- It is not empty
	- A matching session exists in the database
	- The session was created within the last 'ttl_hours' hours

	Args:
		token: Session token to validate
		ttl_hours: Session time-to-live in hours (default: 24)

	Returns:
		bool: True if token is valid, False otherwise
	"""
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



def get_chats(user_id: int) -> list[Chat]:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		chats = db.query(Chat).filter((Chat.user1_id == user_id) | (Chat.user2_id == user_id)).all()
		for chat in chats:
			db.expunge(chat)
		return chats


def get_messages(chat_id: int) -> list[ChatMessage]:
	SessionLocal = _get_session_factory()
	with SessionLocal() as db:
		messages = db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).order_by(ChatMessage.created_at).all()
		for message in messages:
			db.expunge(message)
		return messages
