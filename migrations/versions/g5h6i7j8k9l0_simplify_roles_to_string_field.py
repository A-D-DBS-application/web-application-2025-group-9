"""simplify_roles_to_string_field

Revision ID: g5h6i7j8k9l0
Revises: f3g4h5i6j7k8
Create Date: 2025-12-18 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'g5h6i7j8k9l0'
down_revision = 'f3g4h5i6j7k8'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Drop the role_id column from users (will cascade drop any constraints)
    op.drop_column('users', 'role_id')
    
    # Step 2: Add new role column as nullable string
    op.add_column('users', sa.Column('role', sa.String(50), nullable=True))
    
    # Step 3: Drop the roles table entirely
    op.drop_table('roles')


def downgrade():
    # Recreate roles table
    op.create_table(
        'roles',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('role_name', sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint('role_id'),
        sa.UniqueConstraint('role_name')
    )
    
    # Remove role column from users
    op.drop_column('users', 'role')
    
    # Re-add role_id column
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    
    # Recreate foreign key
    op.create_foreign_key('users_role_id_fkey', 'users', 'roles', ['role_id'], ['role_id'])
