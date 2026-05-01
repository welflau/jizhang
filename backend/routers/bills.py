from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import aiosqlite
from decimal import Decimal
import logging
from datetime import datetime

from backend.schemas.bill import (
    BillQueryRequest,
    BillQueryResponse,
    BillItem,
    BillStatistics
)
from backend.database.connection import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bills", tags=["bills"])


@router.get("/query", response_model=BillQueryResponse)
async def query_bills(
    start_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    category: Optional[str] = Query(None, max_length=50),
    bill_type: Optional[str] = Query(None, regex="^(income|expense)$"),
    min_amount: Optional[Decimal] = Query(None, ge=0),
    max_amount: Optional[Decimal] = Query(None, ge=0),
    keyword: Optional[str] = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("date", regex="^(date|amount|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Query bills with multiple filter conditions.
    
    Supports:
    - Time range filtering (start_date, end_date)
    - Category filtering
    - Type filtering (income/expense)
    - Amount range filtering
    - Keyword search in description
    - Pagination
    - Sorting
    """
    try:
        # Build WHERE clause dynamically
        where_conditions = []
        params = []
        
        if start_date:
            where_conditions.append("date >= ?")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("date <= ?")
            params.append(end_date)
        
        if category:
            where_conditions.append("category = ?")
            params.append(category)
        
        if bill_type:
            where_conditions.append("bill_type = ?")
            params.append(bill_type)
        
        if min_amount is not None:
            where_conditions.append("amount >= ?")
            params.append(float(min_amount))
        
        if max_amount is not None:
            where_conditions.append("amount <= ?")
            params.append(float(max_amount))
        
        if keyword:
            where_conditions.append("description LIKE ?")
            params.append(f"%{keyword}%")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Count total matching records
        count_query = f"SELECT COUNT(*) FROM bills WHERE {where_clause}"
        async with db.execute(count_query, params) as cursor:
            row = await cursor.fetchone()
            total = row[0] if row else 0
        
        # Calculate pagination
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size
        
        # Build ORDER BY clause
        order_column = sort_by
        order_direction = sort_order.upper()
        
        # Query bills with pagination
        query = f"""
            SELECT id, bill_type, category, amount, date, description, 
                   created_at, updated_at
            FROM bills
            WHERE {where_clause}
            ORDER BY {order_column} {order_direction}
            LIMIT ? OFFSET ?
        """
        
        query_params = params + [page_size, offset]
        
        async with db.execute(query, query_params) as cursor:
            rows = await cursor.fetchall()
        
        # Convert rows to BillItem objects
        items = [
            BillItem(
                id=row[0],
                bill_type=row[1],
                category=row[2],
                amount=Decimal(str(row[3])),
                date=row[4],
                description=row[5],
                created_at=row[6],
                updated_at=row[7]
            )
            for row in rows
        ]
        
        return BillQueryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    
    except Exception as e:
        logger.exception("Error querying bills: %s", e)
        raise HTTPException(status_code=500, detail="Failed to query bills")


@router.get("/statistics", response_model=BillStatistics)
async def get_bill_statistics(
    start_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    category: Optional[str] = Query(None, max_length=50),
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Get bill statistics for the given filters.
    
    Returns total income, total expense, net amount, and count.
    """
    try:
        where_conditions = []
        params = []
        
        if start_date:
            where_conditions.append("date >= ?")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("date <= ?")
            params.append(end_date)
        
        if category:
            where_conditions.append("category = ?")
            params.append(category)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT 
                COALESCE(SUM(CASE WHEN bill_type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN bill_type = 'expense' THEN amount ELSE 0 END), 0) as total_expense,
                COUNT(*) as count
            FROM bills
            WHERE {where_clause}
        """
        
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
        
        if not row:
            return BillStatistics(
                total_income=Decimal("0"),
                total_expense=Decimal("0"),
                net_amount=Decimal("0"),
                count=0
            )
        
        total_income = Decimal(str(row[0]))
        total_expense = Decimal(str(row[1]))
        count = row[2]
        
        return BillStatistics(
            total_income=total_income,
            total_expense=total_expense,
            net_amount=total_income - total_expense,
            count=count
        )
    
    except Exception as e:
        logger.exception("Error calculating statistics: %s", e)
        raise HTTPException(status_code=500, detail="Failed to calculate statistics")
