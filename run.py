#!/usr/bin/env python3
"""
run.py - Start the Student Expense Tracker
Usage: python run.py
"""
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

# Create __init__ files if missing
for d in ['backend', 'backend/models', 'backend/routes', 'backend/services', 'config']:
    init = os.path.join(os.path.dirname(__file__), d, '__init__.py')
    if not os.path.exists(init):
        open(init, 'w').close()

from backend.app import app, init_db, check_and_auto_backup
from config.config import Config
import os

if __name__ == '__main__':
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)

    print("🚀 PocketTrack — Student Expense Tracker")
    print("─" * 40)

    print("📦 Initializing database...")
    try:
        init_db()
        print("✅ Database ready")
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("   Run setup.py first: python setup.py")
        sys.exit(1)

    # Auto-backup check
    result = check_and_auto_backup()
    if result and result.get('success'):
        print(f"💾 Auto-backup created: {result['filename']}")

    print("─" * 40)
    print("🌐 Open http://localhost:5000 in your browser")
    print("   Press Ctrl+C to stop")
    print("─" * 40)

    app.run(debug=Config.DEBUG, host='127.0.0.1', port=5000)
