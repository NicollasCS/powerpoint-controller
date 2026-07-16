from flask import render_template, request, jsonify, session, redirect, url_for
from app import app
from app.database import *
from app.utils import send_reset_email, generate_verification_code, send_verification_email
from datetime import datetime, timedelta
from app.database import USE_SUPABASE
import secrets

# ========== ROTAS DE AUTENTICAÇÃO ==========

@app.route('/login')
def login_page():
    return render_template('auth/login.html')

@app.route('/register')
def register_page():
    return render_template('auth/register.html')

@app.route('/recover')
def recover_page():
    return render_template('auth/recover.html')

@app.route('/reset_password')
def reset_password_page():
    token = request.args.get('token')
    if not token:
        return "Token inválido", 400
    return render_template('auth/reset_password.html', token=token)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
    return render_template('dashboard/index.html', user_email=user['email'])

@app.route('/settings')
def settings_page():
    if 'user_id' not in session:
        return redirect('/login')
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
    return render_template('dashboard/settings.html', user_email=user['email'])

@app.route('/controle')
def controle_page():
    return render_template('controle.html')

# ========== API DE AUTENTICAÇÃO ==========

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    user = get_user_by_email(email)
    if user:
        return jsonify({'error': f'O email {email} já está cadastrado. Caso seja um engano, entre em contato com o suporte: nicollascane@gmail.com'}), 400

    result = create_user(email, password)
    if result:
        return jsonify({'status': 'success', 'message': 'Usuário criado com sucesso!'})
    return jsonify({'error': 'Erro ao criar usuário'}), 500

@app.route('/api/login', methods=['POST'])
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

    return jsonify({'status': 'success', 'message': 'Login realizado!', 'token': token})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'success', 'message': 'Logout realizado'})

@app.route('/api/recover', methods=['POST'])
def api_recover():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email é obrigatório'}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Email não encontrado'}), 404

    reset_token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(hours=1)).isoformat()

    update_reset_token(email, reset_token, expires_at)

    if send_reset_email(email, reset_token):
        return jsonify({'status': 'success', 'message': 'Email de recuperação enviado!'})
    return jsonify({'error': 'Erro ao enviar email'}), 500

@app.route('/api/reset_password', methods=['POST'])
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

    update_user_password(user['id'], new_password)
    clear_reset_token(user['id'])

    return jsonify({'status': 'success', 'message': 'Senha redefinida com sucesso!'})

# ========== API DE CONTA ==========

@app.route('/api/change_password', methods=['POST'])
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

    update_user_password(session['user_id'], new_password)

    return jsonify({'status': 'success', 'message': 'Senha alterada com sucesso!'})

@app.route('/api/delete_account', methods=['POST'])
def api_delete_account():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    delete_user(session['user_id'])
    session.clear()

    return jsonify({'status': 'success', 'message': 'Conta excluída com sucesso!'})

# ========== TROCAR EMAIL (COM VERIFICAÇÃO) ==========

@app.route('/api/send_old_email_code', methods=['POST'])
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

@app.route('/api/verify_old_email_code', methods=['POST'])
def verify_old_email_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.json
    code = data.get('code')
    new_email = data.get('new_email')
    
    if not code or not new_email:
        return jsonify({'error': 'Código e novo email são obrigatórios'}), 400
    
    user = get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    if not verify_code(user['email'], code):
        return jsonify({'error': 'Código inválido ou expirado'}), 400
    
    existing_user = get_user_by_email(new_email)
    if existing_user:
        return jsonify({'error': 'Este email já está em uso'}), 400
    
    session['temp_new_email'] = new_email
    
    return jsonify({
        'status': 'success', 
        'message': 'Código verificado! Agora confirme o novo email.',
        'requires_new_email_verification': True
    })

@app.route('/api/send_new_email_code', methods=['POST'])
def send_new_email_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    new_email = session.get('temp_new_email')
    if not new_email:
        return jsonify({'error': 'Nenhum novo email definido'}), 400
    
    code = generate_verification_code()
    expires_at = (datetime.now() + timedelta(minutes=5)).isoformat()
    
    save_verification_code(new_email, code, expires_at)
    
    if send_verification_email(new_email, code, "confirmação de novo email"):
        return jsonify({'status': 'success', 'message': f'Código enviado para {new_email}!'})
    return jsonify({'error': 'Erro ao enviar email'}), 500

@app.route('/api/verify_new_email_code', methods=['POST'])
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