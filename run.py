#!/usr/bin/env python3
"""
run.py - Start the Student Expense Tracker
Usage: python run.py

- Binds 0.0.0.0 for local and cloud (e.g. Render).
- Render: uses the PORT environment variable set by the platform.
- Local: if PORT is unset, picks the first free port starting at 5000 (5001, 5002, …)
  so "Address already in use" is avoided without manual changes.
"""
import errno
import os
import socket
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
from backend.models.db import execute_query

LISTEN_HOST = "0.0.0.0"
LOCAL_PORT_START = 5000
LOCAL_PORT_ATTEMPTS = 100


def _port_is_bindable(port, host=LISTEN_HOST):
    """Return True if we can bind TCP (host, port); False if address is in use or invalid."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
        return True
    except OSError:
        return False


def _first_free_port(start, host=LISTEN_HOST, max_attempts=LOCAL_PORT_ATTEMPTS):
    """Try start, start+1, … until a bind succeeds or max_attempts is reached."""
    for port in range(start, start + max_attempts):
        if _port_is_bindable(port, host):
            return port
    print(
        f"⚠️  No free TCP port in {start}–{start + max_attempts - 1}; "
        f"using {start} (server may error if still busy)."
    )
    return start


def resolve_listen_port():
    """
    Render / production: use PORT from the environment when set and valid.
    Local: when PORT is unset or invalid, use the first free port from 5000 upward.
    """
    raw = os.environ.get("PORT")
    if raw is not None and str(raw).strip() != "":
        try:
            return int(raw)
        except (TypeError, ValueError):
            print("⚠️  PORT is set but not a valid integer; scanning from 5000 for a free port.")

    chosen = _first_free_port(LOCAL_PORT_START, LISTEN_HOST, LOCAL_PORT_ATTEMPTS)
    if chosen != LOCAL_PORT_START:
        print(f"ℹ️  Port {LOCAL_PORT_START} is in use; using {chosen} instead.")
    return chosen


if __name__ == '__main__':
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)

    print("🚀 PocketTrack — Student Expense Tracker")
    print("─" * 40)

    print("📦 Initializing database...")
    try:
        # Check if database is already initialized
        row = execute_query("SELECT COUNT(*) as cnt FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users'", fetch='one')
        if row['cnt'] == 0:
            init_db()
            print("✅ Database initialized")
        else:
            print("✅ Database already initialized")
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("   Run setup.py first: python setup.py")
        sys.exit(1)

    # Auto-backup check
    result = check_and_auto_backup()
    if result and result.get('success'):
        print(f"💾 Auto-backup created: {result['filename']}")

    port = resolve_listen_port()

    print("─" * 40)
    print(f"🌐 Listening on http://{LISTEN_HOST}:{port}")
    print("   Local browser: http://127.0.0.1:{}".format(port))
    print("   Press Ctrl+C to stop")
    print("─" * 40)

    try:
        app.run(host=LISTEN_HOST, port=port)
    except OSError as e:
        # Rare race: port became busy between probe and bind; scan from next port
        if getattr(e, "errno", None) == errno.EADDRINUSE or "address already in use" in str(e).lower():
            print(f"⚠️  Port {port} became busy; retrying on another port…")
            port = _first_free_port(port + 1, LISTEN_HOST, LOCAL_PORT_ATTEMPTS)
            print(f"🌐 Retrying on http://127.0.0.1:{port}")
            app.run(host=LISTEN_HOST, port=port)
        else:
            raise
