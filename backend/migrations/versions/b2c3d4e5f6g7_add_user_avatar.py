"""Add user avatar field

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-25 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add avatar_url column to users table
    op.add_column('users', sa.Column('avatar_url', sa.String(length=255), nullable=True))


def downgrade():
    # Remove avatar_url column from users table
    op.drop_column('users', 'avatar_url')
