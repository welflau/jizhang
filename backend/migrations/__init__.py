"""
Database migrations package initialization.
Provides database migration utilities and version management.
"""

import os
import importlib
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Migration:
    """Base migration class"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.now()
    
    def up(self, cursor):
        """Apply migration"""
        raise NotImplementedError("Subclasses must implement up() method")
    
    def down(self, cursor):
        """Rollback migration"""
        raise NotImplementedError("Subclasses must implement down() method")


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.migrations_dir = os.path.dirname(__file__)
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Create migrations tracking table if not exists"""
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        cursor = self.db.cursor()
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        return [row[0] for row in cursor.fetchall()]
    
    def get_pending_migrations(self) -> List[tuple]:
        """Get list of pending migrations"""
        applied = set(self.get_applied_migrations())
        all_migrations = self._discover_migrations()
        return [(v, d, m) for v, d, m in all_migrations if v not in applied]
    
    def _discover_migrations(self) -> List[tuple]:
        """Discover all migration files"""
        migrations = []
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith('.py') and filename != '__init__.py':
                version = filename.replace('.py', '')
                module_name = f'backend.migrations.{version}'
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, 'migration'):
                        migration = module.migration
                        migrations.append((version, migration.description, migration))
                except Exception as e:
                    logger.error(f"Error loading migration {filename}: {e}")
        return migrations
    
    def migrate(self, target_version: Optional[str] = None):
        """Run pending migrations up to target version"""
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return
        
        for version, description, migration in pending:
            if target_version and version > target_version:
                break
            
            logger.info(f"Applying migration {version}: {description}")
            cursor = self.db.cursor()
            
            try:
                migration.up(cursor)
                cursor.execute(
                    "INSERT INTO schema_migrations (version, description) VALUES (%s, %s)",
                    (version, description)
                )
                self.db.commit()
                logger.info(f"Migration {version} applied successfully")
            except Exception as e:
                self.db.rollback()
                logger.error(f"Error applying migration {version}: {e}")
                raise
    
    def rollback(self, target_version: Optional[str] = None):
        """Rollback migrations to target version"""
        applied = self.get_applied_migrations()
        
        if not applied:
            logger.info("No migrations to rollback")
            return
        
        # Rollback in reverse order
        for version in reversed(applied):
            if target_version and version <= target_version:
                break
            
            module_name = f'backend.migrations.{version}'
            try:
                module = importlib.import_module(module_name)
                migration = module.migration
                
                logger.info(f"Rolling back migration {version}: {migration.description}")
                cursor = self.db.cursor()
                
                try:
                    migration.down(cursor)
                    cursor.execute("DELETE FROM schema_migrations WHERE version = %s", (version,))
                    self.db.commit()
                    logger.info(f"Migration {version} rolled back successfully")
                except Exception as e:
                    self.db.rollback()
                    logger.error(f"Error rolling back migration {version}: {e}")
                    raise
            except Exception as e:
                logger.error(f"Error loading migration {version}: {e}")
                raise
    
    def status(self):
        """Show migration status"""
        applied = set(self.get_applied_migrations())
        all_migrations = self._discover_migrations()
        
        print("\nMigration Status:")
        print("-" * 80)
        print(f"{'Version':<30} {'Status':<10} {'Description'}")
        print("-" * 80)
        
        for version, description, _ in all_migrations:
            status = "Applied" if version in applied else "Pending"
            print(f"{version:<30} {status:<10} {description}")
        
        print("-" * 80)
        print(f"Total: {len(all_migrations)}, Applied: {len(applied)}, Pending: {len(all_migrations) - len(applied)}")


def get_migration_manager(db_connection):
    """Factory function to create migration manager"""
    return MigrationManager(db_connection)


__all__ = ['Migration', 'MigrationManager', 'get_migration_manager']