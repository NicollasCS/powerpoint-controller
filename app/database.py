from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(f"✅ Conectado ao Supabase: {SUPABASE_URL}")

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
    
def get_user_by_token(token):
    try:
        result = supabase.table('users').select('*').eq('token', token).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro: {e}")
        return None

def create_user(email, password_hash):
    try:
        result = supabase.table('users').insert({
            'email': email,
            'password_hash': password_hash
        }).execute()
        if result.data:
            return {'id': result.data[0]['id'], 'email': result.data[0]['email']}
        return None
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return None

def update_user_token(user_id, token):
    try:
        supabase.table('users').update({'token': token}).eq('id', user_id).execute()
    except Exception as e:
        print(f"Erro ao atualizar token: {e}")

def update_user_email(user_id, new_email):
    try:
        supabase.table('users').update({'email': new_email}).eq('id', user_id).execute()
    except Exception as e:
        print(f"Erro ao atualizar email: {e}")

def update_user_password(user_id, password_hash):
    try:
        supabase.table('users').update({'password_hash': password_hash}).eq('id', user_id).execute()
    except Exception as e:
        print(f"Erro ao atualizar senha: {e}")

def update_reset_token(email, reset_token, expires_at):
    try:
        supabase.table('users').update({
            'reset_token': reset_token,
            'reset_token_expires': expires_at
        }).eq('email', email).execute()
    except Exception as e:
        print(f"Erro ao salvar token: {e}")

def get_user_by_reset_token(token):
    try:
        result = supabase.table('users').select('*').eq('reset_token', token).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro: {e}")
        return None

def delete_user(user_id):
    try:
        supabase.table('users').delete().eq('id', user_id).execute()
    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")

def save_verification_code(email, code, expires_at):
    try:
        supabase.table('verification_codes').delete().eq('email', email).execute()
        supabase.table('verification_codes').insert({
            'email': email,
            'code': code,
            'expires_at': expires_at
        }).execute()
    except Exception as e:
        print(f"Erro ao salvar código: {e}")

def verify_code(email, code):
    try:
        result = supabase.table('verification_codes').select('*').eq('email', email).eq('code', code).execute()
        if result.data:
            supabase.table('verification_codes').delete().eq('email', email).eq('code', code).execute()
            return True
        return False
    except Exception as e:
        print(f"Erro ao verificar código: {e}")
        return False