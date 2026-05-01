from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get("/", response_model=schemas.CategoryListResponse)
def get_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取分类列表（按收入/支出分组）
    """
    # 获取所有分类
    categories = db.query(models.Category).filter(
        models.Category.user_id == current_user.id
    ).order_by(models.Category.type, models.Category.name).all()
    
    # 按类型分组
    income_categories = [cat for cat in categories if cat.type == "income"]
    expense_categories = [cat for cat in categories if cat.type == "expense"]
    
    return schemas.CategoryListResponse(
        income=[schemas.Category.model_validate(cat) for cat in income_categories],
        expense=[schemas.Category.model_validate(cat) for cat in expense_categories]
    )


@router.get("/{category_id}", response_model=schemas.Category)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取单个分类详情
    """
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    创建新分类
    """
    # 检查分类名称是否已存在（同一用户、同一类型下）
    existing_category = db.query(models.Category).filter(
        models.Category.user_id == current_user.id,
        models.Category.name == category_data.name,
        models.Category.type == category_data.type
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category_data.name}' already exists for {category_data.type}"
        )
    
    # 验证类型
    if category_data.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category type must be 'income' or 'expense'"
        )
    
    # 创建分类
    new_category = models.Category(
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


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    category_data: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    更新分类信息
    """
    # 查找分类
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # 如果更新名称，检查是否与其他分类重名
    if category_data.name is not None and category_data.name != category.name:
        existing_category = db.query(models.Category).filter(
            models.Category.user_id == current_user.id,
            models.Category.name == category_data.name,
            models.Category.type == category.type,
            models.Category.id != category_id
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category_data.name}' already exists"
            )
    
    # 更新字段
    update_data = category_data.model_dump(exclude_unset=True)
    
    # 验证类型（如果提供）
    if "type" in update_data and update_data["type"] not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category type must be 'income' or 'expense'"
        )
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    删除分类（需检查是否有关联记录）
    """
    # 查找分类
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # 检查是否有关联的记账记录
    record_count = db.query(models.Record).filter(
        models.Record.category_id == category_id
    ).count()
    
    if record_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category. It has {record_count} associated record(s). Please delete or reassign the records first."
        )
    
    # 删除分类
    db.delete(category)
    db.commit()
    
    return None