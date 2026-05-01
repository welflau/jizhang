from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int, user_id: int) -> Optional[Category]:
    """获取单个分类"""
    return db.query(Category).filter(
        and_(Category.id == category_id, Category.user_id == user_id)
    ).first()


def get_categories(
    db: Session,
    user_id: int,
    category_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Category]:
    """获取分类列表（支持按类型筛选）"""
    query = db.query(Category).filter(Category.user_id == user_id)
    
    if category_type:
        query = query.filter(Category.type == category_type)
    
    return query.order_by(Category.name).offset(skip).limit(limit).all()


def get_categories_by_type(db: Session, user_id: int) -> dict:
    """获取分类列表（按收入/支出分组）"""
    categories = db.query(Category).filter(Category.user_id == user_id).order_by(Category.name).all()
    
    result = {
        "income": [],
        "expense": []
    }
    
    for category in categories:
        if category.type == "income":
            result["income"].append(category)
        elif category.type == "expense":
            result["expense"].append(category)
    
    return result


def create_category(db: Session, category: CategoryCreate, user_id: int) -> Category:
    """创建分类"""
    # 检查同名分类是否已存在
    existing = db.query(Category).filter(
        and_(
            Category.user_id == user_id,
            Category.name == category.name,
            Category.type == category.type
        )
    ).first()
    
    if existing:
        raise ValueError(f"分类 '{category.name}' 已存在")
    
    db_category = Category(
        name=category.name,
        type=category.type,
        icon=category.icon,
        color=category.color,
        description=category.description,
        user_id=user_id
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


def update_category(
    db: Session,
    category_id: int,
    category_update: CategoryUpdate,
    user_id: int
) -> Optional[Category]:
    """更新分类"""
    db_category = get_category(db, category_id, user_id)
    
    if not db_category:
        return None
    
    # 如果更新名称，检查是否与其他分类重名
    if category_update.name and category_update.name != db_category.name:
        existing = db.query(Category).filter(
            and_(
                Category.user_id == user_id,
                Category.name == category_update.name,
                Category.type == db_category.type,
                Category.id != category_id
            )
        ).first()
        
        if existing:
            raise ValueError(f"分类 '{category_update.name}' 已存在")
    
    # 更新字段
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


def delete_category(db: Session, category_id: int, user_id: int) -> bool:
    """删除分类（需检查关联记录）"""
    db_category = get_category(db, category_id, user_id)
    
    if not db_category:
        return False
    
    # 检查是否有关联的交易记录
    transaction_count = db.query(Transaction).filter(
        and_(
            Transaction.category_id == category_id,
            Transaction.user_id == user_id
        )
    ).count()
    
    if transaction_count > 0:
        raise ValueError(f"无法删除分类，存在 {transaction_count} 条关联的交易记录")
    
    db.delete(db_category)
    db.commit()
    
    return True


def get_category_by_name(
    db: Session,
    user_id: int,
    name: str,
    category_type: str
) -> Optional[Category]:
    """根据名称和类型获取分类"""
    return db.query(Category).filter(
        and_(
            Category.user_id == user_id,
            Category.name == name,
            Category.type == category_type
        )
    ).first()


def get_category_transaction_count(db: Session, category_id: int, user_id: int) -> int:
    """获取分类关联的交易记录数量"""
    return db.query(Transaction).filter(
        and_(
            Transaction.category_id == category_id,
            Transaction.user_id == user_id
        )
    ).count()


def bulk_create_categories(
    db: Session,
    categories: List[CategoryCreate],
    user_id: int
) -> List[Category]:
    """批量创建分类"""
    created_categories = []
    
    for category_data in categories:
        # 检查是否已存在
        existing = get_category_by_name(
            db, user_id, category_data.name, category_data.type
        )
        
        if not existing:
            db_category = Category(
                name=category_data.name,
                type=category_data.type,
                icon=category_data.icon,
                color=category_data.color,
                description=category_data.description,
                user_id=user_id
            )
            db.add(db_category)
            created_categories.append(db_category)
    
    if created_categories:
        db.commit()
        for category in created_categories:
            db.refresh(category)
    
    return created_categories


def get_categories_with_stats(db: Session, user_id: int) -> List[dict]:
    """获取分类列表及其统计信息"""
    categories = db.query(Category).filter(Category.user_id == user_id).all()
    
    result = []
    for category in categories:
        transaction_count = get_category_transaction_count(db, category.id, user_id)
        
        result.append({
            "id": category.id,
            "name": category.name,
            "type": category.type,
            "icon": category.icon,
            "color": category.color,
            "description": category.description,
            "transaction_count": transaction_count,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        })
    
    return result