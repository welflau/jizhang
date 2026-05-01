from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_category, crud_transaction
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[Category])
def get_categories(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> List[Category]:
    """
    获取当前用户的所有分类列表
    """
    categories = crud_category.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return categories


@router.get("/grouped", response_model=dict)
def get_categories_grouped(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    """
    获取按收入/支出分组的分类列表
    返回格式: {"income": [...], "expense": [...]}
    """
    all_categories = crud_category.get_multi_by_user(
        db, user_id=current_user.id, skip=0, limit=1000
    )
    
    income_categories = [cat for cat in all_categories if cat.type == "income"]
    expense_categories = [cat for cat in all_categories if cat.type == "expense"]
    
    return {
        "income": income_categories,
        "expense": expense_categories
    }


@router.get("/{category_id}", response_model=Category)
def get_category(
    category_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Category:
    """
    根据ID获取分类详情
    """
    category = crud_category.get(db, id=category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此分类"
        )
    
    return category


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    *,
    db: Session = Depends(deps.get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Category:
    """
    创建新分类
    """
    # 验证分类类型
    if category_in.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类类型必须是 'income' 或 'expense'"
        )
    
    # 验证分类名称不为空
    if not category_in.name or not category_in.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名称不能为空"
        )
    
    # 检查同名分类是否已存在
    existing_category = crud_category.get_by_name_and_type(
        db, 
        user_id=current_user.id,
        name=category_in.name.strip(),
        category_type=category_in.type
    )
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该类型下已存在名为 '{category_in.name}' 的分类"
        )
    
    # 创建分类
    category = crud_category.create_with_user(
        db, obj_in=category_in, user_id=current_user.id
    )
    
    return category


@router.put("/{category_id}", response_model=Category)
def update_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Category:
    """
    更新分类信息
    """
    category = crud_category.get(db, id=category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此分类"
        )
    
    # 如果更新了名称，检查是否与其他分类重名
    if category_in.name and category_in.name.strip() != category.name:
        category_type = category_in.type if category_in.type else category.type
        existing_category = crud_category.get_by_name_and_type(
            db,
            user_id=current_user.id,
            name=category_in.name.strip(),
            category_type=category_type
        )
        
        if existing_category and existing_category.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该类型下已存在名为 '{category_in.name}' 的分类"
            )
    
    # 验证分类类型（如果提供）
    if category_in.type and category_in.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类类型必须是 'income' 或 'expense'"
        )
    
    # 如果修改了分类类型，检查是否有关联的交易记录
    if category_in.type and category_in.type != category.type:
        transaction_count = crud_transaction.count_by_category(db, category_id=category_id)
        if transaction_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下有 {transaction_count} 条交易记录，无法修改分类类型"
            )
    
    category = crud_category.update(db, db_obj=category, obj_in=category_in)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> None:
    """
    删除分类（需检查是否有关联的交易记录）
    """
    category = crud_category.get(db, id=category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此分类"
        )
    
    # 检查是否有关联的交易记录
    transaction_count = crud_transaction.count_by_category(db, category_id=category_id)
    
    if transaction_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该分类下有 {transaction_count} 条交易记录，无法删除。请先删除或转移相关交易记录。"
        )
    
    crud_category.remove(db, id=category_id)
    
    return None


@router.get("/{category_id}/transactions/count", response_model=dict)
def get_category_transaction_count(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    """
    获取分类下的交易记录数量
    """
    category = crud_category.get(db, id=category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此分类"
        )
    
    count = crud_transaction.count_by_category(db, category_id=category_id)
    
    return {
        "category_id": category_id,
        "category_name": category.name,
        "transaction_count": count
    }