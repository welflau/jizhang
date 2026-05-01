from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import json
import os

app = FastAPI(title="分类管理系统")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据存储文件
DATA_FILE = "categories_data.json"

# 枚举类型
class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

# 数据模型
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    type: CategoryType = Field(..., description="分类类型：收入或支出")
    icon: Optional[str] = Field(None, max_length=50, description="图标名称")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="颜色代码")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('分类名称不能为空')
        return v.strip()

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = Field(None, max_length=200)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('分类名称不能为空')
        return v.strip() if v else v

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    record_count: int = Field(default=0, description="关联记录数")

class CategoriesResponse(BaseModel):
    income: List[Category]
    expense: List[Category]

# 数据存储类
class DataStore:
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载数据失败: {e}")
                return self.get_default_data()
        return self.get_default_data()
    
    def get_default_data(self) -> Dict:
        return {
            "categories": [],
            "records": [],
            "next_category_id": 1,
            "next_record_id": 1
        }
    
    def save_data(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"保存数据失败: {e}")
            raise HTTPException(status_code=500, detail="数据保存失败")
    
    def get_categories(self) -> List[Dict]:
        return self.data.get("categories", [])
    
    def get_category_by_id(self, category_id: int) -> Optional[Dict]:
        for category in self.data.get("categories", []):
            if category["id"] == category_id:
                return category
        return None
    
    def get_category_by_name(self, name: str, category_type: str, exclude_id: Optional[int] = None) -> Optional[Dict]:
        for category in self.data.get("categories", []):
            if category["name"] == name and category["type"] == category_type:
                if exclude_id is None or category["id"] != exclude_id:
                    return category
        return None
    
    def add_category(self, category_data: Dict) -> Dict:
        category_id = self.data["next_category_id"]
        now = datetime.now().isoformat()
        
        category = {
            "id": category_id,
            "name": category_data["name"],
            "type": category_data["type"],
            "icon": category_data.get("icon"),
            "color": category_data.get("color"),
            "description": category_data.get("description"),
            "created_at": now,
            "updated_at": now
        }
        
        self.data["categories"].append(category)
        self.data["next_category_id"] += 1
        self.save_data()
        
        return category
    
    def update_category(self, category_id: int, update_data: Dict) -> Dict:
        category = self.get_category_by_id(category_id)
        if not category:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                category[key] = value
        
        category["updated_at"] = datetime.now().isoformat()
        self.save_data()
        
        return category
    
    def delete_category(self, category_id: int) -> bool:
        categories = self.data.get("categories", [])
        for i, category in enumerate(categories):
            if category["id"] == category_id:
                del categories[i]
                self.save_data()
                return True
        return False
    
    def get_category_record_count(self, category_id: int) -> int:
        count = 0
        for record in self.data.get("records", []):
            if record.get("category_id") == category_id:
                count += 1
        return count

# 全局数据存储实例
store = DataStore()

# 依赖注入
def get_store():
    return store

# API端点
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "分类管理系统 API",
        "version": "1.0.0",
        "endpoints": {
            "获取分类列表": "GET /api/categories",
            "创建分类": "POST /api/categories",
            "更新分类": "PUT /api/categories/{id}",
            "删除分类": "DELETE /api/categories/{id}"
        }
    }

@app.get("/api/categories", response_model=CategoriesResponse, summary="获取分类列表")
async def get_categories(store: DataStore = Depends(get_store)):
    """
    获取所有分类，按收入和支出分组返回
    """
    categories = store.get_categories()
    
    income_categories = []
    expense_categories = []
    
    for cat in categories:
        record_count = store.get_category_record_count(cat["id"])
        category_data = {
            **cat,
            "record_count": record_count
        }
        
        if cat["type"] == CategoryType.INCOME:
            income_categories.append(category_data)
        else:
            expense_categories.append(category_data)
    
    # 按创建时间排序
    income_categories.sort(key=lambda x: x["created_at"], reverse=True)
    expense_categories.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "income": income_categories,
        "expense": expense_categories
    }

@app.post("/api/categories", response_model=Category, status_code=status.HTTP_201_CREATED, summary="创建分类")
async def create_category(category: CategoryCreate, store: DataStore = Depends(get_store)):
    """
    创建新分类
    
    - **name**: 分类名称（必填，1-50字符）
    - **type**: 分类类型（必填，income或expense）
    - **icon**: 图标名称（可选）
    - **color**: 颜色代码（可选，格式：#RRGGBB）
    - **description**: 分类描述（可选，最多200字符）
    """
    # 检查同类型下是否存在同名分类
    existing = store.get_category_by_name(category.name, category.type)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该类型下已存在名为 '{category.name}' 的分类"
        )
    
    # 创建分类
    new_category = store.add_category(category.dict())
    new_category["record_count"] = 0
    
    return new_category

@app.put("/api/categories/{category_id}", response_model=Category, summary="更新分类")
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    store: DataStore = Depends(get_store)
):
    """
    更新指定分类的信息
    
    - **category_id**: 分类ID
    - 可更新字段：name, icon, color, description
    - 注意：不能修改分类类型（type）
    """
    # 检查分类是否存在
    existing_category = store.get_category_by_id(category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    
    # 如果更新名称，检查是否与同类型其他分类重名
    if category_update.name:
        duplicate = store.get_category_by_name(
            category_update.name,
            existing_category["type"],
            exclude_id=category_id
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该类型下已存在名为 '{category_update.name}' 的分类"
            )
    
    # 更新分类
    update_data = category_update.dict(exclude_unset=True)
    updated_category = store.update_category(category_id, update_data)
    
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新分类失败"
        )
    
    updated_category["record_count"] = store.get_category_record_count(category_id)
    
    return updated_category

@app.delete("/api/categories/{category_id}", summary="删除分类")
async def delete_category(category_id: int, store: DataStore = Depends(get_store)):
    """
    删除指定分类
    
    - **category_id**: 分类ID
    - 注意：如果分类下有关联记录，将无法删除
    """
    # 检查分类是否存在
    category = store.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    
    # 检查是否有关联记录
    record_count = store.get_category_record_count(category_id)
    if record_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该分类下有 {record_count} 条关联记录，无法删除。请先删除或转移相关记录。"
        )
    
    # 删除分类
    success = store.delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除分类失败"
        )
    
    return {
        "success": True,
        "message": f"分类 '{category['name']}' 已成功删除",
        "deleted_id": category_id
    }

@app.get("/api/categories/{category_id}", response_model=Category, summary="获取单个分类详情")
async def get_category(category_id: int, store: DataStore = Depends(get_store)):
    """
    获取指定分类的详细信息
    """
    category = store.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分类ID {category_id} 不存在"
        )
    
    category["record_count"] = store.get_category_record_count(category_id)
    return category

# 异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "服务器内部错误",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)