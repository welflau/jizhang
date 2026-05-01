import sqlite3
from contextlib import contextmanager
from typing import Optional
import os


DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/finance.db')


def get_db_connection():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """数据库连接上下文管理器"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db():
    """初始化数据库"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 创建迁移版本表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 获取当前数据库版本
        cursor.execute('SELECT MAX(version) as version FROM schema_migrations')
        result = cursor.fetchone()
        current_version = result['version'] if result['version'] else 0
        
        # 执行迁移
        run_migrations(conn, current_version)


def run_migrations(conn, current_version: int):
    """执行数据库迁移"""
    cursor = conn.cursor()
    
    # 迁移版本 1: 创建 users 表
    if current_version < 1:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('INSERT INTO schema_migrations (version) VALUES (1)')
        print('Migration 1: Created users table')
    
    # 迁移版本 2: 创建 categories 表
    if current_version < 2:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                icon TEXT,
                color TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, name, type)
            )
        ''')
        
        # 添加索引优化查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_categories_user_type ON categories(user_id, type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_categories_is_default ON categories(is_default)')
        
        cursor.execute('INSERT INTO schema_migrations (version) VALUES (2)')
        print('Migration 2: Created categories table with indexes')
    
    # 迁移版本 3: 创建 accounts 表
    if current_version < 3:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'CNY',
                icon TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id)')
        cursor.execute('INSERT INTO schema_migrations (version) VALUES (3)')
        print('Migration 3: Created accounts table')
    
    # 迁移版本 4: 创建 transactions 表
    if current_version < 4:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                account_id INTEGER NOT NULL,
                category_id INTEGER,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense', 'transfer')),
                amount REAL NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_category_id ON transactions(category_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type)')
        cursor.execute('INSERT INTO schema_migrations (version) VALUES (4)')
        print('Migration 4: Created transactions table')
    
    conn.commit()


def seed_default_categories():
    """为新用户创建默认分类"""
    default_categories = [
        # 支出分类
        {'name': '餐饮', 'type': 'expense', 'icon': '🍔', 'color': '#FF6B6B', 'is_default': 1},
        {'name': '交通', 'type': 'expense', 'icon': '🚗', 'color': '#4ECDC4', 'is_default': 1},
        {'name': '购物', 'type': 'expense', 'icon': '🛍️', 'color': '#95E1D3', 'is_default': 1},
        {'name': '娱乐', 'type': 'expense', 'icon': '🎮', 'color': '#F38181', 'is_default': 1},
        {'name': '医疗', 'type': 'expense', 'icon': '💊', 'color': '#AA96DA', 'is_default': 1},
        {'name': '教育', 'type': 'expense', 'icon': '📚', 'color': '#FCBAD3', 'is_default': 1},
        {'name': '住房', 'type': 'expense', 'icon': '🏠', 'color': '#FFFFD2', 'is_default': 1},
        {'name': '其他', 'type': 'expense', 'icon': '📦', 'color': '#A8D8EA', 'is_default': 1},
        
        # 收入分类
        {'name': '工资', 'type': 'income', 'icon': '💰', 'color': '#6BCF7F', 'is_default': 1},
        {'name': '奖金', 'type': 'income', 'icon': '🎁', 'color': '#4CAF50', 'is_default': 1},
        {'name': '投资', 'type': 'income', 'icon': '📈', 'color': '#8BC34A', 'is_default': 1},
        {'name': '兼职', 'type': 'income', 'icon': '💼', 'color': '#CDDC39', 'is_default': 1},
        {'name': '其他', 'type': 'income', 'icon': '💵', 'color': '#FFC107', 'is_default': 1},
    ]
    
    return default_categories


def create_default_categories_for_user(user_id: int):
    """为指定用户创建默认分类"""
    with get_db() as conn:
        cursor = conn.cursor()
        default_categories = seed_default_categories()
        
        for category in default_categories:
            cursor.execute('''
                INSERT INTO categories (user_id, name, type, icon, color, is_default)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, category['name'], category['type'], 
                  category['icon'], category['color'], category['is_default']))
        
        conn.commit()


if __name__ == '__main__':
    init_db()
    print('Database initialized successfully!')