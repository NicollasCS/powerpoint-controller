import os
from dotenv import load_dotenv

load_dotenv()

# ========== SUPABASE ==========
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ SUPABASE_URL e SUPABASE_KEY são OBRIGATÓRIOS!")

# ========== EMAIL ==========
EMAIL_USER = os.environ.get('EMAIL_USER', 'nicollascane@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

# ========== FLASK ==========
SECRET_KEY = os.environ.get('SECRET_KEY', 'sua-chave-secreta-aqui')