from flask import request, jsonify, session, Blueprint, render_template
from app.database import get_user_by_id, update_user_token, get_user_by_token
from app.utils import generate_token, convert_pdf_to_images
import uuid
import os

slides_bp = Blueprint('slides', __name__)

# Armazena apresentações em memória
presentations = {}

class Presentation:
    def __init__(self, pdf_bytes, ppt_id, user_id):
        self.ppt_id = ppt_id
        self.user_id = user_id
        self.slide_atual = 0
        self.total_slides = 0
        self.ativo = False
        self.slides_images = []
        self._process_pdf(pdf_bytes)
        
    def _process_pdf(self, pdf_bytes):
        from app.utils import convert_pdf_to_images
        images_data, total = convert_pdf_to_images(pdf_bytes)
        self.total_slides = total
        for i, img_data in enumerate(images_data):
            self.slides_images.append({
                'numero': i + 1,
                'imagem': img_data
            })
    
    def get_slide_info(self):
        return self.slide_atual, self.total_slides

# ========== ROTA DO CONTROLE (CELULAR) ==========

@slides_bp.route('/controle')
def controle_page():
    return render_template('controle.html')

# ========== API DE SLIDES ==========

@slides_bp.route('/api/upload', methods=['POST'])
def api_upload():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401

    file = request.files['file']
    if not file:
        return jsonify({'error': 'Nenhum arquivo'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Formato não suportado. Use .pdf'}), 400

    ppt_id = str(uuid.uuid4())[:8]
    pdf_bytes = file.read()

    presentations[ppt_id] = Presentation(pdf_bytes, ppt_id, session['user_id'])
    total = presentations[ppt_id].total_slides

    if total == 0:
        return jsonify({'error': 'Nenhuma página encontrada no PDF'}), 400

    user = get_user_by_id(session['user_id'])
    token = generate_token(user['email'])
    update_user_token(session['user_id'], token)

    return jsonify({
        'status': 'success',
        'ppt_id': ppt_id,
        'message': f'PDF processado! {total} páginas.',
        'total_slides': total,
        'token': token
    })

@slides_bp.route('/api/get_presentation_by_token')
def api_get_presentation_by_token():
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Token necessário'}), 400
    
    user = get_user_by_token(token)
    if not user:
        return jsonify({'error': 'Token inválido'}), 401
    
    for ppt_id, ppt in presentations.items():
        if ppt.user_id == user['id']:
            return jsonify({
                'ppt_id': ppt_id,
                'total_slides': ppt.total_slides
            })
    
    return jsonify({'error': 'Nenhuma apresentação ativa'}), 404

@slides_bp.route('/api/slides/<ppt_id>')
def api_get_slides(ppt_id):
    if ppt_id not in presentations:
        return jsonify({'error': 'Não encontrado'}), 404
    
    ppt = presentations[ppt_id]
    slides_data = []
    for i, slide in enumerate(ppt.slides_images):
        slides_data.append({
            'numero': slide['numero'],
            'imagem': slide['imagem'],
            'ativo': i == ppt.slide_atual
        })
    
    return jsonify({
        'slides': slides_data,
        'slide_atual': ppt.slide_atual,
        'total': ppt.total_slides
    })

@slides_bp.route('/api/status/<ppt_id>')
def api_status(ppt_id):
    if ppt_id not in presentations:
        return jsonify({'error': 'Não encontrado'}), 404
    
    ppt = presentations[ppt_id]
    slide, total = ppt.get_slide_info()
    
    return jsonify({
        'slide_atual': slide,
        'total_slides': total,
        'ativo': ppt.ativo
    })

@slides_bp.route('/api/next/<ppt_id>')
def api_next(ppt_id):
    if ppt_id not in presentations:
        return jsonify({'error': 'Não encontrado'}), 404
    
    ppt = presentations[ppt_id]
    slide, total = ppt.get_slide_info()
    
    if slide < total - 1:
        ppt.slide_atual += 1
    
    return jsonify({'status': 'ok', 'slide': ppt.slide_atual})

@slides_bp.route('/api/prev/<ppt_id>')
def api_prev(ppt_id):
    if ppt_id not in presentations:
        return jsonify({'error': 'Não encontrado'}), 404
    
    ppt = presentations[ppt_id]
    slide, total = ppt.get_slide_info()
    
    if slide > 0:
        ppt.slide_atual -= 1
    
    return jsonify({'status': 'ok', 'slide': ppt.slide_atual})

@slides_bp.route('/api/start/<ppt_id>')
def api_start(ppt_id):
    if ppt_id not in presentations:
        return jsonify({'error': 'Não encontrado'}), 404
    
    presentations[ppt_id].ativo = True
    return jsonify({'status': 'started'})

@slides_bp.route('/api/validate_token', methods=['POST'])
def api_validate_token():
    data = request.json
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Token é obrigatório'}), 400

    user = get_user_by_token(token)
    if not user:
        return jsonify({'error': 'Token inválido'}), 401

    return jsonify({'status': 'success', 'user_email': user['email']})

# ========== ROTA DE COMPATIBILIDADE ==========
@slides_bp.route('/upload', methods=['POST'])
def upload_redirect():
    return api_upload()