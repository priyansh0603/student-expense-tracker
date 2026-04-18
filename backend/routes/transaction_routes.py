# backend/routes/transaction_routes.py
from flask import Blueprint, request, jsonify, session
from backend.services.transaction_service import (
    add_transaction, get_transactions, get_dashboard_data, delete_transaction
)

tx_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

def require_auth():
    if not session.get('authenticated'):
        return jsonify({"error": "Unauthorized"}), 401
    return None

@tx_bp.route('/dashboard', methods=['GET'])
def dashboard():
    auth = require_auth()
    if auth: return auth
    month = request.args.get('month')
    user_id = session.get('user_id')
    return jsonify(get_dashboard_data(user_id, month))

@tx_bp.route('/', methods=['GET'])
def list_transactions():
    auth = require_auth()
    if auth: return auth
    month = request.args.get('month')
    limit = request.args.get('limit', type=int)
    user_id = session.get('user_id')
    return jsonify(get_transactions(user_id, month, limit))

@tx_bp.route('/', methods=['POST'])
def create_transaction():
    auth = require_auth()
    if auth: return auth
    data = request.get_json()

    # Validate
    if not data.get('amount') or float(data['amount']) <= 0:
        return jsonify({"success": False, "error": "Invalid amount"}), 400
    if data.get('type') not in ['income', 'expense']:
        return jsonify({"success": False, "error": "Type must be income or expense"}), 400

    user_id = session.get('user_id')
    result = add_transaction(
        type_=data['type'],
        amount=float(data['amount']),
        category=data.get('category', 'Other'),
        description=data.get('description', ''),
        user_id=user_id,
        trans_date=data.get('date')
    )
    return jsonify(result), 201

@tx_bp.route('/<int:transaction_id>', methods=['DELETE'])
def remove_transaction(transaction_id):
    auth = require_auth()
    if auth: return auth
    user_id = session.get('user_id')
    return jsonify(delete_transaction(user_id, transaction_id))
