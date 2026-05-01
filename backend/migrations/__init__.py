"""
Database migrations package initialization.
"""

import os
import importlib.util
from typing import List, Optional
from datetime import datetime


class Migration:
    """Base migration class."""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.applied_at: Optional[datetime] = None
    
    def up(self, cursor):
        """Apply migration."""
        raise NotImplementedError
    
    def down(self, cursor):
        """Rollback migration."""
        raise NotImplementedError


class MigrationManager:
    """Manage database migrations."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Create migrations tracking table if not exists."""
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
        """Get list of applied migration versions."""
        cursor = self.db.cursor()
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        return [row[0] for row in cursor.fetchall()]
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        applied = set(self.get_applied_migrations())
        all_migrations = self._discover_migrations()
        return [m for m in all_migrations if m.version not in applied]
    
    def _discover_migrations(self) -> List[Migration]:
        """Discover all migration files."""
        migrations = []
        migrations_dir = os.path.dirname(__file__)
        
        for filename in sorted(os.listdir(migrations_dir)):
            if filename.startswith('migration_') and filename.endswith('.py'):
                module_name = filename[:-3]
                module_path = os.path.join(migrations_dir, filename)
                
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'migration'):
                        migrations.append(module.migration)
        
        return migrations
    
    def apply_migration(self, migration: Migration):
        """Apply a single migration."""
        cursor = self.db.cursor()
        
        try:
            print(f"Applying migration {migration.version}: {migration.description}")
            migration.up(cursor)
            
            cursor.execute(
                "INSERT INTO schema_migrations (version, description) VALUES (%s, %s)",
                (migration.version, migration.description)
            )
            
            self.db.commit()
            print(f"✓ Migration {migration.version} applied successfully")
            
        except Exception as e:
            self.db.rollback()
            print(f"✗ Migration {migration.version} failed: {str(e)}")
            raise
    
    def rollback_migration(self, migration: Migration):
        """Rollback a single migration."""
        cursor = self.db.cursor()
        
        try:
            print(f"Rolling back migration {migration.version}: {migration.description}")
            migration.down(cursor)
            
            cursor.execute(
                "DELETE FROM schema_migrations WHERE version = %s",
                (migration.version,)
            )
            
            self.db.commit()
            print(f"✓ Migration {migration.version} rolled back successfully")
            
        except Exception as e:
            self.db.rollback()
            print(f"✗ Rollback of migration {migration.version} failed: {str(e)}")
            raise
    
    def migrate(self, target_version: Optional[str] = None):
        """Run all pending migrations up to target version."""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("No pending migrations")
            return
        
        for migration in pending:
            if target_version and migration.version > target_version:
                break
            self.apply_migration(migration)
    
    def rollback(self, steps: int = 1):
        """Rollback the last N migrations."""
        applied = self.get_applied_migrations()
        
        if not applied:
            print("No migrations to rollback")
            return
        
        all_migrations = {m.version: m for m in self._discover_migrations()}
        
        for version in reversed(applied[-steps:]):
            if version in all_migrations:
                self.rollback_migration(all_migrations[version])
    
    def status(self):
        """Show migration status."""
        applied = set(self.get_applied_migrations())
        all_migrations = self._discover_migrations()
        
        print("\nMigration Status:")
        print("-" * 80)
        
        for migration in all_migrations:
            status = "✓ Applied" if migration.version in applied else "✗ Pending"
            print(f"{status} | {migration.version} | {migration.description}")
        
        print("-" * 80)
        print(f"Total: {len(all_migrations)} migrations, "
              f"{len(applied)} applied, "
              f"{len(all_migrations) - len(applied)} pending\n")


def get_migration_manager(db_connection):
    """Factory function to create migration manager."""
    return MigrationManager(db_connection)