from flask import Blueprint, jsonify, request
from auth_utils import get_user_projects, add_user_project, get_user_project_by_id, load_users, save_users


empresa_bp = Blueprint('empresa', __name__)

@empresa_bp.route('/usuarios/<correo>/proyectos', methods=['GET'])
def obtener_empresas(correo):
    proyectos = get_user_projects(correo)
    if proyectos is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    return jsonify({'empresas': proyectos})

@empresa_bp.route('/usuarios/<correo>/proyectos', methods=['POST'])
def agregar_empresa(correo):
    data = request.get_json()
    exito, resultado = add_user_project(correo, data)
    if not exito:
        return jsonify({'message': resultado}), 404
    return jsonify({'message': 'Proyecto creado exitosamente', 'empresa': resultado}), 201

@empresa_bp.route('/usuarios/<correo>/proyectos/<proyecto_id>', methods=['GET'])
def obtener_empresa_por_id(correo, proyecto_id):
    proyecto = get_user_project_by_id(correo, proyecto_id)
    if not proyecto:
        return jsonify({'message': 'Proyecto no encontrado'}), 404
    return jsonify({'empresa': proyecto})

@empresa_bp.route('/usuarios/<correo>/proyectos/<proyecto_id>', methods=['PUT'])
def actualizar_empresa(correo, proyecto_id):
    data = request.get_json()
    users = load_users()
    if correo not in users:
        return jsonify({"message": "Usuario no encontrado"}), 404

    empresas = users[correo].get("empresas", [])
    for i, empresa in enumerate(empresas):
        if empresa["id"] == proyecto_id:
            empresa.update(data)
            save_users(users)
            return jsonify({"message": "Actualizado correctamente", "empresa": empresa})

    return jsonify({"message": "Proyecto no encontrado"}), 404
