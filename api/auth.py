from flask import Blueprint, request, jsonify
from auth_utils import add_user, validate_user

auth_bp = Blueprint('auth', __name__)

# Ruta para registrar un nuevo usuario
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('usuario')
    email = data.get('correo')
    password = data.get('contrasena')

    if not username or not email or not password:
        return jsonify({'message': 'Todos los campos son requeridos'}), 400

    if add_user(username, email, password):
        return jsonify({'message': 'Usuario registrado exitosamente'}), 201
    else:
        return jsonify({'message': 'El usuario ya existe'}), 400

# Ruta para iniciar sesión
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('correo')  # Cambiar a 'correo' para que coincida con el frontend
    password = data.get('contrasena')

    if not username or not password:
        return jsonify({'message': 'Todos los campos son requeridos'}), 400

    if validate_user(username, password):
        return jsonify({'message': 'Inicio de sesión exitoso'}), 200
    else:
        return jsonify({'message': 'Credenciales inválidas'}), 401
