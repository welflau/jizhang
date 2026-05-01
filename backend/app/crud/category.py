from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """获取单个分类"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None
) -> List[Category]:
    """获取分类列表，可按类型筛选"""
    query = db.query(Category)
    
    if type:
        query = query.filter(Category.type == type)
    
    return query.offset(skip).limit(limit).all()


def get_categories_by_type(db: Session) -> dict:
    """按收入/支出分组获取分类列表"""
    income_categories = db.query(Category).filter(
        Category.type == "income"
    ).order_by(Category.name).all()
    
    expense_categories = db.query(Category).filter(
        Category.type == "expense"
    ).order_by(Category.name).all()
    
    return {
        "income": income_categories,
        "expense": expense_categories
    }


def get_category_by_name(
    db: Session,
    name: str,
    type: str,
    user_id: int
) -> Optional[Category]:
    """根据名称和类型获取分类（用于检查重复）"""
    return db.query(Category).filter(
        Category.name == name,
        Category.type == type,
        Category.user_id == user_id
    ).first()


def create_category(
    db: Session,
    category: CategoryCreate,
    user_id: int
) -> Category:
    """创建新分类"""
    db_category = Category(
        name=category.name,
        type=category.type,
        icon=category.icon,
        color=category.color,
        user_id=user_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
    db: Session,
    category_id: int,
    category_update: CategoryUpdate
) -> Optional[Category]:
    """更新分类信息"""
    db_category = get_category(db, category_id)
    
    if not db_category:
        return None
    
    update_data = category_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """删除分类"""
    db_category = get_category(db, category_id)
    
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True


def check_category_has_records(db: Session, category_id: int) -> bool:
    """检查分类是否有关联的记账记录"""
    from app.models.record import Record
    
    count = db.query(Record).filter(
        Record.category_id == category_id
    ).count()
    
    return count > 0


def get_user_categories(
    db: Session,
    user_id: int,
    type: Optional[str] = None
) -> List[Category]:
    """获取用户的分类列表"""
    query = db.query(Category).filter(Category.user_id == user_id)
    
    if type:
        query = query.filter(Category.type == type)
    
    return query.order_by(Category.name).all()


def get_user_categories_by_type(db: Session, user_id: int) -> dict:
    """按收入/支出分组获取用户的分类列表"""
    income_categories = db.query(Category).filter(
        Category.user_id == user_id,
        Category.type == "income"
    ).order_by(Category.name).all()
    
    expense_categories = db.query(Category).filter(
        Category.user_id == user_id,
        Category.type == "expense"
    ).order_by(Category.name).all()
    
    return {
        "income": income_categories,
        "expense": expense_categories
    }


def count_categories_by_user(db: Session, user_id: int) -> dict:
    """统计用户的分类数量"""
    income_count = db.query(Category).filter(
        Category.user_id == user_id,
        Category.type == "income"
    ).count()
    
    expense_count = db.query(Category).filter(
        Category.user_id == user_id,
        Category.type == "expense"
    ).count()
    
    return {
        "income": income_count,
        "expense": expense_count,
        "total": income_count + expense_count
    }


def bulk_create_categories(
    db: Session,
    categories: List[CategoryCreate],
    user_id: int
) -> List[Category]:
    """批量创建分类"""
    db_categories = []
    
    for category in categories:
        db_category = Category(
            name=category.name,
            type=category.type,
            icon=category.icon,
            color=category.color,
            user_id=user_id
        )
        db_categories.append(db_category)
    
    db.add_all(db_categories)
    db.commit()
    
    for db_category in db_categories:
        db.refresh(db_category)
    
    return db_categories


def get_default_categories() -> List[dict]:
    """获取默认分类列表（用于新用户初始化）"""
    return [
        # 支出分类
        {"name": "餐饮", "type": "expense", "icon": "🍜", "color": "#FF6B6B"},
        {"name": "交通", "type": "expense", "icon": "🚗", "color": "#4ECDC4"},
        {"name": "购物", "type": "expense", "icon": "🛍️", "color": "#95E1D3"},
        {"name": "娱乐", "type": "expense", "icon": "🎮", "color": "#F38181"},
        {"name": "医疗", "type": "expense", "icon": "💊", "color": "#AA96DA"},
        {"name": "住房", "type": "expense", "icon": "🏠", "color": "#FCBAD3"},
        {"name": "教育", "type": "expense", "icon": "📚", "color": "#A8D8EA"},
        {"name": "通讯", "type": "expense", "icon": "📱", "color": "#FFD93D"},
        {"name": "其他", "type": "expense", "icon": "📦", "color": "#C7CEEA"},
        
        # 收入分类
        {"name": "工资", "type": "income", "icon": "💰", "color": "#6BCF7F"},
        {"name": "奖金", "type": "income", "icon": "🎁", "color": "#4D96FF"},
        {"name": "投资", "type": "income", "icon": "📈", "color": "#FFB84D"},
        {"name": "兼职", "type": "income", "icon": "💼", "color": "#A78BFA"},
        {"name": "其他", "type": "income", "icon": "💵", "color": "#34D399"},
    ]


def initialize_default_categories(db: Session, user_id: int) -> List[Category]:
    """为新用户初始化默认分类"""
    default_categories = get_default_categories()
    
    db_categories = []
    for cat_data in default_categories:
        db_category = Category(
            name=cat_data["name"],
            type=cat_data["type"],
            icon=cat_data["icon"],
            color=cat_data["color"],
            user_id=user_id
        )
        db_categories.append(db_category)
    
    db.add_all(db_categories)
    db.commit()
    
    for db_category in db_categories:
        db.refresh(db_category)
    
    return db_categories