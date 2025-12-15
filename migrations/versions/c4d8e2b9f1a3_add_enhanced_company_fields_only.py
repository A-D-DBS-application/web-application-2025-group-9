"""add_enhanced_company_fields_only

Revision ID: c4d8e2b9f1a3
Revises: 9da48cfd6f7e
Create Date: 2025-12-15 13:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c4d8e2b9f1a3'
down_revision = '9da48cfd6f7e'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to companies table
    op.add_column('companies', sa.Column('legal_status', sa.String(length=100), nullable=True))
    op.add_column('companies', sa.Column('established_since', sa.Date(), nullable=True))
    op.add_column('companies', sa.Column('revenue_estimation', sa.String(length=50), nullable=True))
    op.add_column('companies', sa.Column('employee_estimation', sa.String(length=50), nullable=True))
    op.add_column('companies', sa.Column('common_score', sa.String(length=10), nullable=True))
    op.add_column('companies', sa.Column('credit_limit', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('companies', sa.Column('current_ratio', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('companies', sa.Column('quick_ratio', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('companies', sa.Column('ebitda', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('companies', sa.Column('net_profit', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('companies', sa.Column('total_assets', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('companies', sa.Column('equity', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('companies', sa.Column('total_debt', sa.Numeric(precision=15, scale=2), nullable=True))


def downgrade():
    # Remove new columns
    op.drop_column('companies', 'total_debt')
    op.drop_column('companies', 'equity')
    op.drop_column('companies', 'total_assets')
    op.drop_column('companies', 'net_profit')
    op.drop_column('companies', 'ebitda')
    op.drop_column('companies', 'quick_ratio')
    op.drop_column('companies', 'current_ratio')
    op.drop_column('companies', 'credit_limit')
    op.drop_column('companies', 'common_score')
    op.drop_column('companies', 'employee_estimation')
    op.drop_column('companies', 'revenue_estimation')
    op.drop_column('companies', 'established_since')
    op.drop_column('companies', 'legal_status')
