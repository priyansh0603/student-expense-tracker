# backend/services/backup_service.py
import subprocess
import os
from datetime import datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import Config

def create_backup(month: str = None) -> dict:
    """
    Create a PostgreSQL backup for a given month (YYYY-MM).
    Saves to /backups/YYYY_MM.sql
    """
    if not month:
        month = datetime.now().strftime("%Y-%m")

    os.makedirs(Config.BACKUP_DIR, exist_ok=True)
    filename = month.replace("-", "_") + ".sql"
    filepath = os.path.join(Config.BACKUP_DIR, filename)

    env = os.environ.copy()
    env["PGPASSWORD"] = Config.DB_PASSWORD

    cmd = [
        "pg_dump",
        "-h", Config.DB_HOST,
        "-p", str(Config.DB_PORT),
        "-U", Config.DB_USER,
        "-d", Config.DB_NAME,
        "--no-password",
        "-f", filepath
    ]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            size = os.path.getsize(filepath)
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "size_kb": round(size / 1024, 2),
                "month": month
            }
        else:
            return {"success": False, "error": result.stderr}
    except FileNotFoundError:
        return {"success": False, "error": "pg_dump not found. Make sure PostgreSQL client tools are installed."}

def list_backups() -> list:
    """List all backup files."""
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)
    files = []
    for f in sorted(os.listdir(Config.BACKUP_DIR), reverse=True):
        if f.endswith(".sql"):
            fp = os.path.join(Config.BACKUP_DIR, f)
            files.append({
                "filename": f,
                "month": f.replace("_", "-").replace(".sql", ""),
                "size_kb": round(os.path.getsize(fp) / 1024, 2),
                "created": datetime.fromtimestamp(os.path.getctime(fp)).strftime("%Y-%m-%d %H:%M")
            })
    return files

def check_and_auto_backup():
    """
    Auto-backup trigger: if today is the 1st of the month, backup last month.
    Call this on app startup.
    """
    today = datetime.now()
    if today.day == 1:
        last_month = (today.replace(day=1) - __import__('datetime').timedelta(days=1)).strftime("%Y-%m")
        filename = last_month.replace("-", "_") + ".sql"
        filepath = os.path.join(Config.BACKUP_DIR, filename)
        if not os.path.exists(filepath):
            return create_backup(last_month)
    return None
