from flask import Blueprint, request, jsonify
from Cola_utils import agregar_turno, siguiente_turno, obtener_turnos
import uuid

cola_bp = Blueprint('cola', __name__)

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>', methods=['GET'])
def api_obtener_turnos(id_empresa, id_cola):
    turnos = obtener_turnos(id_empresa, id_cola)
    return jsonify({"turnos": turnos})

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>', methods=['POST'])
def api_agregar_turno(id_empresa, id_cola):
    data = request.get_json()
    turno = {
        "id": str(uuid.uuid4()),
        "nombre": data.get("nombre"),
        "tipo": data.get("tipo", "General")
    }
    agregado = agregar_turno(id_empresa, id_cola, turno)
    return jsonify({"turno": agregado})

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>/siguiente', methods=['POST'])
def api_siguiente_turno(id_empresa, id_cola):
    turno = siguiente_turno(id_empresa, id_cola)
    if turno:
        return jsonify({"turno": turno})
    return jsonify({"mensaje": "No hay turnos"}), 404

@cola_bp.route('/colas', methods=['GET'])
def obtener_todas_colas():
    try:
        with open("cola.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except:
        return jsonify({})

@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>', methods=['DELETE'])
def api_eliminar_cola(id_empresa, id_cola):
    from Cola_utils import eliminar_cola
    if eliminar_cola(id_empresa, id_cola):
        return jsonify({"message": "Cola eliminada correctamente"})
    return jsonify({"message": "Cola no encontrada"}), 404


@cola_bp.route('/proyectos/<id_empresa>/cola/<id_cola>/turno-actual', methods=['GET'])
def api_turno_actual(id_empresa, id_cola):
    from Cola_utils import obtener_turno_actual
    turno = obtener_turno_actual(id_empresa, id_cola)
    if turno:
        return jsonify(turno)
    return jsonify(None)


