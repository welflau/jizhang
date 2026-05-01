from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def validate_import_data(records: Any) -> Dict[str, Any]:
    """
    Validate imported data structure and content.
    
    Args:
        records: Data to validate (should be list of dicts)
        
    Returns:
        Dictionary with 'valid' boolean and 'errors' list
    """
    result = {
        'valid': True,
        'errors': []
    }
    
    # Check if records is a list
    if not isinstance(records, list):
        result['valid'] = False
        result['errors'].append('Data must be a JSON array')
        return result
    
    # Check if empty
    if len(records) == 0:
        result['valid'] = False
        result['errors'].append('Data array is empty')
        return result
    
    # Validate each record
    required_fields = ['timestamp']
    optional_fields = ['id', 'ip', 'user_agent', 'referer', 'path']
    all_fields = required_fields + optional_fields
    
    for idx, record in enumerate(records):
        # Check if record is a dictionary
        if not isinstance(record, dict):
            result['errors'].append(f'Record at index {idx} is not an object')
            continue
        
        # Check required fields
        for field in required_fields:
            if field not in record or record[field] is None or record[field] == '':
                result['errors'].append(
                    f'Record at index {idx} missing required field: {field}'
                )
        
        # Check for unknown fields
        unknown_fields = set(record.keys()) - set(all_fields)
        if unknown_fields:
            logger.warning(f"Record {idx} has unknown fields: {unknown_fields}")
        
        # Validate field types
        if 'id' in record and record['id'] is not None:
            if not isinstance(record['id'], int):
                result['errors'].append(
                    f'Record at index {idx}: id must be integer'
                )
        
        if 'timestamp' in record:
            if not isinstance(record['timestamp'], str):
                result['errors'].append(
                    f'Record at index {idx}: timestamp must be string'
                )
    
    # Set valid flag based on errors
    if result['errors']:
        result['valid'] = False
    
    return result
