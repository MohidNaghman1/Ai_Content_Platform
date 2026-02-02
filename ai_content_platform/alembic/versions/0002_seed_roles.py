"""seed initial roles

Revision ID: 0002_seed_roles
Revises: 0001_full_initial_schema
Create Date: 2026-02-02 00:10:00
"""

from alembic import op

revision = '0002_seed_roles'
down_revision = '0001_full_initial_schema'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("INSERT INTO roles (name) VALUES ('admin'), ('creator'), ('viewer');")

def downgrade():
    op.execute("DELETE FROM roles WHERE name IN ('admin', 'creator', 'viewer');")