"""create initial schema

Revision ID: 0001_create_initial_schema
Revises:
Create Date: 2026-04-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_create_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table(
		"users",
		sa.Column("id", sa.Integer(), nullable=False),
		sa.Column("username", sa.String(length=255), nullable=False),
		sa.Column("password", sa.Text(), nullable=False),
		sa.Column("level", sa.Integer(), nullable=False),
		sa.Column("kpi", sa.Integer(), nullable=False),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.PrimaryKeyConstraint("id"),
	)

	op.create_table(
		"chats",
		sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
		sa.Column("title", sa.String(length=255), nullable=True),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.PrimaryKeyConstraint("id"),
	)

	op.create_table(
		"sessions",
		sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
		sa.Column("user_id", sa.Integer(), nullable=False),
		sa.Column("token", sa.Text(), nullable=False),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
		sa.PrimaryKeyConstraint("id"),
	)

	op.create_table(
		"chat_members",
		sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
		sa.Column("chat_id", sa.Integer(), nullable=False),
		sa.Column("user_id", sa.Integer(), nullable=False),
		sa.Column("joined_at", sa.DateTime(), nullable=False),
		sa.ForeignKeyConstraint(["chat_id"], ["chats.id"]),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
		sa.PrimaryKeyConstraint("id"),
	)

	op.create_table(
		"chat_messages",
		sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
		sa.Column("chat_id", sa.Integer(), nullable=False),
		sa.Column("sender_id", sa.Integer(), nullable=False),
		sa.Column("message_text", sa.Text(), nullable=False),
		sa.Column("created_at", sa.DateTime(), nullable=False),
		sa.ForeignKeyConstraint(["chat_id"], ["chats.id"]),
		sa.ForeignKeyConstraint(["sender_id"], ["users.id"]),
		sa.PrimaryKeyConstraint("id"),
	)


def downgrade() -> None:
	op.drop_table("chat_messages")
	op.drop_table("chat_members")
	op.drop_table("sessions")
	op.drop_table("chats")
	op.drop_table("users")
