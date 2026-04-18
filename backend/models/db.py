# backend/models/db.py — PostgreSQL via psycopg 3 (dict rows, autocommit)
import logging
import os
from typing import Any, Mapping, Optional, Sequence, Union

import psycopg
from psycopg.rows import dict_row

from config.config import Config

logger = logging.getLogger(__name__)

_Params = Optional[Union[Sequence[Any], Mapping[str, Any]]]


def get_connection():
    """
    Open a new PostgreSQL connection using credentials from config.config.Config.

    Defaults (overridable via environment / .env):
        host: localhost
        database: student_expense_tracker
        user: postgres
        password: set in Config (use your pgAdmin password)
        port: 5432

    Autocommit is enabled so each statement commits immediately.
    Rows are dict-like (same idea as RealDictCursor).
    """
    try:
        conn = psycopg.connect(
            host=Config.DB_HOST,
            port=int(str(Config.DB_PORT).strip() or 5432),
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=str(Config.DB_PASSWORD),
            connect_timeout=10,
            autocommit=True,
            row_factory=dict_row,
        )
        return conn
    except psycopg.OperationalError as e:
        msg = f"PostgreSQL connection failed: {e}"
        print(f"Database error: {msg}")
        logger.exception("PostgreSQL connection failed")
        raise


def execute_query(
    query: str,
    params: _Params = None,
    fetch: Optional[str] = None,
):
    """
    Run a single SQL statement with optional bound parameters.

    Uses dict rows (column name -> value), same as psycopg2 RealDictCursor.

    Args:
        query: SQL string (use %s placeholders for parameters).
        params: Values for placeholders, or None.
        fetch: None (default) for writes / no result set,
               "one" for fetchone(),
               "all" for fetchall().

    Returns:
        One dict, a list of dicts, or None depending on ``fetch``.

    Raises:
        psycopg.Error: Re-raised after logging and printing.
    """
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        if params is not None:
            cur.execute(query, params)
        else:
            cur.execute(query)

        if fetch == "one":
            return cur.fetchone()
        if fetch == "all":
            return cur.fetchall()
        return None
    except psycopg.Error as e:
        err = f"Database error: {e}"
        print(err)
        logger.exception("Query execution failed: %s", query[:200])
        raise
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


def init_db():
    """Apply database/schema.sql (users, transactions, friends, friend_transactions)."""
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "database",
        "schema.sql",
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()

    conn = None
    cur = None
    try:
        conn = psycopg.connect(
            host=Config.DB_HOST,
            port=int(str(Config.DB_PORT).strip() or 5432),
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=str(Config.DB_PASSWORD),
            connect_timeout=10,
            autocommit=True,
        )
        cur = conn.cursor()
        cur.execute(schema)
        print("✅ Database initialized successfully.")
        logger.info("Database schema applied from %s", schema_path)
    except psycopg.Error as e:
        err = f"Schema initialization failed: {e}"
        print(f"Database error: {err}")
        logger.exception("init_db failed")
        raise
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
