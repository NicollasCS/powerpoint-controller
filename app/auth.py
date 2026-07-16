from flask import render_template, request, jsonify, session, redirect, Blueprint
from app.database import get_user_by_email, create_user, update_user_token, get_user_by_reset_token, update_reset_token, update_user_password
from app.utils import hash_password, generate_token, generate_reset_token
from app.email import send_reset_email
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_page():
    return render_template('auth/login.html')

@auth_bp.route('/register')
def register_page():
    return render_template('auth/register.html')

@auth_bp.route('/recover')
def recover_page():
    return render_template('auth/recover.html')

@auth_bp.route('/reset_password')
def reset_password_page():
    token = request.args.get('token')
    if not token:
        return "Token inválido", 400
    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Email ou senha incorretos'}), 401

    password_hash = hash_password(password)
    if user['password_hash'] != password_hash:
        return jsonify({'error': 'Email ou senha incorretos'}), 401

    session['user_id'] = user['id']
    session['user_email'] = user['email']
    token = generate_token(user['email'])
    update_user_token(user['id'], token)

    return jsonify({'status': 'success', 'message': 'Login realizado!', 'token': token, 'redirect': '/'})

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    user = get_user_by_email(email)
    if user:
        return jsonify({'error': f'O email {email} já está cadastrado. Caso seja um engano, entre em contato com o suporte: nicollascane@gmail.com'}), 400

    password_hash = hash_password(password)
    result = create_user(email, password_hash)
    if result:
        return jsonify({'status': 'success', 'message': 'Usuário criado com sucesso!'})
    return jsonify({'error': 'Erro ao criar usuário'}), 500

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'success', 'message': 'Logout realizado'})

@auth_bp.route('/api/recover', methods=['POST'])
def api_recover():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email é obrigatório'}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Email não encontrado'}), 404

    reset_token = generate_reset_token()
    expires_at = (datetime.now() + timedelta(hours=1)).isoformat()

    update_reset_token(email, reset_token, expires_at)

    if send_reset_email(email, reset_token):
        return jsonify({'status': 'success', 'message': 'Email de recuperação enviado!'})
    return jsonify({'error': 'Erro ao enviar email'}), 500

@auth_bp.route('/api/reset_password', methods=['POST'])
def api_reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({'error': 'Token e nova senha são obrigatórios'}), 400

    user = get_user_by_reset_token(token)
    if not user:
        return jsonify({'error': 'Token inválido'}), 400

    expires_at = datetime.fromisoformat(user['reset_token_expires'])
    if datetime.now() > expires_at:
        return jsonify({'error': 'Token expirado'}), 400

    password_hash = hash_password(new_password)
    update_user_password(user['id'], password_hash)

    # Limpa o token
    update_reset_token(user['email'], None, None)

    return jsonify({'status': 'success', 'message': 'Senha redefinida com sucesso!'})