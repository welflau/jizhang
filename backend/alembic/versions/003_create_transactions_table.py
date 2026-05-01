"""create transactions table

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for transaction type
    transaction_type_enum = postgresql.ENUM('income', 'expense', name='transaction_type', create_type=True)
    transaction_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('income', 'expense', name='transaction_type'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT')
    )
    
    # Create indexes for optimized query performance
    op.create_index('ix_transactions_id', 'transactions', ['id'], unique=False)
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'], unique=False)
    op.create_index('ix_transactions_category_id', 'transactions', ['category_id'], unique=False)
    op.create_index('ix_transactions_date', 'transactions', ['date'], unique=False)
    op.create_index('ix_transactions_type', 'transactions', ['type'], unique=False)
    op.create_index('ix_transactions_created_at', 'transactions', ['created_at'], unique=False)
    
    # Create composite indexes for common query patterns
    op.create_index('ix_transactions_user_date', 'transactions', ['user_id', 'date'], unique=False)
    op.create_index('ix_transactions_user_type', 'transactions', ['user_id', 'type'], unique=False)
    op.create_index('ix_transactions_user_category', 'transactions', ['user_id', 'category_id'], unique=False)
    op.create_index('ix_transactions_user_type_date', 'transactions', ['user_id', 'type', 'date'], unique=False)
    
    # Add check constraint to ensure amount is positive
    op.create_check_constraint(
        'check_transactions_amount_positive',
        'transactions',
        'amount > 0'
    )


def downgrade() -> None:
    # Drop check constraint
    op.drop_constraint('check_transactions_amount_positive', 'transactions', type_='check')
    
    # Drop composite indexes
    op.drop_index('ix_transactions_user_type_date', table_name='transactions')
    op.drop_index('ix_transactions_user_category', table_name='transactions')
    op.drop_index('ix_transactions_user_type', table_name='transactions')
    op.drop_index('ix_transactions_user_date', table_name='transactions')
    
    # Drop single column indexes
    op.drop_index('ix_transactions_created_at', table_name='transactions')
    op.drop_index('ix_transactions_type', table_name='transactions')
    op.drop_index('ix_transactions_date', table_name='transactions')
    op.drop_index('ix_transactions_category_id', table_name='transactions')
    op.drop_index('ix_transactions_user_id', table_name='transactions')
    op.drop_index('ix_transactions_id', table_name='transactions')
    
    # Drop transactions table
    op.drop_table('transactions')
    
    # Drop enum type
    transaction_type_enum = postgresql.ENUM('income', 'expense', name='transaction_type')
    transaction_type_enum.drop(op.get_bind(), checkfirst=True)