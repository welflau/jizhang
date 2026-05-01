from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:
    """分类数据访问层"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int, user_id: int) -> Optional[Category]:
        """根据ID获取分类"""
        return self.db.query(Category).filter(
            and_(
                Category.id == category_id,
                Category.user_id == user_id
            )
        ).first()

    def get_by_name(self, name: str, user_id: int, category_type: str) -> Optional[Category]:
        """根据名称获取分类"""
        return self.db.query(Category).filter(
            and_(
                Category.name == name,
                Category.user_id == user_id,
                Category.type == category_type
            )
        ).first()

    def get_all(self, user_id: int, category_type: Optional[str] = None) -> List[Category]:
        """获取用户的所有分类"""
        query = self.db.query(Category).filter(Category.user_id == user_id)
        
        if category_type:
            query = query.filter(Category.type == category_type)
        
        return query.order_by(Category.created_at.desc()).all()

    def get_grouped_by_type(self, user_id: int) -> dict:
        """按类型分组获取分类"""
        categories = self.get_all(user_id)
        
        grouped = {
            'income': [],
            'expense': []
        }
        
        for category in categories:
            if category.type == 'income':
                grouped['income'].append(category)
            elif category.type == 'expense':
                grouped['expense'].append(category)
        
        return grouped

    def create(self, category_data: CategoryCreate, user_id: int) -> Category:
        """创建分类"""
        category = Category(
            name=category_data.name,
            type=category_data.type,
            icon=category_data.icon,
            color=category_data.color,
            description=category_data.description,
            user_id=user_id
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category

    def update(self, category_id: int, user_id: int, category_data: CategoryUpdate) -> Optional[Category]:
        """更新分类"""
        category = self.get_by_id(category_id, user_id)
        
        if not category:
            return None
        
        update_data = category_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(category, field, value)
        
        self.db.commit()
        self.db.refresh(category)
        
        return category

    def delete(self, category_id: int, user_id: int) -> bool:
        """删除分类"""
        category = self.get_by_id(category_id, user_id)
        
        if not category:
            return False
        
        self.db.delete(category)
        self.db.commit()
        
        return True

    def has_transactions(self, category_id: int, user_id: int) -> bool:
        """检查分类是否有关联的交易记录"""
        count = self.db.query(Transaction).filter(
            and_(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id
            )
        ).count()
        
        return count > 0

    def get_transaction_count(self, category_id: int, user_id: int) -> int:
        """获取分类关联的交易记录数量"""
        return self.db.query(Transaction).filter(
            and_(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id
            )
        ).count()

    def exists(self, category_id: int, user_id: int) -> bool:
        """检查分类是否存在"""
        return self.db.query(Category).filter(
            and_(
                Category.id == category_id,
                Category.user_id == user_id
            )
        ).count() > 0

    def name_exists(self, name: str, user_id: int, category_type: str, exclude_id: Optional[int] = None) -> bool:
        """检查分类名称是否已存在"""
        query = self.db.query(Category).filter(
            and_(
                Category.name == name,
                Category.user_id == user_id,
                Category.type == category_type
            )
        )
        
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        
        return query.count() > 0

    def get_default_categories(self, user_id: int) -> List[Category]:
        """获取默认分类（用于初始化）"""
        default_income = [
            {'name': '工资', 'type': 'income', 'icon': '💰', 'color': '#4CAF50'},
            {'name': '奖金', 'type': 'income', 'icon': '🎁', 'color': '#8BC34A'},
            {'name': '投资收益', 'type': 'income', 'icon': '📈', 'color': '#009688'},
            {'name': '其他收入', 'type': 'income', 'icon': '💵', 'color': '#00BCD4'},
        ]
        
        default_expense = [
            {'name': '餐饮', 'type': 'expense', 'icon': '🍔', 'color': '#FF9800'},
            {'name': '交通', 'type': 'expense', 'icon': '🚗', 'color': '#FF5722'},
            {'name': '购物', 'type': 'expense', 'icon': '🛍️', 'color': '#E91E63'},
            {'name': '娱乐', 'type': 'expense', 'icon': '🎮', 'color': '#9C27B0'},
            {'name': '医疗', 'type': 'expense', 'icon': '🏥', 'color': '#F44336'},
            {'name': '教育', 'type': 'expense', 'icon': '📚', 'color': '#3F51B5'},
            {'name': '住房', 'type': 'expense', 'icon': '🏠', 'color': '#2196F3'},
            {'name': '其他支出', 'type': 'expense', 'icon': '💸', 'color': '#607D8B'},
        ]
        
        categories = []
        
        for data in default_income + default_expense:
            if not self.get_by_name(data['name'], user_id, data['type']):
                category = Category(
                    name=data['name'],
                    type=data['type'],
                    icon=data['icon'],
                    color=data['color'],
                    user_id=user_id
                )
                self.db.add(category)
                categories.append(category)
        
        if categories:
            self.db.commit()
            for category in categories:
                self.db.refresh(category)
        
        return categories

    def bulk_delete(self, category_ids: List[int], user_id: int) -> int:
        """批量删除分类"""
        deleted_count = self.db.query(Category).filter(
            and_(
                Category.id.in_(category_ids),
                Category.user_id == user_id
            )
        ).delete(synchronize_session=False)
        
        self.db.commit()
        
        return deleted_count

    def get_statistics(self, user_id: int) -> dict:
        """获取分类统计信息"""
        categories = self.get_all(user_id)
        
        stats = {
            'total': len(categories),
            'income_count': 0,
            'expense_count': 0,
            'with_transactions': 0,
            'without_transactions': 0
        }
        
        for category in categories:
            if category.type == 'income':
                stats['income_count'] += 1
            elif category.type == 'expense':
                stats['expense_count'] += 1
            
            if self.has_transactions(category.id, user_id):
                stats['with_transactions'] += 1
            else:
                stats['without_transactions'] += 1
        
        return stats