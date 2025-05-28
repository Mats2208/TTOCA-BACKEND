from flask import Blueprint, request, jsonify
from Cola_config_utils import obtener_configuracion, guardar_configuracion_empresa

cola_config_bp = Blueprint("cola_config", __name__)

@cola_config_bp.route("/configuracion/<empresa_id>", methods=["GET"])
def get_config(empresa_id):
    return jsonify(obtener_configuracion(empresa_id))

@cola_config_bp.route("/configuracion/<empresa_id>", methods=["POST"])
def save_config(empresa_id):
    config_data = request.get_json()
    guardar_configuracion_empresa(empresa_id, config_data)
    return jsonify({"message": "Configuración actualizada"})
