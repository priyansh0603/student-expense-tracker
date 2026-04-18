# backend/services/auth_service.py
import hashlib
import psycopg
from backend.models.db import execute_query

def hash_password(password: str) -> str:
    salt = "pockettrack_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def is_first_launch() -> bool:
    row = execute_query("SELECT COUNT(*) as cnt FROM users", fetch='one')
    return row['cnt'] == 0

def register(username: str, password: str, security_question: str, security_answer: str) -> dict:
    print("[register] Registration request received")
    print(f"[register] Incoming username: {username!r}")
    username = username.lower().strip()
    print(f"[register] Normalized username: {username!r}")
    security_answer = security_answer.strip().lower()
    if len(username) < 3:
        return {"success": False, "error": "Username must be at least 3 characters"}
    if len(password) < 4:
        return {"success": False, "error": "Password must be at least 4 characters"}
    if not security_question.strip():
        return {"success": False, "error": "Security question is required"}
    if not security_answer:
        return {"success": False, "error": "Security answer is required"}
    try:
        hashed_pass = hash_password(password)
        hashed_ans  = hash_password(security_answer)
        print("[register] Running insert query")
        execute_query(
            "INSERT INTO users (username, password_hash, security_question, security_answer_hash) VALUES (%s, %s, %s, %s)",
            (username, hashed_pass, security_question.strip(), hashed_ans)
        )
        print("[register] User inserted successfully")
        return {"success": True}
    except psycopg.errors.UniqueViolation as e:
        print(f"[register] Duplicate username detected: {e}")
        return {"success": False, "error": "User already exists"}
    except Exception as e:
        print(f"[register] Database error during registration: {e}")
        return {"success": False, "error": "Registration failed"}

def login(username: str, password: str) -> dict:
    username = username.strip().lower()
    hashed = hash_password(password)
    row = execute_query(
        "SELECT id, username FROM users WHERE username = %s AND password_hash = %s",
        (username, hashed), fetch='one'
    )
    if row:
        return {"success": True, "username": row['username']}
    return {"success": False, "error": "Incorrect username or password"}

def get_security_question(username: str) -> dict:
    username = username.strip().lower()
    row = execute_query("SELECT security_question FROM users WHERE username = %s", (username,), fetch='one')
    if not row:
        return {"success": False, "error": "Username not found"}
    return {"success": True, "question": row['security_question']}

def reset_password(username: str, security_answer: str, new_password: str) -> dict:
    username = username.strip().lower()
    security_answer = security_answer.strip().lower()
    if len(new_password) < 4:
        return {"success": False, "error": "New password must be at least 4 characters"}
    hashed_ans = hash_password(security_answer)
    row = execute_query(
        "SELECT id FROM users WHERE username = %s AND security_answer_hash = %s",
        (username, hashed_ans), fetch='one'
    )
    if not row:
        return {"success": False, "error": "Security answer is incorrect"}
    new_hash = hash_password(new_password)
    execute_query("UPDATE users SET password_hash = %s WHERE username = %s", (new_hash, username))
    return {"success": True}

def change_password(username: str, old_password: str, new_password: str) -> dict:
    result = login(username, old_password)
    if not result['success']:
        return {"success": False, "error": "Current password is incorrect"}
    if len(new_password) < 4:
        return {"success": False, "error": "New password must be at least 4 characters"}
    new_hash = hash_password(new_password)
    execute_query("UPDATE users SET password_hash = %s WHERE username = %s", (new_hash, username.lower()))
    return {"success": True}
