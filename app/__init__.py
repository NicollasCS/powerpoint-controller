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

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SLIDES_FOLDER'] = 'slides_images'

# Cria pastas necessárias
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SLIDES_FOLDER'], exist_ok=True)

# Importa as rotas
from app import auth, slides, main