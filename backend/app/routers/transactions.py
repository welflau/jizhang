from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from ..database import get_db
from ..models.transaction import Transaction, TransactionType
from ..auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


class TransactionTypeEnum(str, Enum):
    income = "income"
    expense = "expense"


class TransactionCreate(BaseModel):
    type: TransactionTypeEnum
    amount: float = Field(..., gt=0, description="Transaction amount must be positive")
    category_id: int
    date: date
    note: Optional[str] = Field(None, max_length=500)
    payment_method: Optional[str] = Field(None, max_length=50)

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)


class TransactionUpdate(BaseModel):
    type: Optional[TransactionTypeEnum] = None
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    date: Optional[date] = None
    note: Optional[str] = Field(None, max_length=500)
    payment_method: Optional[str] = Field(None, max_length=50)

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        if v is not None:
            return round(v, 2)
        return v


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    type: str
    amount: float
    category_id: int
    date: date
    note: Optional[str]
    payment_method: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    transactions: List[TransactionResponse]


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new transaction for the current user
    """
    db_transaction = Transaction(
        user_id=current_user.id,
        type=transaction.type.value,
        amount=transaction.amount,
        category_id=transaction.category_id,
        date=transaction.date,
        note=transaction.note,
        payment_method=transaction.payment_method
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.get("/", response_model=TransactionListResponse)
def get_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[TransactionTypeEnum] = Query(None, description="Filter by transaction type"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of transactions for the current user with optional filters
    """
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    # Apply filters
    if type:
        query = query.filter(Transaction.type == type.value)
    
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    transactions = query.order_by(Transaction.date.desc(), Transaction.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        transactions=transactions
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific transaction by ID
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific transaction
    """
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update fields if provided
    update_data = transaction_update.dict(exclude_unset=True)
    
    if 'type' in update_data:
        update_data['type'] = update_data['type'].value
    
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    
    db_transaction.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific transaction
    """
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(db_transaction)
    db.commit()
    
    return None


@router.get("/stats/summary")
def get_transaction_summary(
    start_date: Optional[date] = Query(None, description="Summary from date"),
    end_date: Optional[date] = Query(None, description="Summary to date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get transaction summary statistics (total income, total expense, balance)
    """
    from sqlalchemy import func
    
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    # Calculate income
    total_income = query.filter(Transaction.type == TransactionType.INCOME.value)\
        .with_entities(func.sum(Transaction.amount)).scalar() or 0
    
    # Calculate expense
    total_expense = query.filter(Transaction.type == TransactionType.EXPENSE.value)\
        .with_entities(func.sum(Transaction.amount)).scalar() or 0
    
    balance = total_income - total_expense
    
    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(balance, 2),
        "start_date": start_date,
        "end_date": end_date
    }


@router.get("/stats/by-category")
def get_transactions_by_category(
    type: TransactionTypeEnum = Query(..., description="Transaction type"),
    start_date: Optional[date] = Query(None, description="From date"),
    end_date: Optional[date] = Query(None, description="To date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get transaction statistics grouped by category
    """
    from sqlalchemy import func
    
    query = db.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('count')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == type.value
    )
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    results = query.group_by(Transaction.category_id).all()
    
    return [
        {
            "category_id": result.category_id,
            "total_amount": round(result.total_amount, 2),
            "count": result.count
        }
        for result in results
    ]


@router.get("/stats/by-payment-method")
def get_transactions_by_payment_method(
    start_date: Optional[date] = Query(None, description="From date"),
    end_date: Optional[date] = Query(None, description="To date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get transaction statistics grouped by payment method
    """
    from sqlalchemy import func
    
    query = db.query(
        Transaction.payment_method,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('count')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.payment_method.isnot(None)
    )
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    results = query.group_by(Transaction.payment_method).all()
    
    return [
        {
            "payment_method": result.payment_method,
            "total_amount": round(result.total_amount, 2),
            "count": result.count
        }
        for result in results
    ]