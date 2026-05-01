from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class PaymentMethod(Base):
    """支付方式模型"""
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False, comment="支付方式名称，如：现金、支付宝、微信、银行卡等")
    icon = Column(String(50), default="wallet", comment="图标标识")
    color = Column(String(20), default="#1890ff", comment="颜色标识")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="payment_methods")
    transactions = relationship("Transaction", back_populates="payment_method", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, name='{self.name}', user_id={self.user_id})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "icon": self.icon,
            "color": self.color,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }