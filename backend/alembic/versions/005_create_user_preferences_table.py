"""create user preferences table

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
    # 创建用户偏好设置表
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.String(20), nullable=False, server_default='light'),
        sa.Column('language', sa.String(10), nullable=False, server_default='zh-CN'),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='Asia/Shanghai'),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('push_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notification_sound', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('show_online_status', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('auto_play_video', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('data_saver_mode', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('font_size', sa.String(10), nullable=False, server_default='medium'),
        sa.Column('page_size', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('preferences_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', name='uq_user_preferences_user_id')
    )
    
    # 创建索引
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])
    op.create_index('ix_user_preferences_theme', 'user_preferences', ['theme'])
    op.create_index('ix_user_preferences_language', 'user_preferences', ['language'])
    
    # 为现有用户创建默认偏好设置
    op.execute("""
        INSERT INTO user_preferences (user_id, theme, language, timezone)
        SELECT id, 'light', 'zh-CN', 'Asia/Shanghai'
        FROM users
        WHERE NOT EXISTS (
            SELECT 1 FROM user_preferences WHERE user_preferences.user_id = users.id
        )
    """)


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_user_preferences_language', table_name='user_preferences')
    op.drop_index('ix_user_preferences_theme', table_name='user_preferences')
    op.drop_index('ix_user_preferences_user_id', table_name='user_preferences')
    
    # 删除表
    op.drop_table('user_preferences')