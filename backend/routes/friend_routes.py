# backend/routes/friend_routes.py
from flask import Blueprint, request, jsonify, session
from backend.services.friend_service import (
    add_friend_transaction, add_payment, mark_completed,
    get_friend_transactions, get_friend_totals, update_friend_transaction,
    delete_friend_transaction, get_all_friends
)

friend_bp = Blueprint('friends', __name__, url_prefix='/api/friends')

def require_auth():
    if not session.get('authenticated'):
        return jsonify({"error": "Unauthorized"}), 401
    return None

@friend_bp.route('/', methods=['GET'])
def list_friends():
    auth = require_auth()
    if auth: return auth
    user_id = session.get('user_id')
    return jsonify(get_all_friends(user_id))

@friend_bp.route('/receive', methods=['GET'])
def get_receive():
    auth = require_auth()
    if auth: return auth
    month = request.args.get('month')
    user_id = session.get('user_id')
    data = get_friend_transactions(user_id, 'receive', month)
    totals = get_friend_totals(user_id, month)
    return jsonify({"transactions": data, "total_to_receive": totals['total_to_receive']})

@friend_bp.route('/pay', methods=['GET'])
def get_pay():
    auth = require_auth()
    if auth: return auth
    month = request.args.get('month')
    user_id = session.get('user_id')
    data = get_friend_transactions(user_id, 'pay', month)
    totals = get_friend_totals(user_id, month)
    return jsonify({"transactions": data, "total_to_pay": totals['total_to_pay']})

@friend_bp.route('/', methods=['POST'])
def create_friend_transaction():
    auth = require_auth()
    if auth: return auth
    data = request.get_json()

    if not data.get('friend_name', '').strip():
        return jsonify({"success": False, "error": "Friend name required"}), 400
    if not data.get('amount') or float(data['amount']) <= 0:
        return jsonify({"success": False, "error": "Invalid amount"}), 400
    if data.get('type') not in ['pay', 'receive']:
        return jsonify({"success": False, "error": "Type must be pay or receive"}), 400

    user_id = session.get('user_id')
    result = add_friend_transaction(
        user_id=user_id,
        friend_name=data['friend_name'].strip(),
        amount=float(data['amount']),
        type_=data['type'],
        description=data.get('description', ''),
        trans_date=data.get('date')
    )
    return jsonify(result), 201

@friend_bp.route('/<int:transaction_id>/payment', methods=['POST'])
def add_payment_route(transaction_id):
    auth = require_auth()
    if auth: return auth
    data = request.get_json()
    amount = float(data.get('amount', 0))
    if amount <= 0:
        return jsonify({"success": False, "error": "Invalid payment amount"}), 400
    user_id = session.get('user_id')
    return jsonify(add_payment(user_id, transaction_id, amount))

@friend_bp.route('/<int:transaction_id>/complete', methods=['POST'])
def complete_transaction(transaction_id):
    auth = require_auth()
    if auth: return auth
    user_id = session.get('user_id')
    return jsonify(mark_completed(user_id, transaction_id))

@friend_bp.route('/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    auth = require_auth()
    if auth: return auth
    data = request.get_json()
    total = float(data['total_amount']) if 'total_amount' in data else None
    user_id = session.get('user_id')
    return jsonify(update_friend_transaction(user_id, transaction_id, total, data.get('description')))

@friend_bp.route('/<int:transaction_id>', methods=['DELETE'])
def remove_transaction(transaction_id):
    auth = require_auth()
    if auth: return auth
    user_id = session.get('user_id')
    return jsonify(delete_friend_transaction(user_id, transaction_id))
