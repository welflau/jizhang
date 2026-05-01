from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.category import Category as CategorySchema, CategoryCreate, CategoryUpdate

router = APIRouter()


@router.get("/", response_model=List[CategorySchema])
def get_categories(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    type: str = None,
) -> List[Category]:
    """
    获取当前用户的分类列表
    可选参数 type: income/expense 用于筛选收入或支出分类
    """
    query = db.query(Category).filter(Category.user_id == current_user.id)
    
    if type:
        if type not in ["income", "expense"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type must be 'income' or 'expense'"
            )
        query = query.filter(Category.type == type)
    
    categories = query.order_by(Category.type, Category.name).all()
    return categories


@router.get("/{category_id}", response_model=CategorySchema)
def get_category(
    category_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Category:
    """
    获取指定分类详情
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Category:
    """
    创建新分类
    """
    # 验证分类类型
    if category_in.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type must be 'income' or 'expense'"
        )
    
    # 检查分类名称是否已存在（同一用户、同一类型下）
    existing_category = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.type == category_in.type,
        Category.name == category_in.name
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category_in.name}' already exists for {category_in.type}"
        )
    
    # 创建分类
    category = Category(
        name=category_in.name,
        type=category_in.type,
        icon=category_in.icon,
        color=category_in.color,
        user_id=current_user.id
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Category:
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
            detail="Category not found"
        )
    
    # 如果更新名称，检查是否与其他分类重名
    if category_in.name and category_in.name != category.name:
        existing_category = db.query(Category).filter(
            Category.user_id == current_user.id,
            Category.type == category.type,
            Category.name == category_in.name,
            Category.id != category_id
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category_in.name}' already exists"
            )
    
    # 更新分类字段
    update_data = category_in.dict(exclude_unset=True)
    
    # 不允许修改分类类型（因为可能影响已有交易记录）
    if "type" in update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change category type"
        )
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    删除分类
    如果分类下有关联的交易记录，则不允许删除
    """
    # 查找分类
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # 检查是否有关联的交易记录
    transaction_count = db.query(Transaction).filter(
        Transaction.category_id == category_id
    ).count()
    
    if transaction_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {transaction_count} associated transactions. Please reassign or delete the transactions first."
        )
    
    # 删除分类
    db.delete(category)
    db.commit()
    
    return None


@router.get("/grouped/by-type", response_model=dict)
def get_categories_grouped(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    获取按收入/支出分组的分类列表
    返回格式: {"income": [...], "expense": [...]}
    """
    categories = db.query(Category).filter(
        Category.user_id == current_user.id
    ).order_by(Category.name).all()
    
    income_categories = [
        CategorySchema.from_orm(cat) for cat in categories if cat.type == "income"
    ]
    expense_categories = [
        CategorySchema.from_orm(cat) for cat in categories if cat.type == "expense"
    ]
    
    return {
        "income": income_categories,
        "expense": expense_categories
    }