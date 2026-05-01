"""
Category Service
分类管理服务
"""
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
        type: Optional[str] = None
    ) -> List[Category]:
        """
        获取分类列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            type: 分类类型（income/expense），可选
            
        Returns:
            分类列表
        """
        query = db.query(Category).filter(Category.user_id == user_id)
        
        if type:
            if type not in ['income', 'expense']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分类类型必须是 'income' 或 'expense'"
                )
            query = query.filter(Category.type == type)
        
        return query.order_by(Category.type, Category.name).all()
    
    @staticmethod
    def get_categories_grouped(db: Session, user_id: int) -> dict:
        """
        获取按类型分组的分类列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            按收入/支出分组的分类字典
        """
        categories = db.query(Category).filter(
            Category.user_id == user_id
        ).order_by(Category.name).all()
        
        grouped = {
            'income': [],
            'expense': []
        }
        
        for category in categories:
            grouped[category.type].append(category)
        
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
            HTTPException: 分类不存在
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
                detail="分类不存在"
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
            HTTPException: 分类名称已存在或数据验证失败
        """
        # 验证分类类型
        if category_data.type not in ['income', 'expense']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类类型必须是 'income' 或 'expense'"
            )
        
        # 检查分类名称是否已存在（同一用户、同一类型下）
        existing = db.query(Category).filter(
            and_(
                Category.user_id == user_id,
                Category.type == category_data.type,
                Category.name == category_data.name
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该类型下已存在名为 '{category_data.name}' 的分类"
            )
        
        # 验证图标（可选）
        if category_data.icon and len(category_data.icon) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图标字符串过长（最多50个字符）"
            )
        
        # 验证颜色（可选）
        if category_data.color:
            if not category_data.color.startswith('#') or len(category_data.color) not in [4, 7]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="颜色格式无效（应为 #RGB 或 #RRGGBB）"
                )
        
        # 创建分类
        category = Category(
            name=category_data.name,
            type=category_data.type,
            icon=category_data.icon,
            color=category_data.color,
            user_id=user_id
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        
        return category
    
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
            HTTPException: 分类不存在、名称冲突或数据验证失败
        """
        # 获取分类
        category = CategoryService.get_category_by_id(db, category_id, user_id)
        
        # 如果更新名称，检查是否冲突
        if category_data.name is not None and category_data.name != category.name:
            existing = db.query(Category).filter(
                and_(
                    Category.user_id == user_id,
                    Category.type == category.type,
                    Category.name == category_data.name,
                    Category.id != category_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"该类型下已存在名为 '{category_data.name}' 的分类"
                )
            
            category.name = category_data.name
        
        # 更新类型（需验证）
        if category_data.type is not None:
            if category_data.type not in ['income', 'expense']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分类类型必须是 'income' 或 'expense'"
                )
            
            # 检查是否有关联的交易记录
            transaction_count = db.query(Transaction).filter(
                Transaction.category_id == category_id
            ).count()
            
            if transaction_count > 0 and category_data.type != category.type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"该分类下有 {transaction_count} 条交易记录，无法更改类型"
                )
            
            category.type = category_data.type
        
        # 更新图标
        if category_data.icon is not None:
            if len(category_data.icon) > 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="图标字符串过长（最多50个字符）"
                )
            category.icon = category_data.icon
        
        # 更新颜色
        if category_data.color is not None:
            if category_data.color and (
                not category_data.color.startswith('#') or 
                len(category_data.color) not in [4, 7]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="颜色格式无效（应为 #RGB 或 #RRGGBB）"
                )
            category.color = category_data.color
        
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
            HTTPException: 分类不存在或有关联记录且未强制删除
        """
        # 获取分类
        category = CategoryService.get_category_by_id(db, category_id, user_id)
        
        # 检查关联的交易记录
        transactions = db.query(Transaction).filter(
            Transaction.category_id == category_id
        ).all()
        
        transaction_count = len(transactions)
        
        if transaction_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下有 {transaction_count} 条交易记录，无法删除。如需强制删除，请设置 force=true"
            )
        
        # 如果强制删除，先将关联记录的分类设为 NULL
        if force and transaction_count > 0:
            for transaction in transactions:
                transaction.category_id = None
            db.commit()
        
        # 删除分类
        db.delete(category)
        db.commit()
        
        return {
            "message": "分类删除成功",
            "deleted_category": category.name,
            "affected_transactions": transaction_count if force else 0
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
        
        # 统计交易记录数量和总金额
        transactions = db.query(Transaction).filter(
            Transaction.category_id == category_id
        ).all()
        
        total_amount = sum(t.amount for t in transactions)
        transaction_count = len(transactions)
        
        return {
            "category_id": category.id,
            "category_name": category.name,
            "category_type": category.type,
            "transaction_count": transaction_count,
            "total_amount": float(total_amount),
            "can_delete": transaction_count == 0
        }