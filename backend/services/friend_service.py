# backend/services/friend_service.py
from datetime import date, datetime
from backend.models.db import execute_query

def get_current_month() -> str:
    return datetime.now().strftime("%Y-%m")

def get_or_create_friend(user_id: int, name: str) -> int:
    """Get existing friend by name (case-insensitive) or create new."""
    # Step 1: Normalize name
    name = name.strip()
    print(f"DEBUG get_or_create_friend - Checking for friend: '{name}' (user_id: {user_id})")
    
    # Step 2: Check if friend exists (case-insensitive)
    row = execute_query(
        "SELECT id FROM friends WHERE user_id = %s AND LOWER(name) = LOWER(%s)",
        (user_id, name), fetch='one'
    )
    
    if row:
        friend_id = row['id']
        print(f"DEBUG Friend exists with id: {friend_id}")
        return friend_id
    
    # Step 3: Friend doesn't exist - insert new friend
    print(f"DEBUG Friend '{name}' not found - creating new friend")
    new_row = execute_query(
        "INSERT INTO friends (name, user_id) VALUES (%s, %s) RETURNING id",
        (name, user_id), fetch='one'
    )
    friend_id = new_row['id']
    print(f"DEBUG New friend created with id: {friend_id}")
    return friend_id

def add_friend_transaction(user_id: int, friend_name: str, amount: float, type_: str, description: str = None, trans_date: str = None) -> dict:
    """Add a new friend money entry."""
    # Validate user_id is not None
    if user_id is None:
        print("ERROR: user_id is None")
        return {"success": False, "error": "User not authenticated"}
    
    print(f"DEBUG add_friend_transaction - user_id: {user_id}, friend_name: {friend_name}, amount: {amount}, type: {type_}")
    
    friend_id = get_or_create_friend(user_id, friend_name)
    print(f"DEBUG friend_id: {friend_id}")
    
    if trans_date:
        d = datetime.strptime(trans_date, "%Y-%m-%d").date()
    else:
        d = date.today()
    month = d.strftime("%Y-%m")
    
    print(f"DEBUG INSERT values - friend_id: {friend_id}, total_amount: {amount}, type: {type_}, description: {description}, date: {d}, month: {month}, user_id: {user_id}")
    
    row = execute_query(
        """INSERT INTO friend_transactions (friend_id, total_amount, paid_amount, type, description, date, month, user_id)
           VALUES (%s, %s, 0, %s, %s, %s, %s, %s) RETURNING id""",
        (friend_id, amount, type_, description, d, month, user_id),
        fetch='one'
    )
    
    print(f"DEBUG Transaction inserted with id: {row['id']}")
    return {"success": True, "id": row['id']}

def add_payment(user_id: int, transaction_id: int, payment_amount: float) -> dict:
    """Add a partial or full payment to a friend transaction."""
    row = execute_query(
        "SELECT * FROM friend_transactions WHERE user_id = %s AND id = %s",
        (user_id, transaction_id), fetch='one'
    )
    if not row:
        return {"success": False, "error": "Transaction not found"}

    new_paid = float(row['paid_amount']) + payment_amount
    total = float(row['total_amount'])
    if new_paid > total:
        return {"success": False, "error": f"Payment exceeds total. Max remaining: ₹{total - float(row['paid_amount']):.2f}"}

    new_status = 'completed' if new_paid >= total else 'pending'
    execute_query(
        "UPDATE friend_transactions SET paid_amount = %s, status = %s WHERE user_id = %s AND id = %s",
        (new_paid, new_status, user_id, transaction_id)
    )
    return {"success": True, "status": new_status, "remaining": round(total - new_paid, 2)}

def mark_completed(user_id: int, transaction_id: int) -> dict:
    """Mark a transaction as fully paid/received."""
    row = execute_query(
        "SELECT total_amount, type, status FROM friend_transactions WHERE user_id = %s AND id = %s",
        (user_id, transaction_id), fetch='one'
    )
    if not row:
        return {"success": False, "error": "Not found"}
    
    if row['status'] == 'completed':
        return {"success": False, "error": "Already completed"}
    
    # Update the transaction status
    execute_query(
        "UPDATE friend_transactions SET paid_amount = total_amount, status = 'completed' WHERE user_id = %s AND id = %s",
        (user_id, transaction_id)
    )
    
    # If this is a "receive" transaction, automatically add income to balance
    if row['type'] == 'receive':
        execute_query(
            """INSERT INTO transactions (type, amount, category, description, date, month, user_id)
               VALUES ('income', %s, 'Income', 'Received from friend', CURRENT_DATE, TO_CHAR(CURRENT_DATE, 'YYYY-MM'), %s)""",
            (float(row['total_amount']), user_id)
        )
    
    return {"success": True}

def get_friend_transactions(user_id: int, type_: str, month: str = None) -> list:
    """Get all friend transactions of a given type."""
    query = """
        SELECT ft.*, f.name as friend_name
        FROM friend_transactions ft
        JOIN friends f ON ft.friend_id = f.id
        WHERE ft.user_id = %s AND ft.type = %s
    """
    params = [user_id, type_]
    if month:
        query += " AND ft.month = %s"
        params.append(month)
    query += " ORDER BY ft.status ASC, ft.date DESC"
    rows = execute_query(query, params, fetch='all')
    return [dict(r) for r in rows] if rows else []

def get_friend_totals(user_id: int, month: str = None) -> dict:
    """Get total amounts owed and to receive."""
    base = "SELECT COALESCE(SUM(remaining_amount), 0) as total FROM friend_transactions WHERE user_id = %s AND type = %s AND status = 'pending'"
    params_pay = [user_id, 'pay']
    params_recv = [user_id, 'receive']
    if month:
        base += " AND month = %s"
        params_pay.append(month)
        params_recv.append(month)

    pay_row = execute_query(base, params_pay, fetch='one')
    recv_row = execute_query(base, params_recv, fetch='one')

    return {
        "total_to_pay": float(pay_row['total']),
        "total_to_receive": float(recv_row['total'])
    }

def update_friend_transaction(user_id: int, transaction_id: int, total_amount: float = None, description: str = None) -> dict:
    """Update a friend transaction."""
    row = execute_query("SELECT * FROM friend_transactions WHERE user_id = %s AND id = %s", (user_id, transaction_id), fetch='one')
    if not row:
        return {"success": False, "error": "Not found"}

    new_total = total_amount if total_amount is not None else float(row['total_amount'])
    new_desc = description if description is not None else row['description']
    paid = float(row['paid_amount'])
    new_status = 'completed' if paid >= new_total else 'pending'

    execute_query(
        "UPDATE friend_transactions SET total_amount = %s, description = %s, status = %s WHERE user_id = %s AND id = %s",
        (new_total, new_desc, new_status, user_id, transaction_id)
    )
    return {"success": True}

def delete_friend_transaction(user_id: int, transaction_id: int) -> dict:
    execute_query("DELETE FROM friend_transactions WHERE user_id = %s AND id = %s", (user_id, transaction_id))
    return {"success": True}

def get_all_friends(user_id: int) -> list:
    rows = execute_query("SELECT * FROM friends WHERE user_id = %s ORDER BY name", (user_id,), fetch='all')
    return [dict(r) for r in rows] if rows else []
