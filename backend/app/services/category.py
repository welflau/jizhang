from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """分类服务类"""

    @staticmethod
    def get_categories(
        db: Session,
        user_id: int,
        category_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """
        获取分类列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            category_type: 分类类型（income/expense），可选
            skip: 跳过记录数
            limit: 返回记录数限制
            
        Returns:
            分类列表
        """
        query = db.query(Category).filter(Category.user_id == user_id)
        
        if category_type:
            if category_type not in ['income', 'expense']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分类类型必须是 'income' 或 'expense'"
                )
            query = query.filter(Category.type == category_type)
        
        return query.order_by(Category.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_categories_grouped(db: Session, user_id: int) -> dict:
        """
        获取按收入/支出分组的分类列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            分组后的分类字典
        """
        categories = db.query(Category).filter(Category.user_id == user_id).order_by(Category.name).all()
        
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

    @staticmethod
    def get_category_by_id(db: Session, category_id: int, user_id: int) -> Category:
        """
        根据ID获取分类
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            user_id: 用户ID
            
        Returns:
            分类对象
            
        Raises:
            HTTPException: 分类不存在或无权限访问
        """
        category = db.query(Category).filter(
            and_(
                Category.id == category_id,
                Category.user_id == user_id
            )
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在或无权限访问"
            )
        
        return category

    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate, user_id: int) -> Category:
        """
        创建分类
        
        Args:
            db: 数据库会话
            category_data: 分类创建数据
            user_id: 用户ID
            
        Returns:
            创建的分类对象
            
        Raises:
            HTTPException: 分类名称已存在或数据验证失败
        """
        # 验证分类类型
        if category_data.type not in ['income', 'expense']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类类型必须是 'income' 或 'expense'"
            )
        
        # 检查同类型下分类名称是否已存在
        existing_category = db.query(Category).filter(
            and_(
                Category.user_id == user_id,
                Category.name == category_data.name,
                Category.type == category_data.type
            )
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该类型下已存在名为 '{category_data.name}' 的分类"
            )
        
        # 创建分类
        db_category = Category(
            name=category_data.name,
            type=category_data.type,
            icon=category_data.icon,
            color=category_data.color,
            description=category_data.description,
            user_id=user_id
        )
        
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        return db_category

    @staticmethod
    def update_category(
        db: Session,
        category_id: int,
        category_data: CategoryUpdate,
        user_id: int
    ) -> Category:
        """
        更新分类
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            category_data: 分类更新数据
            user_id: 用户ID
            
        Returns:
            更新后的分类对象
            
        Raises:
            HTTPException: 分类不存在、无权限或数据验证失败
        """
        # 获取分类
        category = CategoryService.get_category_by_id(db, category_id, user_id)
        
        # 如果更新名称，检查是否与其他分类重名
        if category_data.name and category_data.name != category.name:
            existing_category = db.query(Category).filter(
                and_(
                    Category.user_id == user_id,
                    Category.name == category_data.name,
                    Category.type == category.type,
                    Category.id != category_id
                )
            ).first()
            
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"该类型下已存在名为 '{category_data.name}' 的分类"
                )
        
        # 更新字段
        update_data = category_data.dict(exclude_unset=True)
        
        # 不允许修改分类类型
        if 'type' in update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不允许修改分类类型"
            )
        
        for field, value in update_data.items():
            setattr(category, field, value)
        
        db.commit()
        db.refresh(category)
        
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int, user_id: int) -> dict:
        """
        删除分类
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            user_id: 用户ID
            
        Returns:
            删除结果消息
            
        Raises:
            HTTPException: 分类不存在、无权限或存在关联记录
        """
        # 获取分类
        category = CategoryService.get_category_by_id(db, category_id, user_id)
        
        # 检查是否有关联的交易记录
        transaction_count = db.query(Transaction).filter(
            and_(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id
            )
        ).count()
        
        if transaction_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下存在 {transaction_count} 条交易记录，无法删除。请先删除或转移相关记录。"
            )
        
        # 删除分类
        db.delete(category)
        db.commit()
        
        return {"message": "分类删除成功", "deleted_id": category_id}

    @staticmethod
    def get_category_statistics(db: Session, category_id: int, user_id: int) -> dict:
        """
        获取分类统计信息
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            user_id: 用户ID
            
        Returns:
            分类统计信息
        """
        # 获取分类
        category = CategoryService.get_category_by_id(db, category_id, user_id)
        
        # 统计交易记录数量和总金额
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id
            )
        ).all()
        
        total_amount = sum(t.amount for t in transactions)
        transaction_count = len(transactions)
        
        return {
            "category_id": category_id,
            "category_name": category.name,
            "category_type": category.type,
            "transaction_count": transaction_count,
            "total_amount": float(total_amount)
        }

    @staticmethod
    def validate_category_access(db: Session, category_id: int, user_id: int) -> bool:
        """
        验证用户是否有权限访问指定分类
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            user_id: 用户ID
            
        Returns:
            是否有权限
        """
        category = db.query(Category).filter(
            and_(
                Category.id == category_id,
                Category.user_id == user_id
            )
        ).first()
        
        return category is not None