# backend/routes/backup_routes.py
from flask import Blueprint, request, jsonify, session
from backend.services.backup_service import create_backup, list_backups

backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')

def require_auth():
    if not session.get('authenticated'):
        return jsonify({"error": "Unauthorized"}), 401
    return None

@backup_bp.route('/', methods=['GET'])
def list_all_backups():
    auth = require_auth()
    if auth: return auth
    return jsonify(list_backups())

@backup_bp.route('/create', methods=['POST'])
def trigger_backup():
    auth = require_auth()
    if auth: return auth
    data = request.get_json() or {}
    month = data.get('month')
    return jsonify(create_backup(month))
