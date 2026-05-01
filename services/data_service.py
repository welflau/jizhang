import sqlite3
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DataService:
    """
    Service layer for data management operations.
    Handles export, import, and clear operations with proper transaction management.
    """
    
    def __init__(self, db_path: str = 'visits.db'):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Create database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def export_all_records(self) -> List[Dict[str, Any]]:
        """
        Export all visit records sorted by timestamp.
        
        Returns:
            List of dictionaries containing all record fields
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, ip, user_agent, referer, path
                FROM visits
                ORDER BY timestamp ASC
            """)
            
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
            
            conn.close()
            
            logger.info(f"Exported {len(records)} records")
            return records
            
        except sqlite3.Error as e:
            logger.error(f"Database error during export: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during export: {e}")
            raise
    
    def import_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Import records with duplicate detection and transaction handling.
        
        Args:
            records: List of record dictionaries to import
            
        Returns:
            Dictionary with success_count, skipped_count, and errors list
        """
        result = {
            'success_count': 0,
            'skipped_count': 0,
            'errors': []
        }
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Start transaction
            conn.execute('BEGIN TRANSACTION')
            
            # Get existing IDs for duplicate detection
            cursor.execute('SELECT id FROM visits')
            existing_ids = {row[0] for row in cursor.fetchall()}
            
            for idx, record in enumerate(records):
                try:
                    record_id = record.get('id')
                    
                    # Skip if ID already exists
                    if record_id and record_id in existing_ids:
                        result['skipped_count'] += 1
                        logger.debug(f"Skipped duplicate ID: {record_id}")
                        continue
                    
                    # Validate required fields
                    timestamp = record.get('timestamp')
                    if not timestamp:
                        result['errors'].append({
                            'index': idx,
                            'error': 'Missing timestamp field'
                        })
                        continue
                    
                    # Insert record
                    cursor.execute("""
                        INSERT INTO visits (id, timestamp, ip, user_agent, referer, path)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        record_id,
                        timestamp,
                        record.get('ip', ''),
                        record.get('user_agent', ''),
                        record.get('referer', ''),
                        record.get('path', '/')
                    ))
                    
                    result['success_count'] += 1
                    
                    # Add to existing IDs set
                    if record_id:
                        existing_ids.add(record_id)
                    
                except sqlite3.IntegrityError as e:
                    result['errors'].append({
                        'index': idx,
                        'error': f'Database integrity error: {str(e)}'
                    })
                    logger.warning(f"Integrity error at record {idx}: {e}")
                except Exception as e:
                    result['errors'].append({
                        'index': idx,
                        'error': str(e)
                    })
                    logger.warning(f"Error processing record {idx}: {e}")
            
            # Commit transaction
            conn.commit()
            conn.close()
            
            logger.info(f"Import completed: {result['success_count']} success, "
                       f"{result['skipped_count']} skipped, {len(result['errors'])} errors")
            
            return result
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            logger.error(f"Database error during import: {e}")
            raise
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            logger.error(f"Unexpected error during import: {e}")
            raise
    
    def clear_all_records(self) -> int:
        """
        Clear all visit records from database.
        
        Returns:
            Number of records deleted
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get count before deletion
            cursor.execute('SELECT COUNT(*) FROM visits')
            count = cursor.fetchone()[0]
            
            # Delete all records
            cursor.execute('DELETE FROM visits')
            conn.commit()
            conn.close()
            
            logger.warning(f"Cleared all records: {count} records deleted")
            return count
            
        except sqlite3.Error as e:
            logger.error(f"Database error during clear: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during clear: {e}")
            raise
