"""create transactions table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for query optimization
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'])
    op.create_index('ix_transactions_type', 'transactions', ['type'])
    op.create_index('ix_transactions_category_id', 'transactions', ['category_id'])
    op.create_index('ix_transactions_date', 'transactions', ['date'])
    op.create_index('ix_transactions_created_at', 'transactions', ['created_at'])
    
    # Create composite indexes for common query patterns
    op.create_index('ix_transactions_user_date', 'transactions', ['user_id', 'date'])
    op.create_index('ix_transactions_user_type', 'transactions', ['user_id', 'type'])
    op.create_index('ix_transactions_user_category', 'transactions', ['user_id', 'category_id'])
    
    # Add check constraint for transaction type
    op.create_check_constraint(
        'check_transaction_type',
        'transactions',
        "type IN ('income', 'expense')"
    )
    
    # Add check constraint for amount (must be positive)
    op.create_check_constraint(
        'check_amount_positive',
        'transactions',
        'amount > 0'
    )


def downgrade() -> None:
    # Drop check constraints
    op.drop_constraint('check_amount_positive', 'transactions', type_='check')
    op.drop_constraint('check_transaction_type', 'transactions', type_='check')
    
    # Drop composite indexes
    op.drop_index('ix_transactions_user_category', table_name='transactions')
    op.drop_index('ix_transactions_user_type', table_name='transactions')
    op.drop_index('ix_transactions_user_date', table_name='transactions')
    
    # Drop single column indexes
    op.drop_index('ix_transactions_created_at', table_name='transactions')
    op.drop_index('ix_transactions_date', table_name='transactions')
    op.drop_index('ix_transactions_category_id', table_name='transactions')
    op.drop_index('ix_transactions_type', table_name='transactions')
    op.drop_index('ix_transactions_user_id', table_name='transactions')
    
    # Drop table
    op.drop_table('transactions')