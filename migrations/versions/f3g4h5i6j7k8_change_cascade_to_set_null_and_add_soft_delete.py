"""change_cascade_to_set_null_and_add_soft_delete

Revision ID: f3g4h5i6j7k8
Revises: e1f2g3h4i5j6
Create Date: 2025-12-17 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3g4h5i6j7k8'
down_revision = 'e1f2g3h4i5j6'
branch_labels = None
depends_on = None


def upgrade():
    # Change User → Batch from CASCADE to SET NULL
    op.drop_constraint('debtor_batches_user_id_fkey', 'debtor_batches', type_='foreignkey')
    op.create_foreign_key(
        'debtor_batches_user_id_fkey',
        'debtor_batches',
        'users',
        ['user_id'],
        ['user_id'],
        ondelete='SET NULL'
    )
    # Make user_id nullable
    op.alter_column('debtor_batches', 'user_id', nullable=True)
    
    # Change Batch → Case from CASCADE to SET NULL (already nullable)
    op.drop_constraint('cases_batch_id_fkey', 'cases', type_='foreignkey')
    op.create_foreign_key(
        'cases_batch_id_fkey',
        'cases',
        'debtor_batches',
        ['batch_id'],
        ['batch_id'],
        ondelete='SET NULL'
    )
    
    # Add deleted_at columns for soft delete
    op.add_column('companies', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('debtor_batches', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('cases', sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade():
    # Remove deleted_at columns
    op.drop_column('cases', 'deleted_at')
    op.drop_column('debtor_batches', 'deleted_at')
    op.drop_column('companies', 'deleted_at')
    
    # Revert Batch → Case to CASCADE
    op.drop_constraint('cases_batch_id_fkey', 'cases', type_='foreignkey')
    op.create_foreign_key(
        'cases_batch_id_fkey',
        'cases',
        'debtor_batches',
        ['batch_id'],
        ['batch_id'],
        ondelete='CASCADE'
    )
    
    # Revert User → Batch to CASCADE
    op.alter_column('debtor_batches', 'user_id', nullable=False)
    op.drop_constraint('debtor_batches_user_id_fkey', 'debtor_batches', type_='foreignkey')
    op.create_foreign_key(
        'debtor_batches_user_id_fkey',
        'debtor_batches',
        'users',
        ['user_id'],
        ['user_id'],
        ondelete='CASCADE'
    )
