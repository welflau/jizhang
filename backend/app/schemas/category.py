from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    type: str = Field(..., description="分类类型：income 或 expense")
    icon: Optional[str] = Field(None, max_length=50, description="分类图标")
    color: Optional[str] = Field(None, max_length=20, description="分类颜色")
    sort_order: Optional[int] = Field(0, description="排序顺序")

    @validator('type')
    def validate_type(cls, v):
        if v not in ['income', 'expense']:
            raise ValueError('type must be either "income" or "expense"')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('name cannot be empty')
        return v.strip()

    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('color must start with #')
        return v


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="分类名称")
    icon: Optional[str] = Field(None, max_length=50, description="分类图标")
    color: Optional[str] = Field(None, max_length=20, description="分类颜色")
    sort_order: Optional[int] = Field(None, description="排序顺序")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('name cannot be empty')
        return v.strip() if v else v

    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('color must start with #')
        return v


class CategoryInDB(CategoryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Category(CategoryInDB):
    pass


class CategoryWithStats(Category):
    transaction_count: int = Field(0, description="关联的交易记录数量")
    total_amount: float = Field(0.0, description="该分类的总金额")


class CategoryListResponse(BaseModel):
    income: list[Category] = Field(default_factory=list, description="收入分类列表")
    expense: list[Category] = Field(default_factory=list, description="支出分类列表")


class CategoryDeleteResponse(BaseModel):
    success: bool
    message: str
    transaction_count: Optional[int] = None