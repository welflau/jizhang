from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import re

from ..database import get_db
from ..models import Budget, Transaction, User
from ..schemas import BudgetCreate, BudgetUpdate, BudgetResponse
from ..auth import get_current_user

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


def validate_period(period: str) -> bool:
    """验证预算周期格式 (YYYY-MM)"""
    pattern = r'^\d{4}-(0[1-9]|1[0-2])$'
    return bool(re.match(pattern, period))


def calculate_budget_usage(db: Session, budget: Budget) -> dict:
    """计算预算使用进度"""
    # 解析周期
    year, month = map(int, budget.period.split('-'))
    
    # 计算该月的起止日期
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1
    
    start_date = datetime(year, month, 1)
    end_date = datetime(next_year, next_month, 1)
    
    # 查询该周期内该分类的支出总额
    spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == budget.user_id,
        Transaction.category_id == budget.category_id,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date < end_date
    ).scalar() or 0.0
    
    # 计算剩余和使用百分比
    remaining = budget.amount - spent
    percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
    
    return {
        "spent": float(spent),
        "remaining": float(remaining),
        "percentage": round(percentage, 2)
    }


@router.post("", response_model=BudgetResponse, status_code=201)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建预算"""
    # 验证金额
    if budget.amount <= 0:
        raise HTTPException(status_code=400, detail="预算金额必须大于0")
    
    # 验证周期格式
    if not validate_period(budget.period):
        raise HTTPException(status_code=400, detail="周期格式错误，应为 YYYY-MM")
    
    # 检查该用户在该周期和分类下是否已有预算
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget.category_id,
        Budget.period == budget.period
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="该分类在此周期已存在预算"
        )
    
    # 创建预算
    db_budget = Budget(
        user_id=current_user.id,
        category_id=budget.category_id,
        amount=budget.amount,
        period=budget.period
    )
    
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    
    # 计算使用进度
    usage = calculate_budget_usage(db, db_budget)
    
    return BudgetResponse(
        id=db_budget.id,
        user_id=db_budget.user_id,
        category_id=db_budget.category_id,
        amount=db_budget.amount,
        period=db_budget.period,
        created_at=db_budget.created_at,
        updated_at=db_budget.updated_at,
        **usage
    )


@router.get("", response_model=List[BudgetResponse])
def get_budgets(
    period: Optional[str] = Query(None, description="筛选周期 (YYYY-MM)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询当前用户预算列表"""
    # 验证周期格式
    if period and not validate_period(period):
        raise HTTPException(status_code=400, detail="周期格式错误，应为 YYYY-MM")
    
    # 构建查询
    query = db.query(Budget).filter(Budget.user_id == current_user.id)
    
    # 按周期筛选
    if period:
        query = query.filter(Budget.period == period)
    
    # 按周期降序排列
    budgets = query.order_by(Budget.period.desc()).all()
    
    # 计算每个预算的使用进度
    result = []
    for budget in budgets:
        usage = calculate_budget_usage(db, budget)
        result.append(BudgetResponse(
            id=budget.id,
            user_id=budget.user_id,
            category_id=budget.category_id,
            amount=budget.amount,
            period=budget.period,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
            **usage
        ))
    
    return result


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新预算"""
    # 查询预算
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not db_budget:
        raise HTTPException(status_code=404, detail="预算不存在")
    
    # 权限校验
    if db_budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此预算")
    
    # 验证金额
    if budget_update.amount is not None:
        if budget_update.amount <= 0:
            raise HTTPException(status_code=400, detail="预算金额必须大于0")
        db_budget.amount = budget_update.amount
    
    # 验证周期格式
    if budget_update.period is not None:
        if not validate_period(budget_update.period):
            raise HTTPException(status_code=400, detail="周期格式错误，应为 YYYY-MM")
        
        # 检查新周期是否与其他预算冲突
        if budget_update.period != db_budget.period:
            existing = db.query(Budget).filter(
                Budget.user_id == current_user.id,
                Budget.category_id == db_budget.category_id,
                Budget.period == budget_update.period,
                Budget.id != budget_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="该分类在此周期已存在预算"
                )
        
        db_budget.period = budget_update.period
    
    # 更新分类
    if budget_update.category_id is not None:
        # 检查新分类是否与其他预算冲突
        if budget_update.category_id != db_budget.category_id:
            existing = db.query(Budget).filter(
                Budget.user_id == current_user.id,
                Budget.category_id == budget_update.category_id,
                Budget.period == db_budget.period,
                Budget.id != budget_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="该分类在此周期已存在预算"
                )
        
        db_budget.category_id = budget_update.category_id
    
    db_budget.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_budget)
    
    # 计算使用进度
    usage = calculate_budget_usage(db, db_budget)
    
    return BudgetResponse(
        id=db_budget.id,
        user_id=db_budget.user_id,
        category_id=db_budget.category_id,
        amount=db_budget.amount,
        period=db_budget.period,
        created_at=db_budget.created_at,
        updated_at=db_budget.updated_at,
        **usage
    )


@router.delete("/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除预算"""
    # 查询预算
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    
    if not db_budget:
        raise HTTPException(status_code=404, detail="预算不存在")
    
    # 权限校验
    if db_budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此预算")
    
    db.delete(db_budget)
    db.commit()
    
    return None


# 需要在导入部分添加 func
from sqlalchemy import func
