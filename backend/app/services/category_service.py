from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """分类管理服务"""
    
    @staticmethod
    def get_categories(
        db: Session,
        user_id: int,
        category_type: Optional[str] = None
    ) -> List[Category]:
        """
        获取分类列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            category_type: 分类类型（income/expense），为None时返回所有
            
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
        
        return query.order_by(Category.name).all()
    
    @staticmethod
    def get_categories_grouped(db: Session, user_id: int) -> dict:
        """
        获取按收入/支出分组的分类列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            分组后的分类字典 {'income': [...], 'expense': [...]}
        """
        all_categories = db.query(Category).filter(
            Category.user_id == user_id
        ).order_by(Category.name).all()
        
        grouped = {
            'income': [],
            'expense': []
        }
        
        for category in all_categories:
            if category.type == 'income':
                grouped['income'].append(category)
            elif category.type == 'expense':
                grouped['expense'].append(category)
        
        return grouped
    
    @staticmethod
    def get_category_by_id(
        db: Session,
        category_id: int,
        user_id: int
    ) -> Category:
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
    def create_category(
        db: Session,
        category_data: CategoryCreate,
        user_id: int
    ) -> Category:
        """
        创建分类
        
        Args:
            db: 数据库会话
            category_data: 分类创建数据
            user_id: 用户ID
            
        Returns:
            创建的分类对象
            
        Raises:
            HTTPException: 数据验证失败或分类名称重复
        """
        # 验证分类类型
        if category_data.type not in ['income', 'expense']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类类型必须是 'income' 或 'expense'"
            )
        
        # 验证分类名称长度
        if not category_data.name or len(category_data.name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称不能为空"
            )
        
        if len(category_data.name) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称长度不能超过50个字符"
            )
        
        # 检查同类型下分类名称是否重复
        existing_category = db.query(Category).filter(
            and_(
                Category.user_id == user_id,
                Category.name == category_data.name.strip(),
                Category.type == category_data.type
            )
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该类型下已存在名为 '{category_data.name}' 的分类"
            )
        
        # 创建分类
        new_category = Category(
            name=category_data.name.strip(),
            type=category_data.type,
            icon=category_data.icon,
            color=category_data.color,
            user_id=user_id
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        return new_category
    
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
        
        # 验证分类名称
        if category_data.name is not None:
            if len(category_data.name.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分类名称不能为空"
                )
            
            if len(category_data.name) > 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分类名称长度不能超过50个字符"
                )
            
            # 检查名称是否与其他分类重复（同类型下）
            existing_category = db.query(Category).filter(
                and_(
                    Category.user_id == user_id,
                    Category.name == category_data.name.strip(),
                    Category.type == category.type,
                    Category.id != category_id
                )
            ).first()
            
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"该类型下已存在名为 '{category_data.name}' 的分类"
                )
            
            category.name = category_data.name.strip()
        
        # 更新其他字段
        if category_data.icon is not None:
            category.icon = category_data.icon
        
        if category_data.color is not None:
            category.color = category_data.color
        
        # 注意：不允许修改分类类型，因为这会影响已有的交易记录
        
        db.commit()
        db.refresh(category)
        
        return category
    
    @staticmethod
    def delete_category(
        db: Session,
        category_id: int,
        user_id: int,
        force: bool = False
    ) -> dict:
        """
        删除分类
        
        Args:
            db: 数据库会话
            category_id: 分类ID
            user_id: 用户ID
            force: 是否强制删除（即使有关联记录）
            
        Returns:
            删除结果信息
            
        Raises:
            HTTPException: 分类不存在、无权限或存在关联记录
        """
        # 获取分类
        category = CategoryService.get_category_by_id(db, category_id, user_id)
        
        # 检查是否有关联的交易记录
        related_transactions_count = db.query(Transaction).filter(
            and_(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id
            )
        ).count()
        
        if related_transactions_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下有 {related_transactions_count} 条交易记录，无法删除。如需强制删除，请使用 force 参数"
            )
        
        # 如果强制删除，先将关联交易的分类ID设为NULL
        if force and related_transactions_count > 0:
            db.query(Transaction).filter(
                and_(
                    Transaction.category_id == category_id,
                    Transaction.user_id == user_id
                )
            ).update({Transaction.category_id: None})
        
        # 删除分类
        db.delete(category)
        db.commit()
        
        return {
            "message": "分类删除成功",
            "deleted_category_id": category_id,
            "affected_transactions": related_transactions_count if force else 0
        }
    
    @staticmethod
    def get_category_statistics(
        db: Session,
        category_id: int,
        user_id: int
    ) -> dict:
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
        
        # 统计关联的交易记录数量
        transaction_count = db.query(Transaction).filter(
            and_(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id
            )
        ).count()
        
        # 统计总金额
        from sqlalchemy import func
        total_amount = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id
            )
        ).scalar() or 0
        
        return {
            "category_id": category.id,
            "category_name": category.name,
            "category_type": category.type,
            "transaction_count": transaction_count,
            "total_amount": float(total_amount),
            "can_delete": transaction_count == 0
        }