# backend/app.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session
from config.config import Config
from backend.models.db import init_db
from backend.routes.auth_routes import auth_bp
from backend.routes.transaction_routes import tx_bp
from backend.routes.friend_routes import friend_bp
from backend.routes.backup_routes import backup_bp
from backend.services.backup_service import check_and_auto_backup

app = Flask(__name__,
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'),
    static_url_path='/static'
)

app.secret_key = Config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(tx_bp)
app.register_blueprint(friend_bp)
app.register_blueprint(backup_bp)

# Serve frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

@app.route('/')
def index():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(frontend_dir, filename)

# Initialize __init__ files
def create_init_files():
    dirs = [
        'backend',
        'backend/models',
        'backend/routes',
        'backend/services',
        'config'
    ]
    base = os.path.dirname(os.path.dirname(__file__))
    for d in dirs:
        init_file = os.path.join(base, d, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'w').close()

if __name__ == '__main__':
    create_init_files()
    print("🚀 Initializing database...")
    try:
        init_db()
    except Exception as e:
        print(f"⚠️  DB init error: {e}")
        print("Make sure PostgreSQL is running and credentials in config/config.py are correct.")
        sys.exit(1)

    print("🔍 Checking auto-backup...")
    backup_result = check_and_auto_backup()
    if backup_result:
        print(f"✅ Auto-backup created: {backup_result}")

    print("✅ Starting Student Expense Tracker...")
    print("🌐 Open http://localhost:5000 in your browser")
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
