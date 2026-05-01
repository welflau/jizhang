from flask import Flask, request, jsonify
import sqlite3
import logging
from datetime import datetime
from api.data_management import data_bp

app = Flask(__name__, static_folder='.', static_url_path='')
app.register_blueprint(data_bp)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = 'visits.db'


def init_db():
    """Initialize database with visits table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ip TEXT,
            user_agent TEXT,
            referer TEXT,
            path TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized")


@app.route('/')
def index():
    """Serve the main HTML page."""
    return app.send_static_file('index.html')


@app.route('/api/visit', methods=['POST'])
def record_visit():
    """Record a new visit."""
    try:
        data = request.get_json() or {}
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO visits (timestamp, ip, user_agent, referer, path)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            request.remote_addr,
            request.headers.get('User-Agent', ''),
            request.headers.get('Referer', ''),
            data.get('path', '/')
        ))
        
        conn.commit()
        visit_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"Visit recorded: ID={visit_id}, IP={request.remote_addr}")
        return jsonify({"success": True, "visit_id": visit_id}), 201
        
    except Exception as e:
        logger.exception(f"Failed to record visit: {e}")
        return jsonify({"error": "Failed to record visit"}), 500


@app.route('/api/visits/count', methods=['GET'])
def get_visit_count():
    """Get total visit count."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM visits')
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({"count": count}), 200
        
    except Exception as e:
        logger.exception(f"Failed to get visit count: {e}")
        return jsonify({"error": "Failed to get visit count"}), 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)
