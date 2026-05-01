backend/database/migration_runner.py

import os
import sys
from pathlib import Path
from datetime import datetime
import importlib.util

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.database.connection import get_db_connection


class MigrationRunner:
    """数据库迁移运行器"""
    
    def __init__(self):
        self.migrations_dir = Path(__file__).parent / 'migrations'
        self.migrations_dir.mkdir(exist_ok=True)
        self.conn = get_db_connection()
        self._init_migrations_table()
    
    def _init_migrations_table(self):
        """初始化迁移记录表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def _get_applied_migrations(self):
        """获取已应用的迁移版本"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT version FROM schema_migrations ORDER BY version')
        return {row[0] for row in cursor.fetchall()}
    
    def _get_pending_migrations(self):
        """获取待执行的迁移文件"""
        applied = self._get_applied_migrations()
        migrations = []
        
        for file in sorted(self.migrations_dir.glob('*.py')):
            if file.name.startswith('__'):
                continue
            
            version = file.stem
            if version not in applied:
                migrations.append((version, file))
        
        return migrations
    
    def _load_migration_module(self, file_path):
        """动态加载迁移模块"""
        spec = importlib.util.spec_from_file_location("migration", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def _record_migration(self, version):
        """记录已应用的迁移"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO schema_migrations (version) VALUES (?)',
            (version,)
        )
        self.conn.commit()
    
    def migrate(self):
        """执行所有待执行的迁移"""
        pending = self._get_pending_migrations()
        
        if not pending:
            print("No pending migrations.")
            return
        
        print(f"Found {len(pending)} pending migration(s):")
        for version, _ in pending:
            print(f"  - {version}")
        
        for version, file_path in pending:
            print(f"\nApplying migration: {version}")
            try:
                module = self._load_migration_module(file_path)
                
                if hasattr(module, 'up'):
                    module.up(self.conn)
                    self._record_migration(version)
                    print(f"✓ Successfully applied: {version}")
                else:
                    print(f"✗ Migration {version} has no 'up' function")
            
            except Exception as e:
                print(f"✗ Error applying migration {version}: {e}")
                self.conn.rollback()
                raise
        
        print("\n✓ All migrations completed successfully!")
    
    def rollback(self, steps=1):
        """回滚指定数量的迁移"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT version FROM schema_migrations ORDER BY applied_at DESC LIMIT ?',
            (steps,)
        )
        versions = [row[0] for row in cursor.fetchall()]
        
        if not versions:
            print("No migrations to rollback.")
            return
        
        print(f"Rolling back {len(versions)} migration(s):")
        for version in versions:
            print(f"  - {version}")
        
        for version in versions:
            file_path = self.migrations_dir / f"{version}.py"
            
            if not file_path.exists():
                print(f"✗ Migration file not found: {version}")
                continue
            
            print(f"\nRolling back: {version}")
            try:
                module = self._load_migration_module(file_path)
                
                if hasattr(module, 'down'):
                    module.down(self.conn)
                    cursor.execute(
                        'DELETE FROM schema_migrations WHERE version = ?',
                        (version,)
                    )
                    self.conn.commit()
                    print(f"✓ Successfully rolled back: {version}")
                else:
                    print(f"✗ Migration {version} has no 'down' function")
            
            except Exception as e:
                print(f"✗ Error rolling back migration {version}: {e}")
                self.conn.rollback()
                raise
        
        print("\n✓ Rollback completed successfully!")
    
    def status(self):
        """显示迁移状态"""
        applied = self._get_applied_migrations()
        all_migrations = sorted([f.stem for f in self.migrations_dir.glob('*.py') 
                                if not f.name.startswith('__')])
        
        print("\nMigration Status:")
        print("-" * 60)
        
        if not all_migrations:
            print("No migrations found.")
            return
        
        for migration in all_migrations:
            status = "✓ Applied" if migration in applied else "✗ Pending"
            print(f"{status:12} {migration}")
        
        print("-" * 60)
        print(f"Total: {len(all_migrations)} | Applied: {len(applied)} | Pending: {len(all_migrations) - len(applied)}")
    
    def create_migration(self, name):
        """创建新的迁移文件"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        version = f"{timestamp}_{name}"
        file_path = self.migrations_dir / f"{version}.py"
        
        template = f'''"""
Migration: {name}
Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


def up(conn):
    """Apply migration"""
    cursor = conn.cursor()
    
    # TODO: Write your migration code here
    # Example:
    # cursor.execute(\'\'\'
    #     CREATE TABLE example (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT NOT NULL
    #     )
    # \'\'\')
    
    conn.commit()


def down(conn):
    """Rollback migration"""
    cursor = conn.cursor()
    
    # TODO: Write your rollback code here
    # Example:
    # cursor.execute('DROP TABLE IF EXISTS example')
    
    conn.commit()
'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"✓ Created migration: {version}")
        print(f"  File: {file_path}")
        return version
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('command', choices=['migrate', 'rollback', 'status', 'create'],
                       help='Migration command')
    parser.add_argument('--steps', type=int, default=1,
                       help='Number of migrations to rollback (default: 1)')
    parser.add_argument('--name', type=str,
                       help='Name for new migration')
    
    args = parser.parse_args()
    
    runner = MigrationRunner()
    
    try:
        if args.command == 'migrate':
            runner.migrate()
        elif args.command == 'rollback':
            runner.rollback(args.steps)
        elif args.command == 'status':
            runner.status()
        elif args.command == 'create':
            if not args.name:
                print("Error: --name is required for create command")
                sys.exit(1)
            runner.create_migration(args.name)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    
    finally:
        runner.close()


if __name__ == '__main__':
    main()