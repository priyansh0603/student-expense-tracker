# config/config.py — Flask app + PostgreSQL (pgAdmin) settings
import os

# Optional: load .env from project root when using python-dotenv
try:
    from dotenv import load_dotenv

    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(_root, ".env"))
except ImportError:
    pass


class Config:
    # PostgreSQL — match your pgAdmin server registration (host, user, password, database)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "student_expense_tracker")
    DB_USER = os.getenv("DB_USER", "postgres")
    # Numeric password: use quotes in Python → "2504". In .env: DB_PASSWORD=2504 (no quotes needed).
    DB_PASSWORD = os.getenv("DB_PASSWORD", "2504")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # Backup
    BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
