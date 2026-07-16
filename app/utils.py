import secrets
import string
import os
import base64
import io
from datetime import datetime, timedelta
from PIL import Image
from pdf2image import convert_from_bytes

# ========== POPPLER ==========
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

# ========== EMAIL ==========
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

def send_email(to_email, subject, body):
    """Envia email usando SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

def send_verification_email(to_email, code, purpose="verificação"):
    """Envia email com código de verificação"""
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                background: linear-gradient(135deg, #667eea, #764ba2); 
                color: white; 
                padding: 20px; 
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{ 
                background: #f8f9fa; 
                padding: 30px; 
                border-radius: 0 0 10px 10px;
                border: 1px solid #ddd;
                border-top: none;
            }}
            .code {{
                font-size: 32px;
                font-weight: bold;
                text-align: center;
                padding: 15px;
                background: #f0f0f0;
                border-radius: 8px;
                letter-spacing: 8px;
                color: #333;
                margin: 15px 0;
            }}
            .footer {{ margin-top: 20px; font-size: 12px; color: #888; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🔐 Código de {purpose}</h2>
            </div>
            <div class="content">
                <p>Olá! 😊</p>
                <p>Seu código de {purpose} é:</p>
                <div class="code">{code}</div>
                <p style="color: #666; font-size: 14px;">🔹 Este código é válido por <strong>5 minutos</strong>.</p>
                <p style="color: #666; font-size: 14px;">🔹 Se você não solicitou, ignore este email.</p>
            </div>
            <div class="footer">
                <p>© 2026 Apresenta - Todos os direitos reservados</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, f"🔐 Código de {purpose} - Apresenta", body)

def send_reset_email(to_email, reset_token):
    """Envia email de recuperação de senha"""
    reset_link = f"http://localhost:5000/reset_password?token={reset_token}"
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                background: linear-gradient(135deg, #667eea, #764ba2); 
                color: white; 
                padding: 20px; 
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{ 
                background: #f8f9fa; 
                padding: 30px; 
                border-radius: 0 0 10px 10px;
                border: 1px solid #ddd;
                border-top: none;
            }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                margin: 15px 0;
            }}
            .footer {{ margin-top: 20px; font-size: 12px; color: #888; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🔐 Recuperação de Senha</h2>
            </div>
            <div class="content">
                <p>Olá! 😊</p>
                <p>Recebemos uma solicitação para redefinir a senha da sua conta.</p>
                <p>Clique no botão abaixo para criar uma nova senha:</p>
                <div style="text-align: center;">
                    <a href="{reset_link}" class="btn">🔄 Redefinir Senha</a>
                </div>
                <p style="color: #666; font-size: 13px;">🔹 Este link é válido por <strong>1 hora</strong>.</p>
                <p style="color: #666; font-size: 13px;">🔹 Se você não solicitou, ignore este email.</p>
                <hr style="border: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 13px; color: #999;">
                    Link alternativo:<br>
                    <a href="{reset_link}" style="word-break: break-all; color: #667eea;">{reset_link}</a>
                </p>
            </div>
            <div class="footer">
                <p>© 2026 Apresenta - Todos os direitos reservados</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, "🔐 Recuperação de Senha - Apresenta", body)

def generate_verification_code():
    """Gera um código de 6 dígitos"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

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