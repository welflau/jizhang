"""create users table

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


def upgrade() -> None:
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('company', sa.String(length=100), nullable=True),
        sa.Column('job_title', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_ip', sa.String(length=45), nullable=True),
        sa.Column('login_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    # 创建用户偏好设置表
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='zh-CN'),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='Asia/Shanghai'),
        sa.Column('theme', sa.String(length=20), nullable=False, server_default='light'),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('push_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sms_notifications', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('newsletter_subscription', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('privacy_profile_visible', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('privacy_email_visible', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('privacy_phone_visible', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('two_factor_method', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # 创建用户偏好设置索引
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'], unique=True)

    # 创建用户会话表
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('refresh_token', sa.String(length=500), nullable=True),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('device_name', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # 创建会话索引
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_token', 'user_sessions', ['token'], unique=True)
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'])

    # 创建密码重置表
    op.create_table(
        'password_resets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # 创建密码重置索引
    op.create_index('ix_password_resets_token', 'password_resets', ['token'], unique=True)
    op.create_index('ix_password_resets_user_id', 'password_resets', ['user_id'])
    op.create_index('ix_password_resets_expires_at', 'password_resets', ['expires_at'])

    # 创建用户活动日志表
    op.create_table(
        'user_activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # 创建活动日志索引
    op.create_index('ix_user_activity_logs_user_id', 'user_activity_logs', ['user_id'])
    op.create_index('ix_user_activity_logs_action', 'user_activity_logs', ['action'])
    op.create_index('ix_user_activity_logs_created_at', 'user_activity_logs', ['created_at'])


def downgrade() -> None:
    # 删除表（按照依赖关系逆序删除）
    op.drop_table('user_activity_logs')
    op.drop_table('password_resets')
    op.drop_table('user_sessions')
    op.drop_table('user_preferences')
    op.drop_table('users')