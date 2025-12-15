"""add_debtor_batches

Revision ID: d5e7f8a9b2c1
Revises: c4d8e2b9f1a3
Create Date: 2025-12-15 14:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd5e7f8a9b2c1'
down_revision = 'c4d8e2b9f1a3'
branch_labels = None
depends_on = None


def upgrade():
    # Drop table if it exists (from failed attempts)
    op.execute("DROP TABLE IF EXISTS debtor_batches CASCADE")
    
    # Create debtor_batches table
    op.create_table('debtor_batches',
        sa.Column('batch_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('batch_name', sa.String(length=255), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('batch_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], )
    )
    
    # Add batch_id column to cases table (drop if exists first)
    op.execute("ALTER TABLE cases DROP COLUMN IF EXISTS batch_id CASCADE")
    op.add_column('cases', sa.Column('batch_id', sa.Integer(), nullable=True))
    op.create_foreign_key('cases_batch_id_fkey', 'cases', 'debtor_batches', ['batch_id'], ['batch_id'])


def downgrade():
    # Remove batch_id from cases
    op.drop_constraint('cases_batch_id_fkey', 'cases', type_='foreignkey')
    op.drop_column('cases', 'batch_id')
    
    # Drop debtor_batches table
    op.drop_table('debtor_batches')
