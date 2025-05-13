from flask import Flask
from flask_cors import CORS
from api.auth import auth_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}) 
# Registrar el blueprint de autenticación
app.register_blueprint(auth_bp, url_prefix='/api/auth')

if __name__ == '__main__':
    app.run(debug=True)
