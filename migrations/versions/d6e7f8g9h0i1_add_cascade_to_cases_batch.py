"""add_cascade_to_cases_batch

Revision ID: d6e7f8g9h0i1
Revises: c5d6e7f8g9h0
Create Date: 2025-12-17 00:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6e7f8g9h0i1'
down_revision = 'c5d6e7f8g9h0'
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing foreign key constraint for batch_id
    op.drop_constraint('cases_batch_id_fkey', 'cases', type_='foreignkey')
    
    # Recreate with CASCADE delete
    op.create_foreign_key(
        'cases_batch_id_fkey',
        'cases',
        'debtor_batches',
        ['batch_id'],
        ['batch_id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Remove CASCADE on downgrade
    op.drop_constraint('cases_batch_id_fkey', 'cases', type_='foreignkey')
    
    op.create_foreign_key(
        'cases_batch_id_fkey',
        'cases',
        'debtor_batches',
        ['batch_id'],
        ['batch_id']
    )
