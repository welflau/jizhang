"""Budget data model and database operations.

Handles budget CRUD operations with SQLite async support.
"""

from typing import Optional, List
from datetime import datetime
import aiosqlite
from pydantic import BaseModel, Field, field_validator
import re


class BudgetCreate(BaseModel):
    """Schema for creating a new budget."""
    user_id: int = Field(gt=0, description="User ID who owns this budget")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID (null for total budget)")
    amount: float = Field(ge=0, description="Budget amount")
    period: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Budget period in YYYY-MM format")
    
    @field_validator('period')
    @classmethod
    def validate_period_format(cls, v: str) -> str:
        """Validate period format is YYYY-MM."""
        if not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', v):
            raise ValueError('Period must be in YYYY-MM format')
        return v


class BudgetUpdate(BaseModel):
    """Schema for updating an existing budget."""
    amount: Optional[float] = Field(None, ge=0, description="Budget amount")
    category_id: Optional[int] = Field(None, description="Category ID")


class BudgetResponse(BaseModel):
    """Schema for budget response."""
    id: int
    user_id: int
    category_id: Optional[int]
    amount: float
    period: str
    created_at: str
    updated_at: str


class BudgetDB:
    """Database operations for budgets."""
    
    @staticmethod
    async def create(db: aiosqlite.Connection, budget: BudgetCreate) -> int:
        """Create a new budget.
        
        Args:
            db: Database connection
            budget: Budget creation data
            
        Returns:
            Created budget ID
        """
        cursor = await db.execute(
            """
            INSERT INTO budgets (user_id, category_id, amount, period)
            VALUES (?, ?, ?, ?)
            """,
            (budget.user_id, budget.category_id, budget.amount, budget.period)
        )
        await db.commit()
        return cursor.lastrowid
    
    @staticmethod
    async def get_by_id(db: aiosqlite.Connection, budget_id: int) -> Optional[dict]:
        """Get budget by ID.
        
        Args:
            db: Database connection
            budget_id: Budget ID
            
        Returns:
            Budget data or None if not found
        """
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM budgets WHERE id = ?",
            (budget_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    async def get_by_user_and_period(
        db: aiosqlite.Connection,
        user_id: int,
        period: str
    ) -> List[dict]:
        """Get all budgets for a user in a specific period.
        
        Args:
            db: Database connection
            user_id: User ID
            period: Period in YYYY-MM format
            
        Returns:
            List of budget records
        """
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM budgets
            WHERE user_id = ? AND period = ?
            ORDER BY category_id NULLS FIRST
            """,
            (user_id, period)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    async def get_by_user(
        db: aiosqlite.Connection,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """Get all budgets for a user with pagination.
        
        Args:
            db: Database connection
            user_id: User ID
            limit: Maximum number of records
            offset: Number of records to skip
            
        Returns:
            List of budget records
        """
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM budgets
            WHERE user_id = ?
            ORDER BY period DESC, category_id NULLS FIRST
            LIMIT ? OFFSET ?
            """,
            (user_id, limit, offset)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    @staticmethod
    async def update(
        db: aiosqlite.Connection,
        budget_id: int,
        budget: BudgetUpdate
    ) -> bool:
        """Update budget.
        
        Args:
            db: Database connection
            budget_id: Budget ID
            budget: Budget update data
            
        Returns:
            True if updated, False if not found
        """
        update_fields = []
        params = []
        
        if budget.amount is not None:
            update_fields.append("amount = ?")
            params.append(budget.amount)
        
        if budget.category_id is not None:
            update_fields.append("category_id = ?")
            params.append(budget.category_id)
        
        if not update_fields:
            return True
        
        params.append(budget_id)
        cursor = await db.execute(
            f"UPDATE budgets SET {', '.join(update_fields)} WHERE id = ?",
            params
        )
        await db.commit()
        return cursor.rowcount > 0
    
    @staticmethod
    async def delete(db: aiosqlite.Connection, budget_id: int) -> bool:
        """Delete budget.
        
        Args:
            db: Database connection
            budget_id: Budget ID
            
        Returns:
            True if deleted, False if not found
        """
        cursor = await db.execute(
            "DELETE FROM budgets WHERE id = ?",
            (budget_id,)
        )
        await db.commit()
        return cursor.rowcount > 0
    
    @staticmethod
    async def check_exists(
        db: aiosqlite.Connection,
        user_id: int,
        period: str,
        category_id: Optional[int] = None
    ) -> bool:
        """Check if budget already exists for user/period/category.
        
        Args:
            db: Database connection
            user_id: User ID
            period: Period in YYYY-MM format
            category_id: Category ID (None for total budget)
            
        Returns:
            True if exists, False otherwise
        """
        if category_id is None:
            cursor = await db.execute(
                "SELECT 1 FROM budgets WHERE user_id = ? AND period = ? AND category_id IS NULL",
                (user_id, period)
            )
        else:
            cursor = await db.execute(
                "SELECT 1 FROM budgets WHERE user_id = ? AND period = ? AND category_id = ?",
                (user_id, period, category_id)
            )
        row = await cursor.fetchone()
        return row is not None
