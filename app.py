from flask import Flask
from flask_cors import CORS
from api.auth import auth_bp
from api.empresa import empresa_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}) 
# Registrar el blueprint de autenticación
app.register_blueprint(auth_bp, url_prefix='/api/auth')

#registro para commitear empresas desde /home
app.register_blueprint(empresa_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
