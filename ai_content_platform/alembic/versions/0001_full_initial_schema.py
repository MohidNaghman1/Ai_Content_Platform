"""full initial schema for all models

Revision ID: 0001_full_initial_schema
Revises:
Create Date: 2026-02-02 00:00:00

"""

from alembic import op
import sqlalchemy as sa

revision = "0001_full_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("username", sa.String, unique=True, index=True, nullable=False),
        sa.Column("email", sa.String, unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("role", sa.String, default="viewer", nullable=False),
        sa.Column("avatar", sa.String, nullable=True),
        sa.Column("email_notifications", sa.Boolean, default=True),
        sa.Column("in_app_notifications", sa.Boolean, default=True),
    )

    # Roles table
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, unique=True, nullable=False, index=True),
    )

    # Permissions table
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, unique=True, nullable=False, index=True),
        sa.Column("description", sa.String, nullable=True),
    )

    # user_roles association table
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), primary_key=True),
    )

    # role_permissions association table
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), primary_key=True),
        sa.Column(
            "permission_id",
            sa.Integer,
            sa.ForeignKey("permissions.id"),
            primary_key=True,
        ),
    )

    # Refresh tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("token_hash", sa.String, nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("revoked", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime),
    )

    # Notifications
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("message", sa.String, nullable=False),
        sa.Column("notif_type", sa.String, nullable=False),
        sa.Column("read", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime),
    )

    # Articles
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer, primary_key=True, index=True, autoincrement=True),
        sa.Column("title", sa.String, nullable=False, index=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("flagged", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )

    # Tags
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True, index=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False, index=True),
    )

    # article_tags association table
    op.create_table(
        "article_tags",
        sa.Column(
            "article_id", sa.Integer, sa.ForeignKey("articles.id"), primary_key=True
        ),
        sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
    )

    # Conversations
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("summary_msg_count", sa.Integer, default=0),
    )

    # Messages
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "conversation_id",
            sa.Integer,
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("sender", sa.String, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime),
    )

    # Token usage
    op.create_table(
        "token_usage",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "conversation_id",
            sa.Integer,
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tokens_used", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime),
    )


def downgrade():
    op.drop_table("token_usage")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("article_tags")
    op.drop_table("tags")
    op.drop_table("articles")
    op.drop_table("notifications")
    op.drop_table("refresh_tokens")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
