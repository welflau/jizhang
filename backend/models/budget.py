"""Budget data models and schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BudgetBase(BaseModel):
    """Base budget schema with common fields."""
    category_id: Optional[int] = Field(None, description="Category ID (null for overall budget)")
    amount: float = Field(ge=0, description="Budget amount (must be non-negative)")
    period: str = Field(
        pattern=r"^\d{4}-\d{2}$",
        description="Budget period in YYYY-MM format",
        examples=["2024-01", "2024-12"]
    )


class CreateBudgetRequest(BudgetBase):
    """Request schema for creating a new budget."""
    pass


class UpdateBudgetRequest(BaseModel):
    """Request schema for updating an existing budget."""
    category_id: Optional[int] = Field(None, description="Category ID (null for overall budget)")
    amount: Optional[float] = Field(None, ge=0, description="Budget amount")
    period: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Budget period in YYYY-MM format"
    )


class BudgetResponse(BudgetBase):
    """Response schema for budget data."""
    id: int
    user_id: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class BudgetWithUsage(BudgetResponse):
    """Budget response with spending information."""
    spent: float = Field(description="Amount spent in this budget period")
    remaining: float = Field(description="Remaining budget amount")
    percentage_used: float = Field(description="Percentage of budget used (0-100)")
