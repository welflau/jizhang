"""create budgets table

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
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('period', sa.String(length=7), nullable=False),
        sa.Column('alert_threshold', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_budgets_user_id', 'budgets', ['user_id'])
    op.create_index('ix_budgets_period', 'budgets', ['period'])
    op.create_index('ix_budgets_user_period', 'budgets', ['user_id', 'period'])
    op.create_unique_constraint('uq_budgets_user_category_period', 'budgets', ['user_id', 'category_id', 'period'])


def downgrade():
    op.drop_constraint('uq_budgets_user_category_period', 'budgets', type_='unique')
    op.drop_index('ix_budgets_user_period', table_name='budgets')
    op.drop_index('ix_budgets_period', table_name='budgets')
    op.drop_index('ix_budgets_user_id', table_name='budgets')
    op.drop_table('budgets')