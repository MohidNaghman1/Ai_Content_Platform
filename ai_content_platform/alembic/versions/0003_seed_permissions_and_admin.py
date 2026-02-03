"""Seed permissions and assign to roles

Revision ID: 0003_seed_permissions_and_admin
Revises: 0002_seed_roles
Create Date: 2026-02-03
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_seed_permissions_and_admin"
down_revision = "0002_seed_roles"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Define permissions (richer set, with descriptions)
    permissions = [
        {"name": "view_users", "description": "View users"},
        {"name": "edit_users", "description": "Edit users"},
        {"name": "delete_users", "description": "Delete users"},
        {"name": "view_content", "description": "View content"},
        {"name": "edit_content", "description": "Edit content"},
        {"name": "delete_content", "description": "Delete content"},
        {"name": "generate_content", "description": "Generate AI content"},
        {"name": "summarize_content", "description": "Summarize content"},
        {"name": "view_notifications", "description": "View notifications"},
        {"name": "send_notifications", "description": "Send notifications"},
        {"name": "start_chat", "description": "Start chat"},
        {"name": "view_chat", "description": "View chat"},
        {"name": "send_message", "description": "Send chat message"},
        {"name": "view_usage", "description": "View token usage"},
    ]

    # Role to permissions mapping
    role_permissions = {
        "admin": [p["name"] for p in permissions],
        "creator": [
            "view_users",
            "view_content",
            "generate_content",
            "summarize_content",
            "view_notifications",
            "start_chat",
            "view_chat",
            "send_message",
        ],
        "viewer": ["view_users", "view_content", "view_notifications"],
    }

    # Create permissions if not exist
    for perm in permissions:
        conn.execute(
            sa.text("""
            INSERT INTO permissions (name, description)
            VALUES (:name, :description)
            ON CONFLICT (name) DO NOTHING
            """),
            perm,
        )

    # Assign permissions to each role
    for role, perms in role_permissions.items():
        role_id = conn.execute(
            sa.text("SELECT id FROM roles WHERE name=:role"), {"role": role}
        ).scalar()
        if role_id is not None:
            for perm_name in perms:
                perm_id = conn.execute(
                    sa.text("SELECT id FROM permissions WHERE name=:name"),
                    {"name": perm_name},
                ).scalar()
                if perm_id is not None:
                    conn.execute(
                        sa.text(
                            "INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id) ON CONFLICT DO NOTHING"
                        ),
                        {"role_id": role_id, "perm_id": perm_id},
                    )

    # Optionally, sync role_field for users with their relationship
    for role in role_permissions.keys():
        role_id = conn.execute(
            sa.text("SELECT id FROM roles WHERE name=:role"), {"role": role}
        ).scalar()
        if role_id is not None:
            conn.execute(
                sa.text("""UPDATE users
                    SET role=:role
                    WHERE id IN (
                        SELECT user_id FROM user_roles WHERE role_id=:role_id
                    )"""),
                {"role": role, "role_id": role_id},
            )


def downgrade():
    # Remove the permissions and role assignments
    conn = op.get_bind()
    perm_names = [
        "view_users",
        "edit_users",
        "delete_users",
        "view_content",
        "edit_content",
        "delete_content",
        "generate_content",
        "summarize_content",
        "view_notifications",
        "send_notifications",
        "start_chat",
        "view_chat",
        "send_message",
        "view_usage",
    ]
    for name in perm_names:
        perm_id = conn.execute(
            sa.text("SELECT id FROM permissions WHERE name=:name"), {"name": name}
        ).scalar()
        if perm_id:
            conn.execute(
                sa.text("DELETE FROM role_permissions WHERE permission_id=:perm_id"),
                {"perm_id": perm_id},
            )
            conn.execute(
                sa.text("DELETE FROM permissions WHERE id=:perm_id"),
                {"perm_id": perm_id},
            )
