from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取分类列表
    可选参数 type: income/expense 用于筛选收入或支出分类
    """
    query = db.query(Category).filter(Category.user_id == current_user.id)
    
    if type:
        if type not in ["income", "expense"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="类型参数必须是 'income' 或 'expense'"
            )
        query = query.filter(Category.type == type)
    
    categories = query.order_by(Category.name).all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个分类详情
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新分类
    """
    # 验证分类类型
    if category_data.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="类型必须是 'income' 或 'expense'"
        )
    
    # 检查分类名称是否已存在（同一用户、同一类型下）
    existing_category = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == category_data.name,
        Category.type == category_data.type
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该类型下已存在名为 '{category_data.name}' 的分类"
        )
    
    # 创建分类
    new_category = Category(
        name=category_data.name,
        type=category_data.type,
        icon=category_data.icon,
        color=category_data.color,
        user_id=current_user.id
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新分类信息
    """
    # 查找分类
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 如果更新名称，检查是否与其他分类重名
    if category_data.name and category_data.name != category.name:
        existing_category = db.query(Category).filter(
            Category.user_id == current_user.id,
            Category.name == category_data.name,
            Category.type == category.type,
            Category.id != category_id
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该类型下已存在名为 '{category_data.name}' 的分类"
            )
    
    # 更新字段
    update_data = category_data.dict(exclude_unset=True)
    
    # 不允许修改分类类型（因为可能影响关联的交易记录）
    if "type" in update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不允许修改分类类型"
        )
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除分类
    如果分类下有关联的交易记录，需要设置 force=true 强制删除
    强制删除会将关联交易的分类设为 NULL
    """
    # 查找分类
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 检查是否有关联的交易记录
    transaction_count = db.query(Transaction).filter(
        Transaction.category_id == category_id,
        Transaction.user_id == current_user.id
    ).count()
    
    if transaction_count > 0:
        if not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下有 {transaction_count} 条交易记录，无法删除。如需强制删除，请设置 force=true"
            )
        
        # 强制删除：将关联交易的分类设为 NULL
        db.query(Transaction).filter(
            Transaction.category_id == category_id,
            Transaction.user_id == current_user.id
        ).update({"category_id": None})
    
    # 删除分类
    db.delete(category)
    db.commit()
    
    return None


@router.get("/grouped/by-type")
def get_categories_grouped(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取按收入/支出分组的分类列表
    返回格式: {"income": [...], "expense": [...]}
    """
    categories = db.query(Category).filter(
        Category.user_id == current_user.id
    ).order_by(Category.name).all()
    
    grouped = {
        "income": [],
        "expense": []
    }
    
    for category in categories:
        category_dict = {
            "id": category.id,
            "name": category.name,
            "type": category.type,
            "icon": category.icon,
            "color": category.color,
            "created_at": category.created_at.isoformat() if category.created_at else None
        }
        grouped[category.type].append(category_dict)
    
    return grouped


@router.get("/{category_id}/transactions/count")
def get_category_transaction_count(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取分类下的交易记录数量
    """
    # 验证分类存在且属于当前用户
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    count = db.query(Transaction).filter(
        Transaction.category_id == category_id,
        Transaction.user_id == current_user.id
    ).count()
    
    return {"category_id": category_id, "transaction_count": count}