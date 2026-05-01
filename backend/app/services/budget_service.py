from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.schemas.budget import BudgetCreate, BudgetUpdate
from fastapi import HTTPException, status


class BudgetService:
    """预算管理服务"""

    @staticmethod
    def create_budget(db: Session, budget_data: BudgetCreate, user_id: int) -> Budget:
        """
        创建预算
        
        Args:
            db: 数据库会话
            budget_data: 预算创建数据
            user_id: 用户ID
            
        Returns:
            Budget: 创建的预算对象
            
        Raises:
            HTTPException: 参数校验失败或创建失败
        """
        # 参数校验
        if budget_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="预算金额必须大于0"
            )
        
        # 校验 period 格式 (YYYY-MM)
        if not BudgetService._validate_period_format(budget_data.period):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="period 格式错误，应为 YYYY-MM 格式"
            )
        
        # 检查是否已存在相同分类和周期的预算
        existing_budget = db.query(Budget).filter(
            and_(
                Budget.user_id == user_id,
                Budget.category_id == budget_data.category_id,
                Budget.period == budget_data.period
            )
        ).first()
        
        if existing_budget:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该分类在此周期已存在预算"
            )
        
        # 创建预算
        new_budget = Budget(
            user_id=user_id,
            category_id=budget_data.category_id,
            amount=budget_data.amount,
            period=budget_data.period
        )
        
        db.add(new_budget)
        db.commit()
        db.refresh(new_budget)
        
        return new_budget

    @staticmethod
    def get_budgets(
        db: Session, 
        user_id: int, 
        period: Optional[str] = None
    ) -> List[Budget]:
        """
        查询用户预算列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            period: 可选的周期筛选 (YYYY-MM)
            
        Returns:
            List[Budget]: 预算列表
        """
        query = db.query(Budget).filter(Budget.user_id == user_id)
        
        # 按 period 筛选
        if period:
            if not BudgetService._validate_period_format(period):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="period 格式错误，应为 YYYY-MM 格式"
                )
            query = query.filter(Budget.period == period)
        
        budgets = query.all()
        
        # 计算每个预算的使用进度
        for budget in budgets:
            budget.spent = BudgetService._calculate_spent(db, budget)
            budget.remaining = budget.amount - budget.spent
            budget.percentage = (budget.spent / budget.amount * 100) if budget.amount > 0 else 0
        
        return budgets

    @staticmethod
    def get_budget_by_id(db: Session, budget_id: int, user_id: int) -> Budget:
        """
        根据ID获取预算
        
        Args:
            db: 数据库会话
            budget_id: 预算ID
            user_id: 用户ID
            
        Returns:
            Budget: 预算对象
            
        Raises:
            HTTPException: 预算不存在或无权限访问
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预算不存在"
            )
        
        # 权限校验：仅能访问自己的预算
        if budget.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此预算"
            )
        
        # 计算使用进度
        budget.spent = BudgetService._calculate_spent(db, budget)
        budget.remaining = budget.amount - budget.spent
        budget.percentage = (budget.spent / budget.amount * 100) if budget.amount > 0 else 0
        
        return budget

    @staticmethod
    def update_budget(
        db: Session, 
        budget_id: int, 
        budget_data: BudgetUpdate, 
        user_id: int
    ) -> Budget:
        """
        更新预算
        
        Args:
            db: 数据库会话
            budget_id: 预算ID
            budget_data: 预算更新数据
            user_id: 用户ID
            
        Returns:
            Budget: 更新后的预算对象
            
        Raises:
            HTTPException: 预算不存在、无权限或参数校验失败
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预算不存在"
            )
        
        # 权限校验：仅能更新自己的预算
        if budget.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此预算"
            )
        
        # 参数校验
        if budget_data.amount is not None and budget_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="预算金额必须大于0"
            )
        
        if budget_data.period is not None:
            if not BudgetService._validate_period_format(budget_data.period):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="period 格式错误，应为 YYYY-MM 格式"
                )
            
            # 检查是否与其他预算冲突
            existing_budget = db.query(Budget).filter(
                and_(
                    Budget.user_id == user_id,
                    Budget.category_id == budget_data.category_id if budget_data.category_id else budget.category_id,
                    Budget.period == budget_data.period,
                    Budget.id != budget_id
                )
            ).first()
            
            if existing_budget:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该分类在此周期已存在预算"
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
        budget.spent = BudgetService._calculate_spent(db, budget)
        budget.remaining = budget.amount - budget.spent
        budget.percentage = (budget.spent / budget.amount * 100) if budget.amount > 0 else 0
        
        return budget

    @staticmethod
    def delete_budget(db: Session, budget_id: int, user_id: int) -> None:
        """
        删除预算
        
        Args:
            db: 数据库会话
            budget_id: 预算ID
            user_id: 用户ID
            
        Raises:
            HTTPException: 预算不存在或无权限删除
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预算不存在"
            )
        
        # 权限校验：仅能删除自己的预算
        if budget.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此预算"
            )
        
        db.delete(budget)
        db.commit()

    @staticmethod
    def _validate_period_format(period: str) -> bool:
        """
        校验 period 格式是否为 YYYY-MM
        
        Args:
            period: 周期字符串
            
        Returns:
            bool: 格式是否正确
        """
        try:
            datetime.strptime(period, "%Y-%m")
            return True
        except ValueError:
            return False

    @staticmethod
    def _calculate_spent(db: Session, budget: Budget) -> float:
        """
        计算预算已使用金额
        
        Args:
            db: 数据库会话
            budget: 预算对象
            
        Returns:
            float: 已使用金额
        """
        # 解析 period (YYYY-MM)
        try:
            year, month = map(int, budget.period.split('-'))
        except ValueError:
            return 0.0
        
        # 查询该周期内该分类的所有支出交易
        spent = db.query(Transaction).filter(
            and_(
                Transaction.user_id == budget.user_id,
                Transaction.category_id == budget.category_id,
                Transaction.type == 'expense',
                extract('year', Transaction.date) == year,
                extract('month', Transaction.date) == month
            )
        ).with_entities(Transaction.amount).all()
        
        # 计算总支出
        total_spent = sum([amount[0] for amount in spent]) if spent else 0.0
        
        return total_spent

    @staticmethod
    def get_budget_summary(db: Session, user_id: int, period: str) -> dict:
        """
        获取预算汇总信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            period: 周期 (YYYY-MM)
            
        Returns:
            dict: 预算汇总信息
        """
        if not BudgetService._validate_period_format(period):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="period 格式错误，应为 YYYY-MM 格式"
            )
        
        budgets = BudgetService.get_budgets(db, user_id, period)
        
        total_budget = sum([b.amount for b in budgets])
        total_spent = sum([b.spent for b in budgets])
        total_remaining = total_budget - total_spent
        overall_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        return {
            "period": period,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_remaining": total_remaining,
            "overall_percentage": overall_percentage,
            "budget_count": len(budgets),
            "budgets": budgets
        }