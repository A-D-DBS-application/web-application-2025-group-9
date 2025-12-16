"""merge_login_tables

Revision ID: b7c8d9e0f1a2
Revises: 8cc22ff06c60
Create Date: 2025-12-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7c8d9e0f1a2'
down_revision = '8cc22ff06c60'
branch_labels = None
depends_on = None


def upgrade():
    # Add username column to users table
    op.add_column('users', sa.Column('username', sa.String(length=255), nullable=True, unique=True))
    
    # Make username unique
    op.create_unique_constraint('uq_users_username', 'users', ['username'])
    
    # Drop the inlog_gegevens table (login credentials now in users)
    op.drop_table('inlog_gegevens')


def downgrade():
    # Recreate inlog_gegevens table
    op.create_table('inlog_gegevens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('naam', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('naam')
    )
    
    # Remove username from users
    op.drop_constraint('uq_users_username', 'users', type_='unique')
    op.drop_column('users', 'username')
