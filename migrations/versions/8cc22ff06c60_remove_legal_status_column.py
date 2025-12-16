"""remove_legal_status_column

Revision ID: 8cc22ff06c60
Revises: a1b2c3d4e5f6
Create Date: 2025-12-16 21:08:30.716319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cc22ff06c60'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Drop legal_status column from companies table
    op.drop_column('companies', 'legal_status')


def downgrade():
    # Re-add legal_status column if rolling back
    op.add_column('companies', sa.Column('legal_status', sa.String(length=100), nullable=True))
