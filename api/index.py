from flask import Flask, render_template, request, jsonify, session, redirect
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from supabase import create_client, Client

# ========== SUPABASE ==========
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ SUPABASE_URL e SUPABASE_KEY são OBRIGATÓRIOS!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(f"✅ Conectado ao Supabase: {SUPABASE_URL}")

# ========== FLASK ==========
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'sua-chave-secreta-aqui')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# ========== FUNÇÕES ==========
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(email):
    random_part = secrets.token_hex(3).upper()
    return f"{email[:5]}{random_part}".replace('@', '_').replace('.', '_')

def get_user_by_email(email):
    try:
        result = supabase.table('users').select('*').eq('email', email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro: {e}")
        return None

def get_user_by_id(user_id):
    try:
        result = supabase.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro: {e}")
        return None

def create_user(email, password):
    try:
        password_hash = hash_password(password)
        result = supabase.table('users').insert({
            'email': email,
            'password_hash': password_hash
        }).execute()
        if result.data:
            return {'id': result.data[0]['id'], 'email': result.data[0]['email']}
        return None
    except Exception as e:
        print(f"Erro: {e}")
        return None

def update_user_token(user_id, token):
    try:
        supabase.table('users').update({'token': token}).eq('id', user_id).execute()
    except Exception as e:
        print(f"Erro: {e}")

# ========== ROTAS ==========

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
    return render_template('dashboard/index.html', user_email=user['email'])

@app.route('/login')
def login_page():
    return render_template('auth/login.html')

@app.route('/register')
def register_page():
    return render_template('auth/register.html')

@app.route('/settings')
def settings_page():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard/settings.html', user_email=session.get('user_email', ''))

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

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'success', 'message': 'Logout realizado'})

# Handler para Vercel
def handler(request, context):
    return app(request, context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)