from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, func, Index
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..database import get_db
from ..models import Bill, User
from ..auth import get_current_user

router = APIRouter(prefix="/bills", tags=["bills"])


# Request/Response Schemas
class BillBase(BaseModel):
    amount: float = Field(..., description="金额")
    category: str = Field(..., description="分类")
    type: str = Field(..., description="类型：income/expense")
    description: Optional[str] = Field(None, description="描述")
    date: datetime = Field(..., description="账单日期")


class BillCreate(BillBase):
    pass


class BillUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None


class BillResponse(BillBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillQueryParams(BaseModel):
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    category: Optional[str] = Field(None, description="分类筛选")
    type: Optional[str] = Field(None, description="类型筛选：income/expense")
    min_amount: Optional[float] = Field(None, description="最小金额")
    max_amount: Optional[float] = Field(None, description="最大金额")
    keyword: Optional[str] = Field(None, description="关键词搜索（描述）")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    sort_by: str = Field("date", description="排序字段：date/amount/created_at")
    sort_order: str = Field("desc", description="排序方式：asc/desc")


class BillListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[BillResponse]


class BillStatistics(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    category_stats: dict


# Database Indexes (to be added in models.py)
"""
在 models.py 的 Bill 模型中添加以下索引：

__table_args__ = (
    Index('idx_bill_user_date', 'user_id', 'date'),
    Index('idx_bill_user_category', 'user_id', 'category'),
    Index('idx_bill_user_type', 'user_id', 'type'),
    Index('idx_bill_user_amount', 'user_id', 'amount'),
    Index('idx_bill_user_created', 'user_id', 'created_at'),
    Index('idx_bill_date_type', 'date', 'type'),
)
"""


# API Endpoints
@router.post("/", response_model=BillResponse, status_code=201)
def create_bill(
    bill: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建账单"""
    if bill.type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="类型必须是 income 或 expense")
    
    if bill.amount <= 0:
        raise HTTPException(status_code=400, detail="金额必须大于0")
    
    db_bill = Bill(
        user_id=current_user.id,
        amount=bill.amount,
        category=bill.category,
        type=bill.type,
        description=bill.description,
        date=bill.date
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.get("/", response_model=BillListResponse)
def query_bills(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    category: Optional[str] = Query(None, description="分类筛选"),
    type: Optional[str] = Query(None, description="类型筛选"),
    min_amount: Optional[float] = Query(None, description="最小金额"),
    max_amount: Optional[float] = Query(None, description="最大金额"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("date", description="排序字段"),
    sort_order: str = Query("desc", description="排序方式"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询账单列表（支持多条件组合）"""
    # 构建查询条件
    conditions = [Bill.user_id == current_user.id]
    
    # 时间范围
    if start_date:
        conditions.append(Bill.date >= start_date)
    if end_date:
        conditions.append(Bill.date <= end_date)
    
    # 分类筛选
    if category:
        conditions.append(Bill.category == category)
    
    # 类型筛选
    if type:
        if type not in ["income", "expense"]:
            raise HTTPException(status_code=400, detail="类型必须是 income 或 expense")
        conditions.append(Bill.type == type)
    
    # 金额范围
    if min_amount is not None:
        conditions.append(Bill.amount >= min_amount)
    if max_amount is not None:
        conditions.append(Bill.amount <= max_amount)
    
    # 关键词搜索
    if keyword:
        conditions.append(Bill.description.ilike(f"%{keyword}%"))
    
    # 构建查询
    query = db.query(Bill).filter(and_(*conditions))
    
    # 总数统计
    total = query.count()
    
    # 排序
    sort_field = getattr(Bill, sort_by, Bill.date)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())
    
    # 分页
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/statistics", response_model=BillStatistics)
def get_bill_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取账单统计信息"""
    # 构建查询条件
    conditions = [Bill.user_id == current_user.id]
    
    if start_date:
        conditions.append(Bill.date >= start_date)
    if end_date:
        conditions.append(Bill.date <= end_date)
    
    # 总收入
    total_income = db.query(func.sum(Bill.amount)).filter(
        and_(*conditions, Bill.type == "income")
    ).scalar() or 0.0
    
    # 总支出
    total_expense = db.query(func.sum(Bill.amount)).filter(
        and_(*conditions, Bill.type == "expense")
    ).scalar() or 0.0
    
    # 分类统计
    category_stats_query = db.query(
        Bill.category,
        Bill.type,
        func.sum(Bill.amount).label("total")
    ).filter(and_(*conditions)).group_by(Bill.category, Bill.type).all()
    
    category_stats = {}
    for category, bill_type, total in category_stats_query:
        if category not in category_stats:
            category_stats[category] = {"income": 0.0, "expense": 0.0}
        category_stats[category][bill_type] = float(total)
    
    return {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "balance": float(total_income - total_expense),
        "category_stats": category_stats
    }


@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个账单详情"""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    return bill


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill_update: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新账单"""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    # 更新字段
    update_data = bill_update.dict(exclude_unset=True)
    
    if "type" in update_data and update_data["type"] not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="类型必须是 income 或 expense")
    
    if "amount" in update_data and update_data["amount"] <= 0:
        raise HTTPException(status_code=400, detail="金额必须大于0")
    
    for field, value in update_data.items():
        setattr(bill, field, value)
    
    bill.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bill)
    return bill


@router.delete("/{bill_id}", status_code=204)
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除账单"""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user.id
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    db.delete(bill)
    db.commit()
    return None


@router.get("/categories/list", response_model=List[str])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户所有账单分类"""
    categories = db.query(Bill.category).filter(
        Bill.user_id == current_user.id
    ).distinct().all()
    
    return [category[0] for category in categories if category[0]]
