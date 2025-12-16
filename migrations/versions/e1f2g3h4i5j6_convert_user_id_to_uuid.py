"""convert_user_id_to_uuid

Revision ID: e1f2g3h4i5j6
Revises: d6e7f8g9h0i1
Create Date: 2025-12-17 00:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e1f2g3h4i5j6'
down_revision = 'd6e7f8g9h0i1'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add SET NULL to Case.user_id for when users are deleted
    op.drop_constraint('cases_user_id_fkey', 'cases', type_='foreignkey')
    
    # Step 2: Convert User.user_id from Integer to UUID
    # Drop foreign key constraints first
    op.drop_constraint('debtor_batches_user_id_fkey', 'debtor_batches', type_='foreignkey')
    
    # Change users.user_id type to UUID
    op.execute("ALTER TABLE users ALTER COLUMN user_id TYPE UUID USING uuid_generate_v4()")
    
    # Recreate foreign keys with CASCADE/SET NULL
    op.create_foreign_key(
        'debtor_batches_user_id_fkey',
        'debtor_batches',
        'users',
        ['user_id'],
        ['user_id'],
        ondelete='CASCADE'
    )
    
    op.create_foreign_key(
        'cases_user_id_fkey',
        'cases',
        'users',
        ['user_id'],
        ['user_id'],
        ondelete='SET NULL'
    )


def downgrade():
    # Revert Case.user_id
    op.drop_constraint('cases_user_id_fkey', 'cases', type_='foreignkey')
    op.create_foreign_key(
        'cases_user_id_fkey',
        'cases',
        'users',
        ['user_id'],
        ['user_id']
    )
    
    # Revert User.user_id to Integer
    op.drop_constraint('debtor_batches_user_id_fkey', 'debtor_batches', type_='foreignkey')
    op.execute("ALTER TABLE users ALTER COLUMN user_id TYPE INTEGER USING user_id::text::integer")
    op.create_foreign_key(
        'debtor_batches_user_id_fkey',
        'debtor_batches',
        'users',
        ['user_id'],
        ['user_id'],
        ondelete='CASCADE'
    )
