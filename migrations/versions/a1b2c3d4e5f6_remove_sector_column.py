"""remove_sector_column

Revision ID: a1b2c3d4e5f6
Revises: f3a4b5c6d7e8
Create Date: 2025-12-16 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f3a4b5c6d7e8'
branch_labels = None
depends_on = None


def upgrade():
    # Drop sector column from companies table
    op.drop_column('companies', 'sector')


def downgrade():
    # Recreate sector column if needed to rollback
    op.add_column('companies', sa.Column('sector', sa.String(length=255), nullable=True))
