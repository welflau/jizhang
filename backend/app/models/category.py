from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TransactionType(str, enum.Enum):
    """交易类型枚举"""
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    """分类模型"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    type = Column(Enum(TransactionType), nullable=False, index=True)
    icon = Column(String(50), default="📁")
    color = Column(String(20), default="#1a1a2e")
    description = Column(String(200))
    is_system = Column(Boolean, default=False, comment="系统预设分类不可删除")
    is_active = Column(Boolean, default=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"

    def to_dict(self, include_stats=False):
        """转换为字典"""
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "icon": self.icon,
            "color": self.color,
            "description": self.description,
            "is_system": self.is_system,
            "is_active": self.is_active,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_stats:
            data["transaction_count"] = len(self.transactions)
            data["total_amount"] = sum(t.amount for t in self.transactions if t.is_active)
        
        return data

    @classmethod
    def get_default_categories(cls, user_id: int):
        """获取默认分类列表"""
        return [
            # 收入分类
            cls(name="工资", type=TransactionType.INCOME, icon="💰", color="#2ecc71", 
                description="工资收入", is_system=True, user_id=user_id),
            cls(name="奖金", type=TransactionType.INCOME, icon="🎁", color="#27ae60",
                description="奖金收入", is_system=True, user_id=user_id),
            cls(name="投资收益", type=TransactionType.INCOME, icon="📈", color="#16a085",
                description="投资理财收益", is_system=True, user_id=user_id),
            cls(name="兼职", type=TransactionType.INCOME, icon="💼", color="#1abc9c",
                description="兼职收入", is_system=True, user_id=user_id),
            cls(name="其他收入", type=TransactionType.INCOME, icon="💵", color="#3498db",
                description="其他收入", is_system=True, user_id=user_id),
            
            # 支出分类
            cls(name="餐饮", type=TransactionType.EXPENSE, icon="🍔", color="#e74c3c",
                description="餐饮支出", is_system=True, user_id=user_id),
            cls(name="交通", type=TransactionType.EXPENSE, icon="🚗", color="#c0392b",
                description="交通出行", is_system=True, user_id=user_id),
            cls(name="购物", type=TransactionType.EXPENSE, icon="🛒", color="#e67e22",
                description="购物消费", is_system=True, user_id=user_id),
            cls(name="娱乐", type=TransactionType.EXPENSE, icon="🎮", color="#d35400",
                description="娱乐休闲", is_system=True, user_id=user_id),
            cls(name="医疗", type=TransactionType.EXPENSE, icon="🏥", color="#9b59b6",
                description="医疗健康", is_system=True, user_id=user_id),
            cls(name="教育", type=TransactionType.EXPENSE, icon="📚", color="#8e44ad",
                description="教育培训", is_system=True, user_id=user_id),
            cls(name="住房", type=TransactionType.EXPENSE, icon="🏠", color="#34495e",
                description="房租房贷", is_system=True, user_id=user_id),
            cls(name="通讯", type=TransactionType.EXPENSE, icon="📱", color="#2c3e50",
                description="通讯费用", is_system=True, user_id=user_id),
            cls(name="其他支出", type=TransactionType.EXPENSE, icon="💸", color="#95a5a6",
                description="其他支出", is_system=True, user_id=user_id),
        ]

    def can_delete(self):
        """检查是否可以删除"""
        if self.is_system:
            return False, "系统预设分类不可删除"
        
        active_transactions = [t for t in self.transactions if t.is_active]
        if active_transactions:
            return False, f"该分类下有 {len(active_transactions)} 条关联记录，无法删除"
        
        return True, ""

    def validate_update(self, **kwargs):
        """验证更新数据"""
        errors = []
        
        if 'name' in kwargs:
            name = kwargs['name']
            if not name or len(name.strip()) == 0:
                errors.append("分类名称不能为空")
            elif len(name) > 50:
                errors.append("分类名称不能超过50个字符")
        
        if 'type' in kwargs and self.is_system:
            if kwargs['type'] != self.type:
                errors.append("系统预设分类不能修改类型")
        
        if 'description' in kwargs:
            description = kwargs['description']
            if description and len(description) > 200:
                errors.append("描述不能超过200个字符")
        
        if 'color' in kwargs:
            color = kwargs['color']
            if color and not color.startswith('#'):
                errors.append("颜色格式不正确，应为十六进制格式")
        
        return errors