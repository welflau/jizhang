"""Clear API endpoint for visitor records."""
import logging
from flask import Blueprint, request, jsonify
from backend.database import get_db_connection

logger = logging.getLogger(__name__)
clear_bp = Blueprint('clear', __name__)

# Simple token-based authentication (should be in env var in production)
CLEAR_TOKEN = "dev_clear_token_12345"


def verify_clear_token(token):
    """Verify clear operation token.
    
    Args:
        token: Token from request header
        
    Returns:
        bool: True if valid
    """
    return token == CLEAR_TOKEN


@clear_bp.route('/api/clear', methods=['POST'])
def clear_records():
    """Clear all visitor records from database.
    
    Requires:
        X-Clear-Token header for authentication
        
    Returns:
        JSON response with deleted count
    """
    try:
        # Verify token
        token = request.headers.get('X-Clear-Token')
        
        if not token:
            return jsonify({'error': 'Missing X-Clear-Token header'}), 401
        
        if not verify_clear_token(token):
            logger.warning(f"Invalid clear token attempt from {request.remote_addr}")
            return jsonify({'error': 'Invalid token'}), 403
        
        # Get current count before deletion
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM visits')
        count_before = cursor.fetchone()[0]
        
        # Delete all records
        cursor.execute('DELETE FROM visits')
        conn.commit()
        
        # Verify deletion
        cursor.execute('SELECT COUNT(*) FROM visits')
        count_after = cursor.fetchone()[0]
        
        conn.close()
        
        deleted_count = count_before - count_after
        
        logger.info(f"Cleared {deleted_count} records by {request.remote_addr}")
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'remaining_count': count_after
        }), 200
        
    except Exception as e:
        logger.exception(f"Clear operation failed: {e}")
        return jsonify({'error': 'Clear operation failed', 'detail': str(e)}), 500
