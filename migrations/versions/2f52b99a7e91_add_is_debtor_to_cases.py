"""add is_debtor to cases

Revision ID: 2f52b99a7e91
Revises:
Create Date: 2025-12-11 22:20:19.542287

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2f52b99a7e91'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add is_debtor column to cases table
    op.add_column('cases', sa.Column('is_debtor', sa.Boolean(), nullable=True))


def downgrade():
    # Remove is_debtor column from cases table
    op.drop_column('cases', 'is_debtor')
