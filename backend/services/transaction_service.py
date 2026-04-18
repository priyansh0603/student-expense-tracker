# backend/services/transaction_service.py
from datetime import date, datetime
import calendar
from backend.models.db import execute_query

def get_current_month() -> str:
    return datetime.now().strftime("%Y-%m")

def add_transaction(type_: str, amount: float, category: str, description: str, trans_date: str = None) -> dict:
    """Add an income or expense transaction."""
    if trans_date:
        d = datetime.strptime(trans_date, "%Y-%m-%d").date()
    else:
        d = date.today()
    month = d.strftime("%Y-%m")
    row = execute_query(
        """INSERT INTO transactions (type, amount, category, description, date, month)
           VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
        (type_, amount, category, description, d, month),
        fetch='one'
    )
    return {"success": True, "id": row['id']}

def get_transactions(month: str = None, limit: int = None) -> list:
    """Get transactions, optionally filtered by month."""
    if not month:
        month = get_current_month()
    query = "SELECT * FROM transactions WHERE month = %s ORDER BY date DESC, created_at DESC"
    params = [month]
    if limit:
        query += f" LIMIT {int(limit)}"
    rows = execute_query(query, params, fetch='all')
    return [dict(r) for r in rows] if rows else []

def get_dashboard_data(month: str = None) -> dict:
    """Get all dashboard calculations."""
    if not month:
        month = get_current_month()

    # Income & Expenses
    income_row = execute_query(
        "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type='income' AND month=%s",
        (month,), fetch='one'
    )
    expense_row = execute_query(
        "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type='expense' AND month=%s",
        (month,), fetch='one'
    )

    total_income = float(income_row['total'])
    total_expense = float(expense_row['total'])
    balance = total_income - total_expense

    # Category breakdown
    cat_rows = execute_query(
        """SELECT category, COALESCE(SUM(amount), 0) as total
           FROM transactions WHERE type='expense' AND month=%s
           GROUP BY category""",
        (month,), fetch='all'
    )
    categories = {r['category']: float(r['total']) for r in cat_rows} if cat_rows else {}

    # Days left calculation
    today = date.today()
    year, mon = map(int, month.split("-"))
    days_in_month = calendar.monthrange(year, mon)[1]
    last_day = date(year, mon, days_in_month)

    if today.year == year and today.month == mon:
        days_left = (last_day - today).days + 1
    elif today > last_day:
        days_left = 0
    else:
        days_left = days_in_month

    safe_daily = round(balance / days_left, 2) if days_left > 0 and balance > 0 else 0

    # Recent transactions
    recent = get_transactions(month, limit=8)

    # Friend totals
    from backend.services.friend_service import get_friend_totals
    friend_totals = get_friend_totals(month)

    return {
        "month": month,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "days_left": days_left,
        "safe_daily_spend": safe_daily,
        "categories": categories,
        "recent_transactions": recent,
        "friend_totals": friend_totals
    }

def delete_transaction(transaction_id: int) -> dict:
    execute_query("DELETE FROM transactions WHERE id = %s", (transaction_id,))
    return {"success": True}
