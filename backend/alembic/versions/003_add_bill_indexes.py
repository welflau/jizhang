"""add bill indexes

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # 为账单表添加索引以优化查询性能
    
    # 1. 时间字段索引 - 用于时间范围查询
    op.create_index(
        'ix_bills_bill_date',
        'bills',
        ['bill_date'],
        unique=False
    )
    
    # 2. 分类字段索引 - 用于按分类筛选
    op.create_index(
        'ix_bills_category_id',
        'bills',
        ['category_id'],
        unique=False
    )
    
    # 3. 类型字段索引 - 用于按收入/支出类型筛选
    op.create_index(
        'ix_bills_bill_type',
        'bills',
        ['bill_type'],
        unique=False
    )
    
    # 4. 金额字段索引 - 用于金额范围查询
    op.create_index(
        'ix_bills_amount',
        'bills',
        ['amount'],
        unique=False
    )
    
    # 5. 用户ID索引 - 用于按用户查询（如果还没有的话）
    op.create_index(
        'ix_bills_user_id',
        'bills',
        ['user_id'],
        unique=False
    )
    
    # 6. 组合索引 - 用户ID + 时间（最常用的查询组合）
    op.create_index(
        'ix_bills_user_id_bill_date',
        'bills',
        ['user_id', 'bill_date'],
        unique=False
    )
    
    # 7. 组合索引 - 用户ID + 类型 + 时间
    op.create_index(
        'ix_bills_user_id_type_date',
        'bills',
        ['user_id', 'bill_type', 'bill_date'],
        unique=False
    )
    
    # 8. 组合索引 - 用户ID + 分类 + 时间
    op.create_index(
        'ix_bills_user_id_category_date',
        'bills',
        ['user_id', 'category_id', 'bill_date'],
        unique=False
    )
    
    # 9. 描述字段全文索引（用于关键词搜索）- MySQL
    # 注意：如果使用 PostgreSQL，需要使用不同的全文搜索方式
    # op.create_index(
    #     'ix_bills_description_fulltext',
    #     'bills',
    #     ['description'],
    #     unique=False,
    #     mysql_prefix='FULLTEXT'
    # )


def downgrade():
    # 删除所有创建的索引
    op.drop_index('ix_bills_user_id_category_date', table_name='bills')
    op.drop_index('ix_bills_user_id_type_date', table_name='bills')
    op.drop_index('ix_bills_user_id_bill_date', table_name='bills')
    op.drop_index('ix_bills_user_id', table_name='bills')
    op.drop_index('ix_bills_amount', table_name='bills')
    op.drop_index('ix_bills_bill_type', table_name='bills')
    op.drop_index('ix_bills_category_id', table_name='bills')
    op.drop_index('ix_bills_bill_date', table_name='bills')
    # op.drop_index('ix_bills_description_fulltext', table_name='bills')