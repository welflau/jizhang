from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from sqlalchemy import func, and_

router = APIRouter()


def validate_period_format(period: str) -> bool:
    """验证 period 格式 (YYYY-MM)"""
    try:
        datetime.strptime(period, "%Y-%m")
        return True
    except ValueError:
        return False


def calculate_budget_usage(db: Session, budget: Budget) -> dict:
    """计算预算使用进度"""
    # 查询该预算分类在该周期内的支出总额
    spent = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.user_id == budget.user_id,
            Transaction.category_id == budget.category_id,
            Transaction.type == "expense",
            func.strftime("%Y-%m", Transaction.date) == budget.period
        )
    ).scalar() or 0.0

    remaining = budget.amount - spent
    percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0

    return {
        "spent": float(spent),
        "remaining": float(remaining),
        "percentage": round(percentage, 2)
    }


@router.post("/budgets", response_model=BudgetResponse, status_code=201)
def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建预算"""
    # 参数校验
    if budget_data.amount <= 0:
        raise HTTPException(status_code=400, detail="预算金额必须大于 0")
    
    if not validate_period_format(budget_data.period):
        raise HTTPException(status_code=400, detail="period 格式错误，应为 YYYY-MM")
    
    # 检查该用户在该周期和分类下是否已存在预算
    existing_budget = db.query(Budget).filter(
        and_(
            Budget.user_id == current_user.id,
            Budget.category_id == budget_data.category_id,
            Budget.period == budget_data.period
        )
    ).first()
    
    if existing_budget:
        raise HTTPException(
            status_code=400,
            detail="该分类在此周期已存在预算"
        )
    
    # 创建预算
    new_budget = Budget(
        user_id=current_user.id,
        category_id=budget_data.category_id,
        amount=budget_data.amount,
        period=budget_data.period
    )
    
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    
    # 计算使用进度
    usage = calculate_budget_usage(db, new_budget)
    
    return BudgetResponse(
        id=new_budget.id,
        user_id=new_budget.user_id,
        category_id=new_budget.category_id,
        category_name=new_budget.category.name if new_budget.category else None,
        amount=new_budget.amount,
        period=new_budget.period,
        spent=usage["spent"],
        remaining=usage["remaining"],
        percentage=usage["percentage"],
        created_at=new_budget.created_at,
        updated_at=new_budget.updated_at
    )


@router.get("/budgets", response_model=List[BudgetResponse])
def get_budgets(
    period: Optional[str] = Query(None, description="筛选周期 (YYYY-MM)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询当前用户预算列表"""
    # period 格式校验
    if period and not validate_period_format(period):
        raise HTTPException(status_code=400, detail="period 格式错误，应为 YYYY-MM")
    
    # 构建查询
    query = db.query(Budget).filter(Budget.user_id == current_user.id)
    
    if period:
        query = query.filter(Budget.period == period)
    
    budgets = query.order_by(Budget.period.desc(), Budget.created_at.desc()).all()
    
    # 计算每个预算的使用进度
    result = []
    for budget in budgets:
        usage = calculate_budget_usage(db, budget)
        result.append(BudgetResponse(
            id=budget.id,
            user_id=budget.user_id,
            category_id=budget.category_id,
            category_name=budget.category.name if budget.category else None,
            amount=budget.amount,
            period=budget.period,
            spent=usage["spent"],
            remaining=usage["remaining"],
            percentage=usage["percentage"],
            created_at=budget.created_at,
            updated_at=budget.updated_at
        ))
    
    return result


@router.get("/budgets/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询单个预算详情"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="预算不存在")
    
    # 权限校验
    if budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此预算")
    
    # 计算使用进度
    usage = calculate_budget_usage(db, budget)
    
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category_id=budget.category_id,
        category_name=budget.category.name if budget.category else None,
        amount=budget.amount,
        period=budget.period,
        spent=usage["spent"],
        remaining=usage["remaining"],
        percentage=usage["percentage"],
        created_at=budget.created_at,
        updated_at=budget.updated_at
    )


@router.put("/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新预算"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="预算不存在")
    
    # 权限校验
    if budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此预算")
    
    # 参数校验
    if budget_data.amount is not None and budget_data.amount <= 0:
        raise HTTPException(status_code=400, detail="预算金额必须大于 0")
    
    if budget_data.period is not None and not validate_period_format(budget_data.period):
        raise HTTPException(status_code=400, detail="period 格式错误，应为 YYYY-MM")
    
    # 如果更新了 category_id 或 period，检查是否与其他预算冲突
    if budget_data.category_id is not None or budget_data.period is not None:
        new_category_id = budget_data.category_id if budget_data.category_id is not None else budget.category_id
        new_period = budget_data.period if budget_data.period is not None else budget.period
        
        existing_budget = db.query(Budget).filter(
            and_(
                Budget.user_id == current_user.id,
                Budget.category_id == new_category_id,
                Budget.period == new_period,
                Budget.id != budget_id
            )
        ).first()
        
        if existing_budget:
            raise HTTPException(
                status_code=400,
                detail="该分类在此周期已存在其他预算"
            )
    
    # 更新字段
    if budget_data.category_id is not None:
        budget.category_id = budget_data.category_id
    if budget_data.amount is not None:
        budget.amount = budget_data.amount
    if budget_data.period is not None:
        budget.period = budget_data.period
    
    budget.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(budget)
    
    # 计算使用进度
    usage = calculate_budget_usage(db, budget)
    
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category_id=budget.category_id,
        category_name=budget.category.name if budget.category else None,
        amount=budget.amount,
        period=budget.period,
        spent=usage["spent"],
        remaining=usage["remaining"],
        percentage=usage["percentage"],
        created_at=budget.created_at,
        updated_at=budget.updated_at
    )


@router.delete("/budgets/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除预算"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="预算不存在")
    
    # 权限校验
    if budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此预算")
    
    db.delete(budget)
    db.commit()
    
    return None
