"""add_cascade_delete_to_batches

Revision ID: c5d6e7f8g9h0
Revises: b7c8d9e0f1a2
Create Date: 2025-12-17 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5d6e7f8g9h0'
down_revision = 'b7c8d9e0f1a2'
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing foreign key constraint
    op.drop_constraint('debtor_batches_user_id_fkey', 'debtor_batches', type_='foreignkey')
    
    # Recreate with CASCADE delete
    op.create_foreign_key(
        'debtor_batches_user_id_fkey',
        'debtor_batches',
        'users',
        ['user_id'],
        ['user_id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Remove CASCADE on downgrade
    op.drop_constraint('debtor_batches_user_id_fkey', 'debtor_batches', type_='foreignkey')
    
    op.create_foreign_key(
        'debtor_batches_user_id_fkey',
        'debtor_batches',
        'users',
        ['user_id'],
        ['user_id']
    )
