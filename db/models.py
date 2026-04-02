from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
	pass


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	username: Mapped[str] = mapped_column(String(255), nullable=False)
	full_name: Mapped[str] = mapped_column(String(255), nullable=False, default="Unknown")
	password: Mapped[str] = mapped_column(Text, nullable=False)
	level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	kpi: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

	sessions: Mapped[list["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
	
	chat_messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="sender")


class UserSession(Base):
	__tablename__ = "sessions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
	token: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

	user: Mapped["User"] = relationship("User", back_populates="sessions")


class Chat(Base):
	__tablename__ = "chats"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	title: Mapped[str] = mapped_column(String(255), nullable=True)
	user1_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
	user2_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

	user1: Mapped["User"] = relationship("User", foreign_keys=[user1_id])
	user2: Mapped["User"] = relationship("User", foreign_keys=[user2_id])
	messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")


class ChatMessage(Base):
	__tablename__ = "chat_messages"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("chats.id"), nullable=False)
	sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
	message_text: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

	chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
	sender: Mapped["User"] = relationship("User", back_populates="chat_messages")





