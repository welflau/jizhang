"""Create categories table

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance optimization
    op.create_index(
        'ix_categories_user_id',
        'categories',
        ['user_id']
    )
    
    op.create_index(
        'ix_categories_type',
        'categories',
        ['type']
    )
    
    op.create_index(
        'ix_categories_user_id_type',
        'categories',
        ['user_id', 'type']
    )
    
    op.create_index(
        'ix_categories_is_default',
        'categories',
        ['is_default']
    )
    
    # Add foreign key constraint to users table
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
    
    # Insert default categories for income
    op.execute("""
        INSERT INTO categories (user_id, name, type, icon, color, is_default)
        SELECT id, '工资', 'income', '💰', '#4CAF50', true FROM users
        UNION ALL
        SELECT id, '奖金', 'income', '🎁', '#8BC34A', true FROM users
        UNION ALL
        SELECT id, '投资收益', 'income', '📈', '#009688', true FROM users
        UNION ALL
        SELECT id, '其他收入', 'income', '💵', '#00BCD4', true FROM users
    """)
    
    # Insert default categories for expense
    op.execute("""
        INSERT INTO categories (user_id, name, type, icon, color, is_default)
        SELECT id, '餐饮', 'expense', '🍔', '#FF5722', true FROM users
        UNION ALL
        SELECT id, '交通', 'expense', '🚗', '#FF9800', true FROM users
        UNION ALL
        SELECT id, '购物', 'expense', '🛍️', '#E91E63', true FROM users
        UNION ALL
        SELECT id, '娱乐', 'expense', '🎮', '#9C27B0', true FROM users
        UNION ALL
        SELECT id, '医疗', 'expense', '🏥', '#F44336', true FROM users
        UNION ALL
        SELECT id, '教育', 'expense', '📚', '#3F51B5', true FROM users
        UNION ALL
        SELECT id, '住房', 'expense', '🏠', '#795548', true FROM users
        UNION ALL
        SELECT id, '通讯', 'expense', '📱', '#607D8B', true FROM users
        UNION ALL
        SELECT id, '其他支出', 'expense', '💸', '#9E9E9E', true FROM users
    """)


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_categories_user_id', 'categories', type_='foreignkey')
    
    # Drop check constraint
    op.drop_constraint('ck_categories_type', 'categories', type_='check')
    
    # Drop indexes
    op.drop_index('ix_categories_is_default', table_name='categories')
    op.drop_index('ix_categories_user_id_type', table_name='categories')
    op.drop_index('ix_categories_type', table_name='categories')
    op.drop_index('ix_categories_user_id', table_name='categories')
    
    # Drop table
    op.drop_table('categories')