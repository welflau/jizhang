"""create bills table

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create bills table
    op.create_table(
        'bills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),  # 'income' or 'expense'
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('receipt_url', sa.String(500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), default=False),
        sa.Column('recurring_frequency', sa.String(20), nullable=True),  # 'daily', 'weekly', 'monthly', 'yearly'
        sa.Column('parent_bill_id', sa.Integer(), nullable=True),  # For recurring bills
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for query optimization
    # Index on user_id for user-specific queries
    op.create_index('idx_bills_user_id', 'bills', ['user_id'])
    
    # Index on date for time range queries
    op.create_index('idx_bills_date', 'bills', ['date'])
    
    # Index on type for filtering by income/expense
    op.create_index('idx_bills_type', 'bills', ['type'])
    
    # Index on category_id for category filtering
    op.create_index('idx_bills_category_id', 'bills', ['category_id'])
    
    # Index on amount for amount range queries
    op.create_index('idx_bills_amount', 'bills', ['amount'])
    
    # Composite index for common query patterns (user + date)
    op.create_index('idx_bills_user_date', 'bills', ['user_id', 'date'])
    
    # Composite index for user + type queries
    op.create_index('idx_bills_user_type', 'bills', ['user_id', 'type'])
    
    # Composite index for user + category queries
    op.create_index('idx_bills_user_category', 'bills', ['user_id', 'category_id'])
    
    # Composite index for complex queries (user + date + type)
    op.create_index('idx_bills_user_date_type', 'bills', ['user_id', 'date', 'type'])
    
    # Index on deleted_at for soft delete queries
    op.create_index('idx_bills_deleted_at', 'bills', ['deleted_at'])
    
    # Index on created_at for sorting by creation time
    op.create_index('idx_bills_created_at', 'bills', ['created_at'])
    
    # Index on is_recurring for recurring bill queries
    op.create_index('idx_bills_is_recurring', 'bills', ['is_recurring'])
    
    # Index on parent_bill_id for finding child recurring bills
    op.create_index('idx_bills_parent_bill_id', 'bills', ['parent_bill_id'])
    
    # Full-text search index on description (PostgreSQL specific)
    op.execute("""
        CREATE INDEX idx_bills_description_fts ON bills 
        USING gin(to_tsvector('english', COALESCE(description, '')))
    """)
    
    # Full-text search index on notes (PostgreSQL specific)
    op.execute("""
        CREATE INDEX idx_bills_notes_fts ON bills 
        USING gin(to_tsvector('english', COALESCE(notes, '')))
    """)
    
    # GIN index for tags array queries (PostgreSQL specific)
    op.create_index('idx_bills_tags', 'bills', ['tags'], postgresql_using='gin')

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
    
    op.create_foreign_key(
        'fk_bills_parent_bill_id',
        'bills', 'bills',
        ['parent_bill_id'], ['id'],
        ondelete='SET NULL'
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
    
    # Add check constraint for recurring frequency
    op.create_check_constraint(
        'ck_bills_recurring_frequency',
        'bills',
        "recurring_frequency IS NULL OR recurring_frequency IN ('daily', 'weekly', 'monthly', 'yearly')"
    )


def downgrade() -> None:
    # Drop check constraints
    op.drop_constraint('ck_bills_recurring_frequency', 'bills', type_='check')
    op.drop_constraint('ck_bills_amount_positive', 'bills', type_='check')
    op.drop_constraint('ck_bills_type', 'bills', type_='check')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_bills_parent_bill_id', 'bills', type_='foreignkey')
    op.drop_constraint('fk_bills_category_id', 'bills', type_='foreignkey')
    op.drop_constraint('fk_bills_user_id', 'bills', type_='foreignkey')
    
    # Drop indexes
    op.drop_index('idx_bills_tags', table_name='bills')
    op.execute('DROP INDEX IF EXISTS idx_bills_notes_fts')
    op.execute('DROP INDEX IF EXISTS idx_bills_description_fts')
    op.drop_index('idx_bills_parent_bill_id', table_name='bills')
    op.drop_index('idx_bills_is_recurring', table_name='bills')
    op.drop_index('idx_bills_created_at', table_name='bills')
    op.drop_index('idx_bills_deleted_at', table_name='bills')
    op.drop_index('idx_bills_user_date_type', table_name='bills')
    op.drop_index('idx_bills_user_category', table_name='bills')
    op.drop_index('idx_bills_user_type', table_name='bills')
    op.drop_index('idx_bills_user_date', table_name='bills')
    op.drop_index('idx_bills_amount', table_name='bills')
    op.drop_index('idx_bills_category_id', table_name='bills')
    op.drop_index('idx_bills_type', table_name='bills')
    op.drop_index('idx_bills_date', table_name='bills')
    op.drop_index('idx_bills_user_id', table_name='bills')
    
    # Drop table
    op.drop_table('bills')