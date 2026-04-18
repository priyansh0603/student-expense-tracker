#!/usr/bin/env python3
"""
run.py - Start the Student Expense Tracker
Usage: python run.py

Production / cloud: bind 0.0.0.0 so the app accepts external connections (e.g. Render).
Set DEBUG=False in the environment for production. Render sets PORT; default is 5000.
"""
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

# Create __init__ files if missing
for d in ['backend', 'backend/models', 'backend/routes', 'backend/services', 'config']:
    init = os.path.join(os.path.dirname(__file__), d, '__init__.py')
    if not os.path.exists(init):
        open(init, 'w').close()

from backend.app import app, init_db, check_and_auto_backup
from config.config import Config

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

    port = int(os.getenv("PORT", "5000"))
    debug = Config.DEBUG

    print("─" * 40)
    print(f"🌐 Listening on http://0.0.0.0:{port}  (debug={debug})")
    print("   Local browser: http://127.0.0.1:{}".format(port))
    print("   Press Ctrl+C to stop")
    print("─" * 40)

    app.run(host="0.0.0.0", port=port, debug=debug)
