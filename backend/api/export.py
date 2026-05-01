"""Export API endpoint for visitor records."""
import json
import logging
from flask import Blueprint, jsonify, Response
from backend.database import get_db_connection

logger = logging.getLogger(__name__)
export_bp = Blueprint('export', __name__)


@export_bp.route('/api/export', methods=['GET'])
def export_records():
    """Export all visitor records as JSON file.
    
    Returns:
        JSON file download with all records sorted by timestamp.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query all records ordered by timestamp
        cursor.execute("""
            SELECT id, timestamp, ip, user_agent, path, method
            FROM visits
            ORDER BY timestamp ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        records = []
        for row in rows:
            records.append({
                'id': row[0],
                'timestamp': row[1],
                'ip': row[2],
                'user_agent': row[3],
                'path': row[4],
                'method': row[5]
            })
        
        logger.info(f"Exported {len(records)} records")
        
        # Create JSON response with download header
        json_data = json.dumps(records, indent=2, ensure_ascii=False)
        response = Response(
            json_data,
            mimetype='application/json',
            headers={
                'Content-Disposition': 'attachment; filename=visitor_records_export.json'
            }
        )
        
        return response
        
    except Exception as e:
        logger.exception(f"Export failed: {e}")
        return jsonify({'error': 'Export failed', 'detail': str(e)}), 500
