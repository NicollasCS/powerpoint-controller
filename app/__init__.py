from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

app.secret_key = os.environ.get('SECRET_KEY', 'sua-chave-secreta-aqui')

# ========== CONFIGURAÇÕES ==========
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# 🔧 CORREÇÃO: Usar /tmp no Vercel
if os.environ.get('ENV') == 'production':
    # Vercel - usa /tmp
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    app.config['SLIDES_FOLDER'] = '/tmp/slides_images'
else:
    # Local - usa pastas normais
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['SLIDES_FOLDER'] = 'slides_images'

# Cria pastas necessárias (se for local)
if not os.environ.get('ENV') == 'production':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SLIDES_FOLDER'], exist_ok=True)
else:
    # No Vercel, cria as pastas no /tmp
    os.makedirs('/tmp/uploads', exist_ok=True)
    os.makedirs('/tmp/slides_images', exist_ok=True)

# Importa as rotas
from app import auth, slides