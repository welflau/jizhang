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
    按收入/支出分组返回
    """
    categories = crud_category.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return categories


@router.get("/income", response_model=List[Category])
def get_income_categories(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> List[Category]:
    """
    获取收入类型的分类列表
    """
    categories = crud_category.get_by_type(
        db, user_id=current_user.id, category_type="income"
    )
    return categories


@router.get("/expense", response_model=List[Category])
def get_expense_categories(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> List[Category]:
    """
    获取支出类型的分类列表
    """
    categories = crud_category.get_by_type(
        db, user_id=current_user.id, category_type="expense"
    )
    return categories


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    *,
    db: Session = Depends(deps.get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Category:
    """
    创建新分类
    需要验证：
    - 分类名称不能为空
    - 分类类型必须是 income 或 expense
    - 同一用户下分类名称不能重复
    """
    # 验证分类类型
    if category_in.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类类型必须是 income 或 expense"
        )
    
    # 验证分类名称
    if not category_in.name or not category_in.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名称不能为空"
        )
    
    # 检查分类名称是否已存在
    existing_category = crud_category.get_by_name(
        db, user_id=current_user.id, name=category_in.name.strip()
    )
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该分类名称已存在"
        )
    
    # 创建分类
    category = crud_category.create_with_user(
        db, obj_in=category_in, user_id=current_user.id
    )
    return category


@router.get("/{category_id}", response_model=Category)
def get_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Category:
    """
    获取指定分类的详细信息
    """
    category = crud_category.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 验证权限
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该分类"
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
    需要验证：
    - 分类存在且属于当前用户
    - 如果修改名称，新名称不能与其他分类重复
    - 如果修改类型，需要检查是否有关联的交易记录
    """
    category = crud_category.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 验证权限
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改该分类"
        )
    
    # 如果修改了名称，检查新名称是否已存在
    if category_in.name and category_in.name.strip() != category.name:
        existing_category = crud_category.get_by_name(
            db, user_id=current_user.id, name=category_in.name.strip()
        )
        if existing_category and existing_category.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该分类名称已存在"
            )
    
    # 如果修改了类型，检查是否有关联的交易记录
    if category_in.type and category_in.type != category.type:
        if category_in.type not in ["income", "expense"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类类型必须是 income 或 expense"
            )
        
        # 检查是否有关联的交易记录
        transaction_count = crud_transaction.count_by_category(db, category_id=category_id)
        if transaction_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下有 {transaction_count} 条交易记录，无法修改类型"
            )
    
    # 更新分类
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
    删除分类
    需要验证：
    - 分类存在且属于当前用户
    - 分类下没有关联的交易记录
    """
    category = crud_category.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 验证权限
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除该分类"
        )
    
    # 检查是否有关联的交易记录
    transaction_count = crud_transaction.count_by_category(db, category_id=category_id)
    if transaction_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该分类下有 {transaction_count} 条交易记录，无法删除。请先删除或转移相关交易记录。"
        )
    
    # 删除分类
    crud_category.remove(db, id=category_id)
    return None


@router.get("/{category_id}/transactions/count")
def get_category_transaction_count(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> dict:
    """
    获取指定分类下的交易记录数量
    用于删除前的确认提示
    """
    category = crud_category.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 验证权限
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该分类"
        )
    
    count = crud_transaction.count_by_category(db, category_id=category_id)
    return {
        "category_id": category_id,
        "category_name": category.name,
        "transaction_count": count
    }