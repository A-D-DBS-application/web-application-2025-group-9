"""add_cash_column_only

Revision ID: e1f2a3b4c5d6
Revises: d5e7f8a9b2c1
Create Date: 2025-12-15 23:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1f2a3b4c5d6'
down_revision = 'd5e7f8a9b2c1'
branch_labels = None
depends_on = None


def upgrade():
    # Add cash column to companies table
    op.add_column('companies', sa.Column('cash', sa.Numeric(precision=15, scale=2), nullable=True))


def downgrade():
    # Remove cash column from companies table
    op.drop_column('companies', 'cash')
