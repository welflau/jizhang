"""Main Flask application with visitor tracking and data management APIs."""
import os
import logging
from flask import Flask, request, jsonify
from backend.database import init_db, get_db_connection
from backend.api.export import export_bp
from backend.api.import_data import import_bp
from backend.api.clear import clear_bp
from backend.api.bills import bills_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Register blueprints
app.register_blueprint(export_bp)
app.register_blueprint(import_bp)
app.register_blueprint(clear_bp)
app.register_blueprint(bills_bp)

# Initialize database
init_db()


@app.before_request
def track_visit():
    """Track visitor information before each request."""
    # Skip tracking for API endpoints
    if request.path.startswith('/api/'):
        return
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO visits (timestamp, ip, user_agent, path, method)
            VALUES (datetime('now'), ?, ?, ?, ?)
        """, (
            request.remote_addr,
            request.headers.get('User-Agent', ''),
            request.path,
            request.method
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to track visit: {e}")


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get visitor statistics.
    
    Returns:
        JSON with total visits and recent records
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM visits')
        total = cursor.fetchone()[0]
        
        # Get recent visits
        cursor.execute("""
            SELECT id, timestamp, ip, path
            FROM visits
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        recent = []
        for row in cursor.fetchall():
            recent.append({
                'id': row[0],
                'timestamp': row[1],
                'ip': row[2],
                'path': row[3]
            })
        
        conn.close()
        
        return jsonify({
            'total_visits': total,
            'recent_visits': recent
        })
        
    except Exception as e:
        logger.exception(f"Failed to get stats: {e}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500


@app.route('/')
def index():
    """Serve main page."""
    return app.send_static_file('index.html')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)