from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.bill import Bill
from app.models.category import Category
from app.auth import get_current_user

router = APIRouter(prefix="/bills", tags=["bills"])


# Request/Response Schemas
class BillCreate(BaseModel):
    type: str = Field(..., description="账单类型: income 或 expense")
    amount: float = Field(..., gt=0, description="金额，必须大于0")
    category_id: int = Field(..., description="分类ID")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    date: datetime = Field(..., description="账单日期")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "expense",
                "amount": 50.00,
                "category_id": 1,
                "description": "午餐",
                "date": "2024-01-15T12:00:00"
            }
        }


class BillUpdate(BaseModel):
    type: Optional[str] = Field(None, description="账单类型: income 或 expense")
    amount: Optional[float] = Field(None, gt=0, description="金额，必须大于0")
    category_id: Optional[int] = Field(None, description="分类ID")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    date: Optional[datetime] = Field(None, description="账单日期")


class BillResponse(BaseModel):
    id: int
    type: str
    amount: float
    category_id: int
    category_name: str
    description: Optional[str]
    date: datetime
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillQueryParams(BaseModel):
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    type: Optional[str] = Field(None, description="账单类型: income 或 expense")
    category_ids: Optional[List[int]] = Field(None, description="分类ID列表")
    min_amount: Optional[float] = Field(None, ge=0, description="最小金额")
    max_amount: Optional[float] = Field(None, ge=0, description="最大金额")
    keyword: Optional[str] = Field(None, max_length=100, description="关键词搜索（描述）")
    sort_by: Optional[str] = Field("date", description="排序字段: date, amount, created_at")
    sort_order: Optional[str] = Field("desc", description="排序方式: asc 或 desc")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class BillListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[BillResponse]
    summary: dict = Field(description="统计摘要")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "items": [],
                "summary": {
                    "total_income": 5000.00,
                    "total_expense": 3000.00,
                    "balance": 2000.00
                }
            }
        }


class BillStatistics(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    income_count: int
    expense_count: int
    avg_income: float
    avg_expense: float


# Helper Functions
def build_query_filters(params: BillQueryParams, user_id: int):
    """构建查询过滤条件"""
    filters = [Bill.user_id == user_id]

    if params.start_date:
        filters.append(Bill.date >= params.start_date)
    
    if params.end_date:
        filters.append(Bill.date <= params.end_date)
    
    if params.type:
        if params.type not in ["income", "expense"]:
            raise HTTPException(status_code=400, detail="类型必须是 income 或 expense")
        filters.append(Bill.type == params.type)
    
    if params.category_ids:
        filters.append(Bill.category_id.in_(params.category_ids))
    
    if params.min_amount is not None:
        filters.append(Bill.amount >= params.min_amount)
    
    if params.max_amount is not None:
        filters.append(Bill.amount <= params.max_amount)
    
    if params.keyword:
        filters.append(Bill.description.ilike(f"%{params.keyword}%"))
    
    return filters


def get_sort_column(sort_by: str):
    """获取排序字段"""
    sort_columns = {
        "date": Bill.date,
        "amount": Bill.amount,
        "created_at": Bill.created_at
    }
    return sort_columns.get(sort_by, Bill.date)


# API Endpoints
@router.post("", response_model=BillResponse, status_code=201)
def create_bill(
    bill_data: BillCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建账单"""
    # 验证类型
    if bill_data.type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="类型必须是 income 或 expense")
    
    # 验证分类是否存在且属于当前用户
    category = db.query(Category).filter(
        Category.id == bill_data.category_id,
        Category.user_id == current_user["id"]
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 验证分类类型与账单类型是否匹配
    if category.type != bill_data.type:
        raise HTTPException(status_code=400, detail="分类类型与账单类型不匹配")
    
    # 创建账单
    bill = Bill(
        type=bill_data.type,
        amount=bill_data.amount,
        category_id=bill_data.category_id,
        description=bill_data.description,
        date=bill_data.date,
        user_id=current_user["id"]
    )
    
    db.add(bill)
    db.commit()
    db.refresh(bill)
    
    # 构造响应
    response = BillResponse(
        id=bill.id,
        type=bill.type,
        amount=bill.amount,
        category_id=bill.category_id,
        category_name=category.name,
        description=bill.description,
        date=bill.date,
        user_id=bill.user_id,
        created_at=bill.created_at,
        updated_at=bill.updated_at
    )
    
    return response


@router.get("", response_model=BillListResponse)
def query_bills(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    type: Optional[str] = Query(None, description="账单类型"),
    category_ids: Optional[str] = Query(None, description="分类ID列表，逗号分隔"),
    min_amount: Optional[float] = Query(None, ge=0, description="最小金额"),
    max_amount: Optional[float] = Query(None, ge=0, description="最大金额"),
    keyword: Optional[str] = Query(None, max_length=100, description="关键词"),
    sort_by: str = Query("date", description="排序字段"),
    sort_order: str = Query("desc", description="排序方式"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """查询账单列表（支持多条件组合查询）"""
    # 解析分类ID列表
    category_id_list = None
    if category_ids:
        try:
            category_id_list = [int(cid.strip()) for cid in category_ids.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="分类ID格式错误")
    
    # 构建查询参数
    params = BillQueryParams(
        start_date=start_date,
        end_date=end_date,
        type=type,
        category_ids=category_id_list,
        min_amount=min_amount,
        max_amount=max_amount,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    # 构建查询过滤条件
    filters = build_query_filters(params, current_user["id"])
    
    # 基础查询
    query = db.query(Bill).filter(and_(*filters))
    
    # 计算统计数据
    summary_query = db.query(Bill).filter(and_(*filters))
    total_income = sum(b.amount for b in summary_query.all() if b.type == "income")
    total_expense = sum(b.amount for b in summary_query.all() if b.type == "expense")
    
    # 总数
    total = query.count()
    
    # 排序
    sort_column = get_sort_column(params.sort_by)
    if params.sort_order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # 分页
    offset = (params.page - 1) * params.page_size
    bills = query.offset(offset).limit(params.page_size).all()
    
    # 获取分类信息
    category_map = {}
    if bills:
        category_ids_in_bills = list(set(b.category_id for b in bills))
        categories = db.query(Category).filter(Category.id.in_(category_ids_in_bills)).all()
        category_map = {c.id: c.name for c in categories}
    
    # 构造响应
    items = [
        BillResponse(
            id=bill.id,
            type=bill.type,
            amount=bill.amount,
            category_id=bill.category_id,
            category_name=category_map.get(bill.category_id, "未知分类"),
            description=bill.description,
            date=bill.date,
            user_id=bill.user_id,
            created_at=bill.created_at,
            updated_at=bill.updated_at
        )
        for bill in bills
    ]
    
    total_pages = (total + params.page_size - 1) // params.page_size
    
    return BillListResponse(
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
        items=items,
        summary={
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "balance": round(total_income - total_expense, 2)
        }
    )


@router.get("/statistics", response_model=BillStatistics)
def get_bill_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取账单统计信息"""
    filters = [Bill.user_id == current_user["id"]]
    
    if start_date:
        filters.append(Bill.date >= start_date)
    if end_date:
        filters.append(Bill.date <= end_date)
    
    bills = db.query(Bill).filter(and_(*filters)).all()
    
    income_bills = [b for b in bills if b.type == "income"]
    expense_bills = [b for b in bills if b.type == "expense"]
    
    total_income = sum(b.amount for b in income_bills)
    total_expense = sum(b.amount for b in expense_bills)
    income_count = len(income_bills)
    expense_count = len(expense_bills)
    
    return BillStatistics(
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        balance=round(total_income - total_expense, 2),
        income_count=income_count,
        expense_count=expense_count,
        avg_income=round(total_income / income_count, 2) if income_count > 0 else 0,
        avg_expense=round(total_expense / expense_count, 2) if expense_count > 0 else 0
    )


@router.get("/{bill_id}", response_model=BillResponse)
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取单个账单详情"""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user["id"]
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    category = db.query(Category).filter(Category.id == bill.category_id).first()
    
    return BillResponse(
        id=bill.id,
        type=bill.type,
        amount=bill.amount,
        category_id=bill.category_id,
        category_name=category.name if category else "未知分类",
        description=bill.description,
        date=bill.date,
        user_id=bill.user_id,
        created_at=bill.created_at,
        updated_at=bill.updated_at
    )


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    bill_data: BillUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新账单"""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user["id"]
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    # 验证类型
    if bill_data.type and bill_data.type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="类型必须是 income 或 expense")
    
    # 验证分类
    if bill_data.category_id:
        category = db.query(Category).filter(
            Category.id == bill_data.category_id,
            Category.user_id == current_user["id"]
        ).first()
        
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
        
        # 验证分类类型
        bill_type = bill_data.type if bill_data.type else bill.type
        if category.type != bill_type:
            raise HTTPException(status_code=400, detail="分类类型与账单类型不匹配")
    
    # 更新字段
    update_data = bill_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bill, field, value)
    
    bill.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(bill)
    
    category = db.query(Category).filter(Category.id == bill.category_id).first()
    
    return BillResponse(
        id=bill.id,
        type=bill.type,
        amount=bill.amount,
        category_id=bill.category_id,
        category_name=category.name if category else "未知分类",
        description=bill.description,
        date=bill.date,
        user_id=bill.user_id,
        created_at=bill.created_at,
        updated_at=bill.updated_at
    )


@router.delete("/{bill_id}", status_code=204)
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除账单"""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.user_id == current_user["id"]
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    db.delete(bill)
    db.commit()
    
    return None