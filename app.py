from flask import Flask, send_from_directory
from flask_cors import CORS
from api.auth import auth_bp
from api.empresa import empresa_bp
from api.cola import cola_bp
from Cola_utils import load_colas, save_colas
from api.cola_config import cola_config_bp
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4173", "http://localhost:5173", "https://www.ttoca.online"]}})
# Registrar el blueprint de autenticación
app.register_blueprint(auth_bp, url_prefix='/api/auth')

#registro para commitear empresas desde /home
app.register_blueprint(empresa_bp, url_prefix='/api')

#Registro para commitear turnos desde /Dashboard
app.register_blueprint(cola_bp, url_prefix='/api')

#Registro para commitear configuraciones de las distintas queue que puede crear el usuario
app.register_blueprint(cola_config_bp, url_prefix='/api')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    if path != "" and os.path.exists(os.path.join('dist', path)):
        return send_from_directory('dist', path)
    else:
        return send_from_directory('dist', 'index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

