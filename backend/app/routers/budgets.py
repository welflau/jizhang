from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import re

from ..database import get_db
from ..models import Budget, Transaction
from ..schemas import BudgetCreate, BudgetUpdate, BudgetResponse
from ..auth import get_current_user
from sqlalchemy import func, and_

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


def validate_period_format(period: str) -> bool:
    """验证期间格式 YYYY-MM"""
    pattern = r'^\d{4}-(0[1-9]|1[0-2])$'
    return bool(re.match(pattern, period))


def calculate_budget_usage(db: Session, budget: Budget) -> dict:
    """计算预算使用进度"""
    # 查询该预算期间内该分类的支出总额
    spent = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.user_id == budget.user_id,
            Transaction.category_id == budget.category_id,
            Transaction.type == 'expense',
            func.strftime('%Y-%m', Transaction.date) == budget.period
        )
    ).scalar() or 0.0
    
    percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
    remaining = budget.amount - spent
    
    return {
        "spent": float(spent),
        "percentage": round(percentage, 2),
        "remaining": float(remaining)
    }


@router.post("", response_model=BudgetResponse, status_code=201)
def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建预算"""
    # 参数校验
    if budget_data.amount <= 0:
        raise HTTPException(status_code=400, detail="预算金额必须大于0")
    
    if not validate_period_format(budget_data.period):
        raise HTTPException(status_code=400, detail="期间格式错误，应为 YYYY-MM")
    
    # 检查该用户在该期间该分类是否已存在预算
    existing = db.query(Budget).filter(
        and_(
            Budget.user_id == current_user["id"],
            Budget.category_id == budget_data.category_id,
            Budget.period == budget_data.period
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该期间该分类的预算已存在")
    
    # 创建预算
    new_budget = Budget(
        user_id=current_user["id"],
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
        percentage=usage["percentage"],
        remaining=usage["remaining"],
        created_at=new_budget.created_at,
        updated_at=new_budget.updated_at
    )


@router.get("", response_model=List[BudgetResponse])
def get_budgets(
    period: Optional[str] = Query(None, description="筛选期间 YYYY-MM"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """查询当前用户预算列表"""
    # 期间格式校验
    if period and not validate_period_format(period):
        raise HTTPException(status_code=400, detail="期间格式错误，应为 YYYY-MM")
    
    # 构建查询
    query = db.query(Budget).filter(Budget.user_id == current_user["id"])
    
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
            percentage=usage["percentage"],
            remaining=usage["remaining"],
            created_at=budget.created_at,
            updated_at=budget.updated_at
        ))
    
    return result


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新预算"""
    # 查询预算
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="预算不存在")
    
    # 权限校验
    if budget.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="无权操作此预算")
    
    # 参数校验
    if budget_data.amount is not None:
        if budget_data.amount <= 0:
            raise HTTPException(status_code=400, detail="预算金额必须大于0")
        budget.amount = budget_data.amount
    
    if budget_data.period is not None:
        if not validate_period_format(budget_data.period):
            raise HTTPException(status_code=400, detail="期间格式错误，应为 YYYY-MM")
        
        # 检查新期间是否与其他预算冲突
        if budget_data.period != budget.period:
            existing = db.query(Budget).filter(
                and_(
                    Budget.user_id == current_user["id"],
                    Budget.category_id == budget.category_id,
                    Budget.period == budget_data.period,
                    Budget.id != budget_id
                )
            ).first()
            
            if existing:
                raise HTTPException(status_code=400, detail="该期间该分类的预算已存在")
        
        budget.period = budget_data.period
    
    if budget_data.category_id is not None:
        # 检查新分类是否与其他预算冲突
        if budget_data.category_id != budget.category_id:
            existing = db.query(Budget).filter(
                and_(
                    Budget.user_id == current_user["id"],
                    Budget.category_id == budget_data.category_id,
                    Budget.period == budget.period,
                    Budget.id != budget_id
                )
            ).first()
            
            if existing:
                raise HTTPException(status_code=400, detail="该期间该分类的预算已存在")
        
        budget.category_id = budget_data.category_id
    
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
        percentage=usage["percentage"],
        remaining=usage["remaining"],
        created_at=budget.created_at,
        updated_at=budget.updated_at
    )


@router.delete("/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除预算"""
    # 查询预算
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="预算不存在")
    
    # 权限校验
    if budget.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="无权操作此预算")
    
    db.delete(budget)
    db.commit()
    
    return None