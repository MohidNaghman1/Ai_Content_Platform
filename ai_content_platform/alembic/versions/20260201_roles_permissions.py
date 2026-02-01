"""add initial roles and assign permissions

Revision ID: 20260201_roles_permissions
Revises: 91d572d3d9da
Create Date: 2026-02-01 08:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260201_roles_permissions'
down_revision: Union[str, Sequence[str], None] = '91d572d3d9da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Insert roles
    op.execute("""
    INSERT INTO roles (name)
    VALUES
      ('admin'),
      ('creator'),
      ('viewer');
    """)

    # Assign all permissions to admin
    op.execute("""
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id
    FROM roles r, permissions p
    WHERE r.name = 'admin';
    """)

    # Assign read-only permissions to viewer
    op.execute("""
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id
    FROM roles r
    JOIN permissions p ON p.name IN ('view_content', 'view_notifications')
    WHERE r.name = 'viewer';
    """)

    # Assign content creation permissions to creator
    op.execute("""
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id
    FROM roles r
    JOIN permissions p ON p.name IN ('view_content', 'edit_content', 'generate_content', 'summarize_content', 'view_notifications')
    WHERE r.name = 'creator';
    """)

def downgrade() -> None:
    # Remove role-permission assignments
    op.execute("DELETE FROM role_permissions WHERE role_id IN (SELECT id FROM roles WHERE name IN ('admin', 'creator', 'viewer'));")
    # Remove roles
    op.execute("DELETE FROM roles WHERE name IN ('admin', 'creator', 'viewer');")
