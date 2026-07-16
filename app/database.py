import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta

# ========== CONFIGURAÇÃO DO AMBIENTE ==========
ENV = os.environ.get('ENV', 'development')

# 🔧 FORÇA O USO DO SUPABASE EM PRODUÇÃO
if ENV == 'production':
    USE_SUPABASE = True
else:
    USE_SUPABASE = os.environ.get('SUPABASE_URL') and os.environ.get('SUPABASE_KEY')

print(f"🔧 Ambiente: {ENV}")
print(f"🔧 Usando Supabase: {USE_SUPABASE}")

# ========== SUPABASE (PRODUÇÃO) ==========
if USE_SUPABASE:
    try:
        from supabase import create_client, Client
        SUPABASE_URL = os.environ.get('SUPABASE_URL')
        SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("❌ ERRO: SUPABASE_URL ou SUPABASE_KEY não configurados!")
            print("   Verifique as variáveis de ambiente no Vercel.")
            USE_SUPABASE = False
        else:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print(f"✅ Conectado ao Supabase: {SUPABASE_URL}")
            
            # Testa a conexão
            try:
                test = supabase.table('users').select('*').limit(1).execute()
                print("✅ Conexão com Supabase verificada!")
            except Exception as e:
                print(f"❌ Erro ao testar conexão: {e}")
                USE_SUPABASE = False
                
    except Exception as e:
        print(f"❌ Erro ao iniciar Supabase: {e}")
        USE_SUPABASE = False
        print("⚠️ Usando SQLite como fallback")

# ========== SQLITE (APENAS LOCAL) ==========
DB_NAME = 'apresenta.db'

def get_db():
    """Retorna uma conexão com o banco de dados SQLite (apenas local)"""
    if ENV == 'production':
        raise Exception("❌ SQLite não suportado em produção! Use Supabase.")
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria as tabelas SQLite se não existirem (apenas local)"""
    if USE_SUPABASE:
        print("ℹ️ Supabase: tabelas criadas manualmente no dashboard")
        return
    
    if ENV == 'production':
        print("❌ Não é possível criar SQLite em produção!")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            token TEXT UNIQUE,
            reset_token TEXT,
            reset_token_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Tabelas SQLite criadas")

# ========== FUNÇÕES HÍBRIDAS ==========

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(email):
    random_part = secrets.token_hex(3).upper()
    return f"{email[:5]}{random_part}".replace('@', '_').replace('.', '_')

# ========== USUÁRIOS - SQLITE ==========

def create_user_sqlite(email, password):
    conn = get_db()
    cursor = conn.cursor()
    try:
        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (email, password_hash) VALUES (?, ?)',
            (email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {'id': user_id, 'email': email}
    except sqlite3.IntegrityError:
        conn.close()
        return None

def create_user_supabase(email, password):
    try:
        password_hash = hash_password(password)
        data = {
            'email': email,
            'password_hash': password_hash
        }
        result = supabase.table('users').insert(data).execute()
        if result.data:
            return {'id': result.data[0]['id'], 'email': result.data[0]['email']}
        return None
    except Exception as e:
        print(f"Erro Supabase: {e}")
        return None

def create_user(email, password):
    if USE_SUPABASE:
        return create_user_supabase(email, password)
    return create_user_sqlite(email, password)

# ========== BUSCAR USUÁRIO ==========

def get_user_by_email_sqlite(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_email_supabase(email):
    try:
        result = supabase.table('users').select('*').eq('email', email).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Erro Supabase: {e}")
        return None

def get_user_by_email(email):
    if USE_SUPABASE:
        return get_user_by_email_supabase(email)
    return get_user_by_email_sqlite(email)

# ========== OUTRAS FUNÇÕES ==========

def get_user_by_id_sqlite(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id_supabase(user_id):
    try:
        result = supabase.table('users').select('*').eq('id', user_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Erro Supabase: {e}")
        return None

def get_user_by_id(user_id):
    if USE_SUPABASE:
        return get_user_by_id_supabase(user_id)
    return get_user_by_id_sqlite(user_id)

def get_user_by_token_sqlite(token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE token = ?', (token,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_token_supabase(token):
    try:
        result = supabase.table('users').select('*').eq('token', token).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Erro Supabase: {e}")
        return None

def get_user_by_token(token):
    if USE_SUPABASE:
        return get_user_by_token_supabase(token)
    return get_user_by_token_sqlite(token)

# ========== ATUALIZAR USUÁRIO ==========

def update_user_token_sqlite(user_id, token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET token = ? WHERE id = ?', (token, user_id))
    conn.commit()
    conn.close()

def update_user_token_supabase(user_id, token):
    try:
        supabase.table('users').update({'token': token}).eq('id', user_id).execute()
    except Exception as e:
        print(f"Erro Supabase: {e}")

def update_user_token(user_id, token):
    if USE_SUPABASE:
        update_user_token_supabase(user_id, token)
    else:
        update_user_token_sqlite(user_id, token)

# ========== ETC ==========

def get_user_by_reset_token(token):
    if USE_SUPABASE:
        try:
            result = supabase.table('users').select('*').eq('reset_token', token).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Erro Supabase: {e}")
            return None
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE reset_token = ?', (token,))
        user = cursor.fetchone()
        conn.close()
        return user

def update_user_email(user_id, new_email):
    if USE_SUPABASE:
        try:
            supabase.table('users').update({'email': new_email}).eq('id', user_id).execute()
        except Exception as e:
            print(f"Erro Supabase: {e}")
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET email = ? WHERE id = ?', (new_email, user_id))
        conn.commit()
        conn.close()

def update_user_password(user_id, new_password):
    password_hash = hash_password(new_password)
    if USE_SUPABASE:
        try:
            supabase.table('users').update({'password_hash': password_hash}).eq('id', user_id).execute()
        except Exception as e:
            print(f"Erro Supabase: {e}")
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        conn.commit()
        conn.close()

def update_reset_token(email, reset_token, expires_at):
    if USE_SUPABASE:
        try:
            supabase.table('users').update({
                'reset_token': reset_token,
                'reset_token_expires': expires_at
            }).eq('email', email).execute()
        except Exception as e:
            print(f"Erro Supabase: {e}")
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET reset_token = ?, reset_token_expires = ? WHERE email = ?',
            (reset_token, expires_at, email)
        )
        conn.commit()
        conn.close()

def clear_reset_token(user_id):
    if USE_SUPABASE:
        try:
            supabase.table('users').update({
                'reset_token': None,
                'reset_token_expires': None
            }).eq('id', user_id).execute()
        except Exception as e:
            print(f"Erro Supabase: {e}")
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET reset_token = NULL, reset_token_expires = NULL WHERE id = ?',
            (user_id,)
        )
        conn.commit()
        conn.close()

def delete_user(user_id):
    if USE_SUPABASE:
        try:
            supabase.table('users').delete().eq('id', user_id).execute()
        except Exception as e:
            print(f"Erro Supabase: {e}")
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

# ========== CÓDIGOS DE VERIFICAÇÃO ==========

def save_verification_code(email, code, expires_at):
    if USE_SUPABASE:
        try:
            supabase.table('verification_codes').delete().eq('email', email).execute()
            supabase.table('verification_codes').insert({
                'email': email,
                'code': code,
                'expires_at': expires_at
            }).execute()
        except Exception as e:
            print(f"Erro Supabase: {e}")
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM verification_codes WHERE email = ?', (email,))
        cursor.execute(
            'INSERT INTO verification_codes (email, code, expires_at) VALUES (?, ?, ?)',
            (email, code, expires_at)
        )
        conn.commit()
        conn.close()

def verify_code(email, code):
    if USE_SUPABASE:
        try:
            result = supabase.table('verification_codes').select('*').eq('email', email).eq('code', code).execute()
            if result.data:
                supabase.table('verification_codes').delete().eq('email', email).eq('code', code).execute()
                return True
            return False
        except Exception as e:
            print(f"Erro Supabase: {e}")
            return False
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM verification_codes 
            WHERE email = ? AND code = ? AND expires_at > datetime('now')
            ORDER BY created_at DESC LIMIT 1
        ''', (email, code))
        result = cursor.fetchone()
        conn.close()
        if result:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM verification_codes WHERE email = ? AND code = ?', (email, code))
            conn.commit()
            conn.close()
            return True
        return False

# Só inicializa o SQLite se NÃO estiver em produção
if ENV != 'production' and not USE_SUPABASE:
    init_db()
elif ENV == 'production' and not USE_SUPABASE:
    print("❌ ERRO: Em produção, você PRECISA usar Supabase!")
    print("   Verifique as variáveis SUPABASE_URL e SUPABASE_KEY")