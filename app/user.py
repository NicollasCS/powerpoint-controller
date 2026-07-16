from flask import render_template, request, jsonify, session, Blueprint, redirect
from app.database import get_user_by_id, get_user_by_email, update_user_email, update_user_password, delete_user, save_verification_code, verify_code
from app.utils import hash_password, generate_verification_code
from app.email import send_verification_email
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
    
    # Detecta se é celular
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone'])
    
    if is_mobile:
        return redirect('/controle')
    
    return render_template('dashboard/index.html', user_email=user['email'])

@user_bp.route('/settings')
def settings_page():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard/settings.html', user_email=session.get('user_email', ''))

@user_bp.route('/api/send_old_email_code', methods=['POST'])
def send_old_email_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user = get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    code = generate_verification_code()
    expires_at = (datetime.now() + timedelta(minutes=5)).isoformat()
    
    save_verification_code(user['email'], code, expires_at)
    
    if send_verification_email(user['email'], code, "verificação"):
        return jsonify({'status': 'success', 'message': 'Código enviado para seu email!'})
    return jsonify({'error': 'Erro ao enviar email'}), 500

@user_bp.route('/api/verify_old_email_code', methods=['POST'])
def verify_old_email_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'Código é obrigatório'}), 400
    
    user = get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    if not verify_code(user['email'], code):
        return jsonify({'error': 'Código inválido ou expirado'}), 400
    
    return jsonify({
        'status': 'success', 
        'message': 'Código verificado! Agora digite o novo email.'
    })

@user_bp.route('/api/send_new_email_code', methods=['POST'])
def send_new_email_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.json
    new_email = data.get('new_email')
    
    if not new_email:
        return jsonify({'error': 'Novo email é obrigatório'}), 400
    
    existing_user = get_user_by_email(new_email)
    if existing_user:
        return jsonify({'error': 'Este email já está em uso'}), 400
    
    session['temp_new_email'] = new_email
    
    code = generate_verification_code()
    expires_at = (datetime.now() + timedelta(minutes=5)).isoformat()
    
    save_verification_code(new_email, code, expires_at)
    
    if send_verification_email(new_email, code, "confirmação de novo email"):
        return jsonify({'status': 'success', 'message': f'Código enviado para {new_email}!'})
    return jsonify({'error': 'Erro ao enviar email'}), 500

@user_bp.route('/api/verify_new_email_code', methods=['POST'])
def verify_new_email_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'Código é obrigatório'}), 400
    
    new_email = session.get('temp_new_email')
    if not new_email:
        return jsonify({'error': 'Nenhum novo email definido'}), 400
    
    if not verify_code(new_email, code):
        return jsonify({'error': 'Código inválido ou expirado'}), 400
    
    update_user_email(session['user_id'], new_email)
    session['user_email'] = new_email
    session.pop('temp_new_email', None)
    
    return jsonify({'status': 'success', 'message': 'Email alterado com sucesso!'})

@user_bp.route('/api/change_password', methods=['POST'])
def api_change_password():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400

    user = get_user_by_id(session['user_id'])
    current_hash = hash_password(current_password)

    if user['password_hash'] != current_hash:
        return jsonify({'error': 'Senha atual incorreta'}), 400

    new_hash = hash_password(new_password)
    update_user_password(session['user_id'], new_hash)

    return jsonify({'status': 'success', 'message': 'Senha alterada com sucesso!'})

@user_bp.route('/api/delete_account', methods=['POST'])
def api_delete_account():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    delete_user(session['user_id'])
    session.clear()

    return jsonify({'status': 'success', 'message': 'Conta excluída com sucesso!'})