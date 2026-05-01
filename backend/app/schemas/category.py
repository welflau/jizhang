from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    type: str = Field(..., description="分类类型：income(收入) 或 expense(支出)")
    icon: Optional[str] = Field(None, max_length=50, description="图标名称")
    color: Optional[str] = Field(None, max_length=20, description="颜色代码")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")

    @validator('type')
    def validate_type(cls, v):
        if v not in ['income', 'expense']:
            raise ValueError('分类类型必须是 income 或 expense')
        return v

    @validator('color')
    def validate_color(cls, v):
        if v is None:
            return v
        # 验证颜色格式（支持 hex 和 rgb）
        if not (v.startswith('#') or v.startswith('rgb')):
            raise ValueError('颜色格式不正确，应为 #RRGGBB 或 rgb(r,g,b)')
        return v


class CategoryCreate(CategoryBase):
    """创建分类模型"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="分类名称")
    type: Optional[str] = Field(None, description="分类类型")
    icon: Optional[str] = Field(None, max_length=50, description="图标名称")
    color: Optional[str] = Field(None, max_length=20, description="颜色代码")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")

    @validator('type')
    def validate_type(cls, v):
        if v is not None and v not in ['income', 'expense']:
            raise ValueError('分类类型必须是 income 或 expense')
        return v

    @validator('color')
    def validate_color(cls, v):
        if v is None:
            return v
        if not (v.startswith('#') or v.startswith('rgb')):
            raise ValueError('颜色格式不正确，应为 #RRGGBB 或 rgb(r,g,b)')
        return v


class CategoryInDB(CategoryBase):
    """数据库分类模型"""
    id: int
    user_id: int
    is_system: bool = Field(default=False, description="是否为系统预设分类")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryResponse(CategoryInDB):
    """分类响应模型"""
    record_count: Optional[int] = Field(None, description="关联的记录数量")


class CategoryListResponse(BaseModel):
    """分类列表响应模型（按类型分组）"""
    income: list[CategoryResponse] = Field(default_factory=list, description="收入分类列表")
    expense: list[CategoryResponse] = Field(default_factory=list, description="支出分类列表")
    total: int = Field(..., description="分类总数")


class CategoryDeleteResponse(BaseModel):
    """删除分类响应模型"""
    success: bool
    message: str
    deleted_id: int
    affected_records: Optional[int] = Field(None, description="受影响的记录数")