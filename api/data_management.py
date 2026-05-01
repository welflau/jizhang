from flask import Blueprint, jsonify, request, send_file
from services.data_service import DataService
from utils.validators import validate_import_data
import logging
import io
import json

logger = logging.getLogger(__name__)
data_bp = Blueprint('data_management', __name__)
data_service = DataService()


@data_bp.route('/api/export', methods=['GET'])
def export_data():
    """
    Export all visit records as JSON file.
    Returns downloadable JSON file with all records sorted by timestamp.
    """
    try:
        records = data_service.export_all_records()
        
        # Create JSON file in memory
        json_data = json.dumps(records, indent=2, ensure_ascii=False)
        json_bytes = io.BytesIO(json_data.encode('utf-8'))
        json_bytes.seek(0)
        
        logger.info(f"Exported {len(records)} records")
        
        return send_file(
            json_bytes,
            mimetype='application/json',
            as_attachment=True,
            download_name='visit_records_export.json'
        )
    except Exception as e:
        logger.exception(f"Export failed: {e}")
        return jsonify({"error": "Export failed", "detail": str(e)}), 500


@data_bp.route('/api/import', methods=['POST'])
def import_data():
    """
    Import visit records from uploaded JSON file.
    Validates format, handles duplicates, uses transaction for atomicity.
    
    Request: multipart/form-data with 'file' field containing JSON
    Response: {success_count, skipped_count, errors[]}
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({"error": "File must be JSON format"}), 400
        
        # Read and parse JSON
        try:
            content = file.read().decode('utf-8')
            records = json.loads(content)
        except json.JSONDecodeError as e:
            return jsonify({"error": "Invalid JSON format", "detail": str(e)}), 400
        except UnicodeDecodeError as e:
            return jsonify({"error": "File encoding error", "detail": str(e)}), 400
        
        # Validate data structure
        validation_result = validate_import_data(records)
        if not validation_result['valid']:
            return jsonify({
                "error": "Data validation failed",
                "detail": validation_result['errors']
            }), 400
        
        # Import records
        result = data_service.import_records(records)
        
        logger.info(f"Import completed: {result['success_count']} success, "
                   f"{result['skipped_count']} skipped, {len(result['errors'])} errors")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.exception(f"Import failed: {e}")
        return jsonify({"error": "Import failed", "detail": str(e)}), 500


@data_bp.route('/api/clear', methods=['POST'])
def clear_data():
    """
    Clear all visit records from database.
    Requires confirmation token in request body.
    
    Request: {"confirm_token": "CLEAR_ALL_DATA"}
    Response: {"deleted_count": int, "message": str}
    """
    try:
        data = request.get_json()
        
        if not data or data.get('confirm_token') != 'CLEAR_ALL_DATA':
            return jsonify({
                "error": "Invalid confirmation token",
                "detail": "Must provide confirm_token='CLEAR_ALL_DATA'"
            }), 403
        
        deleted_count = data_service.clear_all_records()
        
        logger.warning(f"All records cleared: {deleted_count} records deleted")
        
        return jsonify({
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} records"
        }), 200
        
    except Exception as e:
        logger.exception(f"Clear operation failed: {e}")
        return jsonify({"error": "Clear operation failed", "detail": str(e)}), 500
