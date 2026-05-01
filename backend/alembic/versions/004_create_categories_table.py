"""create categories table

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance optimization
    op.create_index('ix_categories_user_id', 'categories', ['user_id'])
    op.create_index('ix_categories_type', 'categories', ['type'])
    op.create_index('ix_categories_user_id_type', 'categories', ['user_id', 'type'])
    op.create_index('ix_categories_is_default', 'categories', ['is_default'])

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_categories_user_id',
        'categories',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Add check constraint for type field
    op.create_check_constraint(
        'ck_categories_type',
        'categories',
        "type IN ('income', 'expense')"
    )

    # Create unique constraint for user_id and name combination
    op.create_unique_constraint(
        'uq_categories_user_id_name',
        'categories',
        ['user_id', 'name']
    )


def downgrade():
    # Drop constraints
    op.drop_constraint('uq_categories_user_id_name', 'categories', type_='unique')
    op.drop_constraint('ck_categories_type', 'categories', type_='check')
    op.drop_constraint('fk_categories_user_id', 'categories', type_='foreignkey')

    # Drop indexes
    op.drop_index('ix_categories_is_default', table_name='categories')
    op.drop_index('ix_categories_user_id_type', table_name='categories')
    op.drop_index('ix_categories_type', table_name='categories')
    op.drop_index('ix_categories_user_id', table_name='categories')

    # Drop table
    op.drop_table('categories')