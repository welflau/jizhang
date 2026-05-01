"""Import API endpoint for visitor records."""
import json
import logging
from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError
from backend.database import get_db_connection

logger = logging.getLogger(__name__)
import_bp = Blueprint('import_data', __name__)

# JSON schema for validation
RECORD_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["timestamp", "ip"],
        "properties": {
            "id": {"type": "integer"},
            "timestamp": {"type": "string"},
            "ip": {"type": "string"},
            "user_agent": {"type": "string"},
            "path": {"type": "string"},
            "method": {"type": "string"}
        }
    }
}


def validate_json_schema(data):
    """Validate uploaded JSON against schema.
    
    Args:
        data: Parsed JSON data
        
    Raises:
        ValidationError: If schema validation fails
    """
    validate(instance=data, schema=RECORD_SCHEMA)


def batch_insert_with_transaction(records):
    """Insert records into database with transaction.
    
    Args:
        records: List of record dicts
        
    Returns:
        tuple: (imported_count, skipped_count, errors)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    imported_count = 0
    skipped_count = 0
    errors = []
    
    try:
        conn.execute('BEGIN TRANSACTION')
        
        for idx, record in enumerate(records):
            try:
                # Check if ID exists (if provided)
                if 'id' in record and record['id']:
                    cursor.execute('SELECT id FROM visits WHERE id = ?', (record['id'],))
                    if cursor.fetchone():
                        skipped_count += 1
                        logger.warning(f"Skipped duplicate ID: {record['id']}")
                        continue
                
                # Insert record
                cursor.execute("""
                    INSERT INTO visits (id, timestamp, ip, user_agent, path, method)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    record.get('id'),
                    record['timestamp'],
                    record['ip'],
                    record.get('user_agent', ''),
                    record.get('path', '/'),
                    record.get('method', 'GET')
                ))
                
                imported_count += 1
                
            except Exception as e:
                error_msg = f"Record {idx}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        conn.commit()
        logger.info(f"Import completed: {imported_count} imported, {skipped_count} skipped")
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Transaction failed: {e}")
        raise
    finally:
        conn.close()
    
    return imported_count, skipped_count, errors


@import_bp.route('/api/import', methods=['POST'])
def import_records():
    """Import visitor records from uploaded JSON file.
    
    Expects:
        multipart/form-data with 'file' field containing JSON
        
    Returns:
        JSON response with import statistics
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Parse JSON
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            return jsonify({'error': 'Invalid JSON format', 'detail': str(e)}), 400
        
        # Validate schema
        try:
            validate_json_schema(data)
        except ValidationError as e:
            return jsonify({'error': 'Schema validation failed', 'detail': str(e)}), 400
        
        # Import records
        imported_count, skipped_count, errors = batch_insert_with_transaction(data)
        
        return jsonify({
            'success': True,
            'imported_count': imported_count,
            'skipped_count': skipped_count,
            'errors': errors
        }), 200
        
    except Exception as e:
        logger.exception(f"Import failed: {e}")
        return jsonify({'error': 'Import failed', 'detail': str(e)}), 500
