from flask import Blueprint, request, jsonify
from db_cola_config_utils import (
    obtener_configuracion, 
    guardar_configuracion_empresa, 
    agregar_categoria,
    actualizar_categoria,
    eliminar_categoria,
    obtener_categoria,
    obtener_categorias_resumen,
    resetear_contador_categoria
)

cola_config_bp = Blueprint("cola_config", __name__)

@cola_config_bp.route("/configuracion/<empresa_id>", methods=["GET"])
def get_config(empresa_id):
    return jsonify(obtener_configuracion(empresa_id))

@cola_config_bp.route("/configuracion/<empresa_id>", methods=["POST"])
def save_config(empresa_id):
    config_data = request.get_json()
    exito, mensaje = guardar_configuracion_empresa(empresa_id, config_data)
    if exito:
        return jsonify({"message": mensaje})
    return jsonify({"error": mensaje}), 400

@cola_config_bp.route("/configuracion/<empresa_id>/categorias", methods=["POST"])
def add_categoria(empresa_id):
    categoria_data = request.get_json()
    categoria, mensaje = agregar_categoria(empresa_id, categoria_data)
    if categoria:
        return jsonify({"message": mensaje, "categoria": categoria}), 201
    return jsonify({"error": mensaje}), 400

@cola_config_bp.route("/configuracion/<empresa_id>/categorias/<categoria_id>", methods=["PUT"])
def update_categoria(empresa_id, categoria_id):
    categoria_data = request.get_json()
    exito, mensaje = actualizar_categoria(empresa_id, categoria_id, categoria_data)
    if exito:
        return jsonify({"message": mensaje})
    return jsonify({"error": mensaje}), 400

@cola_config_bp.route("/configuracion/<empresa_id>/categorias/<categoria_id>", methods=["DELETE"])
def delete_categoria(empresa_id, categoria_id):
    exito, mensaje = eliminar_categoria(empresa_id, categoria_id)
    if exito:
        return jsonify({"message": mensaje})
    return jsonify({"error": mensaje}), 400

@cola_config_bp.route("/configuracion/<empresa_id>/categorias/<categoria_id>", methods=["GET"])
def get_categoria(empresa_id, categoria_id):
    categoria = obtener_categoria(empresa_id, categoria_id)
    if categoria:
        return jsonify(categoria)
    return jsonify({"error": "Categoría no encontrada"}), 404

@cola_config_bp.route("/configuracion/<empresa_id>/resumen", methods=["GET"])
def get_resumen(empresa_id):
    categorias = obtener_categorias_resumen(empresa_id)
    return jsonify({"categorias": categorias})

@cola_config_bp.route("/configuracion/<empresa_id>/categorias/<categoria_id>/resetear-contador", methods=["POST"])
def reset_contador(empresa_id, categoria_id):
    exito, mensaje = resetear_contador_categoria(empresa_id, categoria_id)
    if exito:
        return jsonify({"message": mensaje})
    return jsonify({"error": mensaje}), 400
