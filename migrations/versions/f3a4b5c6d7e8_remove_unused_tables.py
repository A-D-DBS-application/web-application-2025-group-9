"""remove_unused_tables

Revision ID: f3a4b5c6d7e8
Revises: e1f2a3b4c5d6
Create Date: 2025-12-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3a4b5c6d7e8'
down_revision = 'e1f2a3b4c5d6'
branch_labels = None
depends_on = None


def upgrade():
    # Drop unused tables
    op.drop_table('statements')
    op.drop_table('tables')
    op.drop_table('companies1')


def downgrade():
    # Recreate tables if needed to rollback
    op.create_table('companies1',
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('company_id')
    )
    
    op.create_table('tables',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('statement_id', sa.String(length=100), nullable=True),
        sa.Column('table_name', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('statements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('activa', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('oprichtingskosten', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('vaste_activa', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('immateriële_activa', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('source_date', sa.Date(), nullable=True),
        sa.Column('file_name', sa.String(length=500), nullable=True),
        sa.Column('inserted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies1.company_id'], ),
        sa.ForeignKeyConstraint(['id'], ['tables.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
