from flask import Blueprint, request, jsonify
from db_cola_utils import agregar_turno, siguiente_turno, obtener_turnos, eliminar_cola, obtener_turno_actual, obtener_posicion_turno, buscar_turno_global, obtener_estadisticas_cola
import uuid
import json

cola_bp = Blueprint('cola', __name__)

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>', methods=['GET'])
def api_obtener_turnos(id_empresa, id_cola):
    turnos = obtener_turnos(id_empresa, id_cola)
    return jsonify({"turnos": turnos})

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>', methods=['POST'])
def api_agregar_turno(id_empresa, id_cola):
    data = request.get_json()
    turno = {
        "nombre": data.get("nombre"),
        "tipo": data.get("tipo", "General")
    }
    agregado = agregar_turno(id_empresa, id_cola, turno)
    if agregado:
        return jsonify({"turno": agregado})
    return jsonify({"error": "No se pudo agregar el turno"}), 400

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>/siguiente', methods=['POST'])
def api_siguiente_turno(id_empresa, id_cola):
    turno = siguiente_turno(id_empresa, id_cola)
    if turno:
        return jsonify({"turno": turno})
    return jsonify({"mensaje": "No hay turnos"}), 404

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>', methods=['DELETE'])
def api_eliminar_cola(id_empresa, id_cola):
    if eliminar_cola(id_empresa, id_cola):
        return jsonify({"message": "Cola eliminada correctamente"})
    return jsonify({"message": "Cola no encontrada"}), 404

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>/turno-actual', methods=['GET'])
def api_turno_actual(id_empresa, id_cola):
    turno = obtener_turno_actual(id_empresa, id_cola)
    if turno:
        return jsonify(turno)
    return jsonify(None)

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>/verificar', methods=['GET'])
def api_verificar_turno(id_empresa, id_cola):
    identificador = request.args.get("id") or request.args.get("nombre")
    if not identificador:
        return jsonify({"error": "Se requiere 'id' o 'nombre'"}), 400

    resultado = obtener_posicion_turno(id_empresa, id_cola, identificador)
    if resultado:
        return jsonify(resultado)
    return jsonify({"mensaje": "Turno no encontrado"}), 404

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>/estadisticas', methods=['GET'])
def api_estadisticas_cola(id_empresa, id_cola):
    estadisticas = obtener_estadisticas_cola(id_empresa, id_cola)
    return jsonify(estadisticas)

@cola_bp.route('/verificar-global', methods=['GET'])
def verificar_global():
    codigo = request.args.get("codigo")
    if not codigo:
        return jsonify({"error": "Falta el parámetro 'codigo'"}), 400

    resultado = buscar_turno_global(codigo)
    if resultado:
        return jsonify(resultado)
    return jsonify({"mensaje": "Turno no encontrado"}), 404
