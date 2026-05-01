from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


class BillQueryRequest(BaseModel):
    """Bill query request with multiple filter conditions."""
    
    start_date: Optional[str] = Field(
        None,
        description="Start date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    end_date: Optional[str] = Field(
        None,
        description="End date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    category: Optional[str] = Field(
        None,
        description="Bill category filter",
        max_length=50
    )
    bill_type: Optional[Literal["income", "expense"]] = Field(
        None,
        description="Bill type: income or expense"
    )
    min_amount: Optional[Decimal] = Field(
        None,
        description="Minimum amount filter",
        ge=0
    )
    max_amount: Optional[Decimal] = Field(
        None,
        description="Maximum amount filter",
        ge=0
    )
    keyword: Optional[str] = Field(
        None,
        description="Keyword search in description",
        max_length=100
    )
    page: int = Field(
        1,
        description="Page number for pagination",
        ge=1
    )
    page_size: int = Field(
        20,
        description="Items per page",
        ge=1,
        le=100
    )
    sort_by: Literal["date", "amount", "created_at"] = Field(
        "date",
        description="Sort field"
    )
    sort_order: Literal["asc", "desc"] = Field(
        "desc",
        description="Sort order"
    )


class BillItem(BaseModel):
    """Single bill item in response."""
    
    id: int
    bill_type: str
    category: str
    amount: Decimal
    date: str
    description: Optional[str] = None
    created_at: str
    updated_at: str


class BillQueryResponse(BaseModel):
    """Bill query response with pagination."""
    
    items: list[BillItem]
    total: int = Field(description="Total number of matching bills")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class BillStatistics(BaseModel):
    """Bill statistics for query result."""
    
    total_income: Decimal = Field(description="Total income amount")
    total_expense: Decimal = Field(description="Total expense amount")
    net_amount: Decimal = Field(description="Net amount (income - expense)")
    count: int = Field(description="Total number of bills")
