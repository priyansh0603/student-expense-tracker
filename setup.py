#!/usr/bin/env python3
"""
setup.py - First-time setup for Student Expense Tracker
Run this once before starting the app.
"""
import os
import sys
import subprocess

print("=" * 50)
print("  PocketTrack — Student Expense Tracker Setup")
print("=" * 50)

# 1. Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8+ required")
    sys.exit(1)
print("✅ Python version OK")

# 2. Install dependencies
print("\n📦 Installing Python dependencies...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
print("✅ Dependencies installed")

# 3. Prompt for DB credentials
print("\n🗄️  PostgreSQL Configuration")
print("(Press Enter to keep defaults)\n")

db_host = input("DB Host [localhost]: ").strip() or "localhost"
db_port = input("DB Port [5432]: ").strip() or "5432"
db_name = input("DB Name [student_expense_tracker]: ").strip() or "student_expense_tracker"
db_user = input("DB User [postgres]: ").strip() or "postgres"
db_pass = input("DB Password: ").strip()

# 4. Write config
config_content = f'''# config/config.py
import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "{db_host}")
    DB_PORT = os.getenv("DB_PORT", "{db_port}")
    DB_NAME = os.getenv("DB_NAME", "{db_name}")
    DB_USER = os.getenv("DB_USER", "{db_user}")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "{db_pass}")

    DATABASE_URL = f"postgresql://{{DB_USER}}:{{DB_PASSWORD}}@{{DB_HOST}}:{{DB_PORT}}/{{DB_NAME}}"

    SECRET_KEY = os.getenv("SECRET_KEY", "pockettrack-secret-2026-change-me")
    DEBUG = os.getenv("DEBUG", "True") == "True"

    BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
'''
with open("config/config.py", "w") as f:
    f.write(config_content)
print("✅ Config written")

# 5. Create database
print(f"\n🗄️  Creating database '{db_name}'...")
try:
    import psycopg
    from psycopg import sql

    conn = psycopg.connect(
        host=db_host,
        port=int(str(db_port).strip() or 5432),
        user=db_user,
        password=db_pass,
        dbname="postgres",
        autocommit=True,
    )
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"✅ Database '{db_name}' created")
    else:
        print(f"ℹ️  Database '{db_name}' already exists")
    cur.close()
    conn.close()
except Exception as e:
    print(f"⚠️  Could not create database automatically: {e}")
    print(f"   Please create the database manually: CREATE DATABASE {db_name};")

# 6. Create __init__.py files
for d in ['backend', 'backend/models', 'backend/routes', 'backend/services', 'config']:
    init = os.path.join(d, '__init__.py')
    if not os.path.exists(init):
        open(init, 'w').close()

# 7. Create backups dir
os.makedirs("backups", exist_ok=True)

# 8. Initialize schema
print("\n🏗️  Initializing database schema...")
try:
    sys.path.insert(0, os.getcwd())
    from backend.models.db import init_db
    init_db()
    print("✅ Schema created")
except Exception as e:
    print(f"⚠️  Schema init failed: {e}")

print("\n" + "=" * 50)
print("  ✅ Setup complete!")
print("=" * 50)
print("\n🚀 Start the app:")
print("   python run.py")
print("\n🌐 Then open:  http://localhost:5000")
print("=" * 50)
