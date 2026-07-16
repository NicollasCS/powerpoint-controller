from flask import Flask
from app.config import SECRET_KEY

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

    from app.auth import auth_bp
    from app.user import user_bp
    from app.slides import slides_bp  # <-- ADICIONA ESTE

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(slides_bp)  # <-- ADICIONA ESTE

    return app