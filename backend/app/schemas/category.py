from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    type: str = Field(..., description="分类类型：income（收入）或 expense（支出）")
    icon: Optional[str] = Field(None, max_length=50, description="图标名称")
    color: Optional[str] = Field(None, max_length=20, description="颜色代码")
    sort_order: int = Field(default=0, description="排序顺序")
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['income', 'expense']:
            raise ValueError('分类类型必须是 income 或 expense')
        return v
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None and not v.startswith('#'):
            raise ValueError('颜色代码必须以 # 开头')
        return v


class CategoryCreate(CategoryBase):
    """创建分类模型"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="分类名称")
    icon: Optional[str] = Field(None, max_length=50, description="图标名称")
    color: Optional[str] = Field(None, max_length=20, description="颜色代码")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None and not v.startswith('#'):
            raise ValueError('颜色代码必须以 # 开头')
        return v


class CategoryInDB(CategoryBase):
    """数据库中的分类模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Category(CategoryInDB):
    """返回给客户端的分类模型"""
    pass


class CategoryWithStats(Category):
    """带统计信息的分类模型"""
    record_count: int = Field(default=0, description="关联的记录数量")
    total_amount: float = Field(default=0.0, description="总金额")


class CategoryList(BaseModel):
    """分类列表响应模型"""
    income: list[Category] = Field(default_factory=list, description="收入分类列表")
    expense: list[Category] = Field(default_factory=list, description="支出分类列表")


class CategoryDelete(BaseModel):
    """删除分类响应模型"""
    message: str
    deleted_id: int
    affected_records: int = Field(default=0, description="受影响的记录数")