from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    type: str = Field(..., pattern="^(income|expense)$", description="分类类型：income-收入，expense-支出")
    icon: Optional[str] = Field(None, max_length=50, description="图标名称")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="颜色代码")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")


class CategoryCreate(CategoryBase):
    """创建分类模型"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="分类名称")
    icon: Optional[str] = Field(None, max_length=50, description="图标名称")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="颜色代码")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")


class CategoryInDB(CategoryBase):
    """数据库分类模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryResponse(CategoryInDB):
    """分类响应模型"""
    record_count: Optional[int] = Field(0, description="关联的记录数量")


class CategoryListResponse(BaseModel):
    """分类列表响应模型"""
    income_categories: list[CategoryResponse] = Field(default_factory=list, description="收入分类列表")
    expense_categories: list[CategoryResponse] = Field(default_factory=list, description="支出分类列表")


class CategoryDeleteResponse(BaseModel):
    """删除分类响应模型"""
    message: str
    deleted_id: int