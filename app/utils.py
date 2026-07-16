import hashlib
import secrets
import string
import base64
import io
import os
from datetime import datetime, timedelta
from PIL import Image
from pdf2image import convert_from_bytes

# ========== FUNÇÕES DE HASH E TOKEN ==========

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(email):
    random_part = secrets.token_hex(3).upper()
    return f"{email[:5]}{random_part}".replace('@', '_').replace('.', '_')

def generate_verification_code():
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def generate_reset_token():
    return secrets.token_urlsafe(32)

# ========== CONVERSÃO DE PDF ==========

# Configuração do Poppler
POPPLER_PATHS = [
    r"C:\poppler\Library\bin",
    r"C:\poppler\bin",
    r"C:\Program Files\poppler\bin",
]

POPPLER_PATH = None
for path in POPPLER_PATHS:
    if os.path.exists(path):
        POPPLER_PATH = path
        break

def convert_pdf_to_images(pdf_bytes):
    """Converte PDF para imagens base64"""
    images_data = []
    
    try:
        if POPPLER_PATH:
            images = convert_from_bytes(pdf_bytes, dpi=150, fmt='png', poppler_path=POPPLER_PATH)
        else:
            images = convert_from_bytes(pdf_bytes, dpi=150, fmt='png')
        
        for img in images:
            img.thumbnail((1200, 800))
            buffered = io.BytesIO()
            img.save(buffered, format="PNG", quality=85)
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            images_data.append(f"data:image/png;base64,{img_base64}")
        
        return images_data, len(images_data)
    except Exception as e:
        print(f"Erro ao converter PDF: {e}")
        return [], 0