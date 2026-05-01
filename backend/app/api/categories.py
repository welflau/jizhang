from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Category, Transaction, User
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
async def get_categories(
    type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取分类列表
    可选参数: type (income/expense) - 按收入/支出类型筛选
    """
    query = db.query(Category).filter(Category.user_id == current_user.id)
    
    if type:
        if type not in ["income", "expense"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="类型必须是 'income' 或 'expense'"
            )
        query = query.filter(Category.type == type)
    
    categories = query.order_by(Category.name).all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个分类详情"""
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


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新分类
    - name: 分类名称（必填，1-50字符）
    - type: 类型（必填，income/expense）
    - icon: 图标（可选）
    - color: 颜色（可选，十六进制格式）
    """
    # 验证类型
    if category_data.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="类型必须是 'income' 或 'expense'"
        )
    
    # 验证名称长度
    if not category_data.name or len(category_data.name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名称不能为空"
        )
    
    if len(category_data.name) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名称不能超过50个字符"
        )
    
    # 检查同名分类是否已存在
    existing = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == category_data.name.strip(),
        Category.type == category_data.type
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该类型下已存在名为 '{category_data.name}' 的分类"
        )
    
    # 验证颜色格式（如果提供）
    if category_data.color:
        color = category_data.color.strip()
        if not color.startswith('#') or len(color) != 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="颜色格式必须是十六进制格式（如 #FF5733）"
            )
        try:
            int(color[1:], 16)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="颜色格式无效"
            )
    
    # 创建分类
    new_category = Category(
        name=category_data.name.strip(),
        type=category_data.type,
        icon=category_data.icon.strip() if category_data.icon else None,
        color=category_data.color.strip() if category_data.color else None,
        user_id=current_user.id
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新分类信息
    - name: 分类名称（可选，1-50字符）
    - icon: 图标（可选）
    - color: 颜色（可选，十六进制格式）
    注意: 不允许修改分类类型(type)
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
    
    # 更新名称
    if category_data.name is not None:
        name = category_data.name.strip()
        
        if len(name) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称不能为空"
            )
        
        if len(name) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称不能超过50个字符"
            )
        
        # 检查同名分类
        if name != category.name:
            existing = db.query(Category).filter(
                Category.user_id == current_user.id,
                Category.name == name,
                Category.type == category.type,
                Category.id != category_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"该类型下已存在名为 '{name}' 的分类"
                )
        
        category.name = name
    
    # 更新图标
    if category_data.icon is not None:
        category.icon = category_data.icon.strip() if category_data.icon else None
    
    # 更新颜色
    if category_data.color is not None:
        if category_data.color:
            color = category_data.color.strip()
            if not color.startswith('#') or len(color) != 7:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="颜色格式必须是十六进制格式（如 #FF5733）"
                )
            try:
                int(color[1:], 16)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="颜色格式无效"
                )
            category.color = color
        else:
            category.color = None
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除分类
    注意: 如果该分类下存在交易记录，将无法删除
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法删除该分类，因为存在 {transaction_count} 条关联的交易记录。请先删除或转移这些记录。"
        )
    
    # 删除分类
    db.delete(category)
    db.commit()
    
    return None


@router.get("/stats/summary")
async def get_category_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取分类统计信息
    返回每个分类的交易数量和总金额
    """
    from sqlalchemy import func
    
    # 查询每个分类的统计信息
    stats = db.query(
        Category.id,
        Category.name,
        Category.type,
        Category.icon,
        Category.color,
        func.count(Transaction.id).label('transaction_count'),
        func.coalesce(func.sum(Transaction.amount), 0).label('total_amount')
    ).outerjoin(
        Transaction,
        (Transaction.category_id == Category.id) & (Transaction.user_id == current_user.id)
    ).filter(
        Category.user_id == current_user.id
    ).group_by(
        Category.id
    ).order_by(
        Category.type, Category.name
    ).all()
    
    # 格式化结果
    result = {
        "income": [],
        "expense": []
    }
    
    for stat in stats:
        category_stat = {
            "id": stat.id,
            "name": stat.name,
            "type": stat.type,
            "icon": stat.icon,
            "color": stat.color,
            "transaction_count": stat.transaction_count,
            "total_amount": float(stat.total_amount)
        }
        
        if stat.type == "income":
            result["income"].append(category_stat)
        else:
            result["expense"].append(category_stat)
    
    return result