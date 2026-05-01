"""create bills table and indexes

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
    # Create bills table
    op.create_table(
        'bills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),  # income or expense
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('bill_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for optimizing query performance
    
    # Index on user_id - most queries will filter by user
    op.create_index('idx_bills_user_id', 'bills', ['user_id'])
    
    # Index on bill_date - for time range queries
    op.create_index('idx_bills_bill_date', 'bills', ['bill_date'])
    
    # Index on type - for filtering income/expense
    op.create_index('idx_bills_type', 'bills', ['type'])
    
    # Index on category_id - for category filtering
    op.create_index('idx_bills_category_id', 'bills', ['category_id'])
    
    # Index on amount - for amount range queries
    op.create_index('idx_bills_amount', 'bills', ['amount'])
    
    # Composite index for common query patterns
    # user_id + bill_date (most common: user's bills in time range)
    op.create_index('idx_bills_user_date', 'bills', ['user_id', 'bill_date'])
    
    # user_id + type + bill_date (user's income/expense in time range)
    op.create_index('idx_bills_user_type_date', 'bills', ['user_id', 'type', 'bill_date'])
    
    # user_id + category_id + bill_date (user's bills by category in time range)
    op.create_index('idx_bills_user_category_date', 'bills', ['user_id', 'category_id', 'bill_date'])
    
    # user_id + type + category_id (user's income/expense by category)
    op.create_index('idx_bills_user_type_category', 'bills', ['user_id', 'type', 'category_id'])
    
    # GIN index for tags array - for keyword search in tags
    op.create_index('idx_bills_tags', 'bills', ['tags'], postgresql_using='gin')
    
    # Full text search index on description - for keyword search
    op.execute("""
        CREATE INDEX idx_bills_description_fts ON bills 
        USING gin(to_tsvector('english', COALESCE(description, '')))
    """)

    # Add foreign key constraints
    op.create_foreign_key(
        'fk_bills_user_id',
        'bills', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    op.create_foreign_key(
        'fk_bills_category_id',
        'bills', 'categories',
        ['category_id'], ['id'],
        ondelete='RESTRICT'
    )

    # Add check constraint for bill type
    op.create_check_constraint(
        'ck_bills_type',
        'bills',
        "type IN ('income', 'expense')"
    )
    
    # Add check constraint for amount (must be positive)
    op.create_check_constraint(
        'ck_bills_amount_positive',
        'bills',
        'amount > 0'
    )


def downgrade() -> None:
    # Drop check constraints
    op.drop_constraint('ck_bills_amount_positive', 'bills', type_='check')
    op.drop_constraint('ck_bills_type', 'bills', type_='check')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_bills_category_id', 'bills', type_='foreignkey')
    op.drop_constraint('fk_bills_user_id', 'bills', type_='foreignkey')
    
    # Drop indexes
    op.execute('DROP INDEX IF EXISTS idx_bills_description_fts')
    op.drop_index('idx_bills_tags', table_name='bills')
    op.drop_index('idx_bills_user_type_category', table_name='bills')
    op.drop_index('idx_bills_user_category_date', table_name='bills')
    op.drop_index('idx_bills_user_type_date', table_name='bills')
    op.drop_index('idx_bills_user_date', table_name='bills')
    op.drop_index('idx_bills_amount', table_name='bills')
    op.drop_index('idx_bills_category_id', table_name='bills')
    op.drop_index('idx_bills_type', table_name='bills')
    op.drop_index('idx_bills_bill_date', table_name='bills')
    op.drop_index('idx_bills_user_id', table_name='bills')
    
    # Drop table
    op.drop_table('bills')