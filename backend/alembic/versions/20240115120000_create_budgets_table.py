"""create budgets table

Revision ID: 20240115120000
Revises: 
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240115120000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False, comment='Budget period in YYYY-MM format'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for optimized query performance
    op.create_index('ix_budgets_user_id', 'budgets', ['user_id'])
    op.create_index('ix_budgets_period', 'budgets', ['period'])
    op.create_index('ix_budgets_user_id_period', 'budgets', ['user_id', 'period'])
    op.create_index('ix_budgets_category_id', 'budgets', ['category_id'])
    
    # Create unique constraint to prevent duplicate budgets for same user, category, and period
    op.create_index(
        'ix_budgets_user_category_period_unique',
        'budgets',
        ['user_id', 'category_id', 'period'],
        unique=True
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_budgets_user_category_period_unique', table_name='budgets')
    op.drop_index('ix_budgets_category_id', table_name='budgets')
    op.drop_index('ix_budgets_user_id_period', table_name='budgets')
    op.drop_index('ix_budgets_period', table_name='budgets')
    op.drop_index('ix_budgets_user_id', table_name='budgets')
    
    # Drop table
    op.drop_table('budgets')