# backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify, session
from backend.services.auth_service import (
    is_first_launch, register, login,
    get_security_question, reset_password, change_password
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/status', methods=['GET'])
def status():
    return jsonify({
        "first_launch": is_first_launch(),
        "authenticated": session.get('authenticated', False),
        "username": session.get('username', '')
    })

@auth_bp.route('/register', methods=['POST'])
def do_register():
    if not is_first_launch():
        return jsonify({"success": False, "error": "Account already exists"}), 400
    d = request.get_json()
    result = register(
        d.get('username', ''),
        d.get('password', ''),
        d.get('security_question', ''),
        d.get('security_answer', '')
    )
    if result['success']:
        session['authenticated'] = True
        session['username'] = d.get('username', '').strip().lower()
    return jsonify(result), 201 if result['success'] else 400

@auth_bp.route('/login', methods=['POST'])
def do_login():
    d = request.get_json()
    result = login(d.get('username', ''), d.get('password', ''))
    if result['success']:
        session['authenticated'] = True
        session['username'] = result['username']
    return jsonify(result), 200 if result['success'] else 401

@auth_bp.route('/logout', methods=['POST'])
def do_logout():
    session.clear()
    return jsonify({"success": True})

@auth_bp.route('/security-question', methods=['POST'])
def fetch_security_question():
    d = request.get_json()
    return jsonify(get_security_question(d.get('username', '')))

@auth_bp.route('/reset-password', methods=['POST'])
def do_reset():
    d = request.get_json()
    result = reset_password(
        d.get('username', ''),
        d.get('security_answer', ''),
        d.get('new_password', '')
    )
    return jsonify(result)

@auth_bp.route('/change-password', methods=['POST'])
def do_change():
    if not session.get('authenticated'):
        return jsonify({"error": "Unauthorized"}), 401
    d = request.get_json()
    result = change_password(
        session.get('username', ''),
        d.get('old_password', ''),
        d.get('new_password', '')
    )
    return jsonify(result)
