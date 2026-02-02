"""add chat permissions and assign to roles

Revision ID: 20260201_chat_permissions
Revises: 20260201_roles_permissions
Create Date: 2026-02-01 09:00:00
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260201_chat_permissions"
down_revision: Union[str, Sequence[str], None] = "20260201_roles_permissions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert chat permissions (including view_message and view_usage)
    op.execute("""
        INSERT INTO permissions (name, description) VALUES
            ('start_chat', 'Start a new chat conversation'),
            ('view_chat', 'View chat conversations'),
            ('send_message', 'Send messages in chat'),
            ('view_message', 'View messages in a conversation'),
            ('view_usage', 'View token usage for a conversation');
        """)

    # Assign all chat permissions to admin
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r, permissions p
        WHERE r.name = 'admin' AND p.name IN ('start_chat', 'view_chat', 'send_message', 'view_message', 'view_usage');
        """)

    # Assign all chat permissions to creator
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r, permissions p
        WHERE r.name = 'creator' AND p.name IN ('start_chat', 'view_chat', 'send_message', 'view_message', 'view_usage');
        """)


def downgrade() -> None:
    # Remove chat permissions from role_permissions
    op.execute("""
    DELETE FROM role_permissions WHERE permission_id IN (
        SELECT id FROM permissions WHERE name IN ('start_chat', 'view_chat', 'send_message', 'view_message', 'view_usage')
    );
    """)
    # Remove chat permissions
    op.execute("""
    DELETE FROM permissions WHERE name IN ('start_chat', 'view_chat', 'send_message', 'view_message', 'view_usage');
    """)
