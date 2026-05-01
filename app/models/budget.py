from datetime import datetime
from app import db


class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    period = db.Column(db.String(7), nullable=False)  # 格式: YYYY-MM
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 索引定义
    __table_args__ = (
        db.Index('idx_budget_user_id', 'user_id'),
        db.Index('idx_budget_period', 'period'),
        db.Index('idx_budget_user_period', 'user_id', 'period'),
        db.UniqueConstraint('user_id', 'category_id', 'period', name='uq_user_category_period'),
    )

    # 关系定义
    user = db.relationship('User', backref=db.backref('budgets', lazy='dynamic', cascade='all, delete-orphan'))
    category = db.relationship('Category', backref=db.backref('budgets', lazy='dynamic'))

    def __repr__(self):
        return f'<Budget {self.id}: User {self.user_id}, Period {self.period}, Amount {self.amount}>'

    def to_dict(self):
        """将预算对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'amount': float(self.amount),
            'period': self.period,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'category_name': self.category.name if self.category else None
        }

    @staticmethod
    def validate_period(period):
        """验证预算周期格式是否为 YYYY-MM"""
        import re
        pattern = r'^\d{4}-(0[1-9]|1[0-2])$'
        return bool(re.match(pattern, period))

    @classmethod
    def get_by_user_and_period(cls, user_id, period):
        """获取指定用户和周期的所有预算"""
        return cls.query.filter_by(user_id=user_id, period=period).all()

    @classmethod
    def get_by_user_category_period(cls, user_id, category_id, period):
        """获取指定用户、分类和周期的预算"""
        return cls.query.filter_by(
            user_id=user_id,
            category_id=category_id,
            period=period
        ).first()