from app import app

# Importa todas as rotas
from app import auth, slides

# Se precisar de rotas adicionais, coloque aqui

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)