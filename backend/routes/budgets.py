"""Budget management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import aiosqlite
import logging

from backend.models.budget import (
    CreateBudgetRequest,
    UpdateBudgetRequest,
    BudgetResponse,
    BudgetWithUsage
)
from backend.dependencies import get_db, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    req: CreateBudgetRequest,
    db: aiosqlite.Connection = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Create a new budget for the current user.
    
    Args:
        req: Budget creation request
        db: Database connection
        user_id: Current user ID from auth token
        
    Returns:
        Created budget data
        
    Raises:
        HTTPException: 400 if budget already exists for this user/category/period
    """
    # Check if budget already exists for this user/category/period
    cursor = await db.execute(
        """
        SELECT id FROM budgets 
        WHERE user_id = ? AND period = ? AND 
        (category_id = ? OR (category_id IS NULL AND ? IS NULL))
        """,
        (user_id, req.period, req.category_id, req.category_id)
    )
    existing = await cursor.fetchone()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Budget already exists for period {req.period} and category {req.category_id}"
        )
    
    # Insert new budget
    cursor = await db.execute(
        """
        INSERT INTO budgets (user_id, category_id, amount, period)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, req.category_id, req.amount, req.period)
    )
    await db.commit()
    budget_id = cursor.lastrowid
    
    # Fetch created budget
    cursor = await db.execute(
        "SELECT * FROM budgets WHERE id = ?",
        (budget_id,)
    )
    row = await cursor.fetchone()
    
    return BudgetResponse(
        id=row[0],
        user_id=row[1],
        category_id=row[2],
        amount=row[3],
        period=row[4],
        created_at=row[5],
        updated_at=row[6]
    )


@router.get("", response_model=List[BudgetWithUsage])
async def list_budgets(
    period: Optional[str] = None,
    category_id: Optional[int] = None,
    db: aiosqlite.Connection = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    List all budgets for the current user with spending information.
    
    Args:
        period: Filter by period (YYYY-MM format)
        category_id: Filter by category ID
        db: Database connection
        user_id: Current user ID from auth token
        
    Returns:
        List of budgets with usage statistics
    """
    # Build query with optional filters
    query = """
        SELECT 
            b.id, b.user_id, b.category_id, b.amount, b.period, 
            b.created_at, b.updated_at,
            COALESCE(SUM(t.amount), 0) as spent
        FROM budgets b
        LEFT JOIN transactions t ON 
            t.user_id = b.user_id AND
            strftime('%Y-%m', t.date) = b.period AND
            (b.category_id IS NULL OR t.category_id = b.category_id)
        WHERE b.user_id = ?
    """
    params = [user_id]
    
    if period:
        query += " AND b.period = ?"
        params.append(period)
    
    if category_id is not None:
        query += " AND b.category_id = ?"
        params.append(category_id)
    
    query += " GROUP BY b.id ORDER BY b.period DESC, b.category_id"
    
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    
    budgets = []
    for row in rows:
        spent = row[7]
        amount = row[3]
        remaining = max(0, amount - spent)
        percentage = (spent / amount * 100) if amount > 0 else 0
        
        budgets.append(BudgetWithUsage(
            id=row[0],
            user_id=row[1],
            category_id=row[2],
            amount=amount,
            period=row[4],
            created_at=row[5],
            updated_at=row[6],
            spent=spent,
            remaining=remaining,
            percentage_used=round(percentage, 2)
        ))
    
    return budgets


@router.get("/{budget_id}", response_model=BudgetWithUsage)
async def get_budget(
    budget_id: int,
    db: aiosqlite.Connection = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Get a specific budget by ID with spending information.
    
    Args:
        budget_id: Budget ID
        db: Database connection
        user_id: Current user ID from auth token
        
    Returns:
        Budget data with usage statistics
        
    Raises:
        HTTPException: 404 if budget not found or doesn't belong to user
    """
    cursor = await db.execute(
        """
        SELECT 
            b.id, b.user_id, b.category_id, b.amount, b.period, 
            b.created_at, b.updated_at,
            COALESCE(SUM(t.amount), 0) as spent
        FROM budgets b
        LEFT JOIN transactions t ON 
            t.user_id = b.user_id AND
            strftime('%Y-%m', t.date) = b.period AND
            (b.category_id IS NULL OR t.category_id = b.category_id)
        WHERE b.id = ? AND b.user_id = ?
        GROUP BY b.id
        """,
        (budget_id, user_id)
    )
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found"
        )
    
    spent = row[7]
    amount = row[3]
    remaining = max(0, amount - spent)
    percentage = (spent / amount * 100) if amount > 0 else 0
    
    return BudgetWithUsage(
        id=row[0],
        user_id=row[1],
        category_id=row[2],
        amount=amount,
        period=row[4],
        created_at=row[5],
        updated_at=row[6],
        spent=spent,
        remaining=remaining,
        percentage_used=round(percentage, 2)
    )


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    req: UpdateBudgetRequest,
    db: aiosqlite.Connection = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Update an existing budget.
    
    Args:
        budget_id: Budget ID
        req: Budget update request
        db: Database connection
        user_id: Current user ID from auth token
        
    Returns:
        Updated budget data
        
    Raises:
        HTTPException: 404 if budget not found, 400 if update conflicts with existing budget
    """
    # Check budget exists and belongs to user
    cursor = await db.execute(
        "SELECT id FROM budgets WHERE id = ? AND user_id = ?",
        (budget_id, user_id)
    )
    if not await cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found"
        )
    
    # Build update query dynamically
    updates = []
    params = []
    
    if req.amount is not None:
        updates.append("amount = ?")
        params.append(req.amount)
    
    if req.category_id is not None:
        updates.append("category_id = ?")
        params.append(req.category_id)
    
    if req.period is not None:
        updates.append("period = ?")
        params.append(req.period)
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    params.extend([budget_id, user_id])
    
    await db.execute(
        f"UPDATE budgets SET {', '.join(updates)} WHERE id = ? AND user_id = ?",
        params
    )
    await db.commit()
    
    # Fetch updated budget
    cursor = await db.execute(
        "SELECT * FROM budgets WHERE id = ?",
        (budget_id,)
    )
    row = await cursor.fetchone()
    
    return BudgetResponse(
        id=row[0],
        user_id=row[1],
        category_id=row[2],
        amount=row[3],
        period=row[4],
        created_at=row[5],
        updated_at=row[6]
    )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    db: aiosqlite.Connection = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Delete a budget.
    
    Args:
        budget_id: Budget ID
        db: Database connection
        user_id: Current user ID from auth token
        
    Raises:
        HTTPException: 404 if budget not found
    """
    cursor = await db.execute(
        "DELETE FROM budgets WHERE id = ? AND user_id = ?",
        (budget_id, user_id)
    )
    await db.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget {budget_id} not found"
        )
