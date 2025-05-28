import json
import os
from Queue import Queue
import uuid
import random
import string



def generar_codigo_corto():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

cola_file = "Queue.json"
colas_virtuales = {}

def load_colas():
    global colas_virtuales
    if os.path.exists(cola_file):
        with open(cola_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            for empresa_id, colas in raw_data.items():
                colas_virtuales[empresa_id] = {}
                for cola_id, cola_info in colas.items():
                    q = Queue()
                    for turno in cola_info.get("turnos", []):
                        q.push(turno)
                    q.contador = cola_info.get("contador", 0)  # ✅ cargar contador
                    colas_virtuales[empresa_id][cola_id] = q
    else:
        colas_virtuales = {}

def save_colas():
    data = {}
    for empresa_id, subcolas in colas_virtuales.items():
        data[empresa_id] = {}
        for cola_id, cola in subcolas.items():
            turnos = []
            current = cola.front
            while current:
                turnos.append(current.data)
                current = current.next
            data[empresa_id][cola_id] = {
                "contador": cola.contador,  # ✅ guardar contador
                "turnos": turnos
            }

    with open(cola_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def iniciar_cola(empresa_id, cola_id):
    if empresa_id not in colas_virtuales:
        colas_virtuales[empresa_id] = {}
    if cola_id not in colas_virtuales[empresa_id]:
        colas_virtuales[empresa_id][cola_id] = Queue()
        save_colas()

def agregar_turno(empresa_id, cola_id, turno_obj):
    iniciar_cola(empresa_id, cola_id)
    q = colas_virtuales[empresa_id][cola_id]

    q.contador += 1  # ✅ asigna número único
    turno_obj["id"] = str(uuid.uuid4())
    turno_obj["numero"] = q.contador
    turno_obj["codigo"] = generar_codigo_corto()  # 👈 nuevo campo

    q.push(turno_obj)
    save_colas()
    return turno_obj

def siguiente_turno(empresa_id, cola_id):
    if empresa_id in colas_virtuales and cola_id in colas_virtuales[empresa_id]:
        if not colas_virtuales[empresa_id][cola_id].is_empty():
            turno = colas_virtuales[empresa_id][cola_id].pop()
            guardar_turno_actual(empresa_id, cola_id, turno)
            save_colas()
            return turno
    return None

def obtener_turnos(empresa_id, cola_id):
    if empresa_id not in colas_virtuales or cola_id not in colas_virtuales[empresa_id]:
        return []
    turnos = []
    current = colas_virtuales[empresa_id][cola_id].front
    while current:
        turnos.append(current.data)
        current = current.next
    return turnos

def eliminar_cola(empresa_id, cola_id):
    if empresa_id in colas_virtuales and cola_id in colas_virtuales[empresa_id]:
        del colas_virtuales[empresa_id][cola_id]
        save_colas()
        return True
    return False

turnos_llamados = {}  # empresa_id -> cola_id -> último turno

def guardar_turno_actual(empresa_id, cola_id, turno):
    if empresa_id not in turnos_llamados:
        turnos_llamados[empresa_id] = {}
    turnos_llamados[empresa_id][cola_id] = turno

def obtener_turno_actual(empresa_id, cola_id):
    return turnos_llamados.get(empresa_id, {}).get(cola_id)

def obtener_posicion_turno(empresa_id, cola_id, identificador):
    if empresa_id not in colas_virtuales or cola_id not in colas_virtuales[empresa_id]:
        return None

    q = colas_virtuales[empresa_id][cola_id]
    current = q.front
    posicion = 1

    while current:
        data = current.data
        if (data.get("id") == identificador or data.get("nombre") == identificador or data.get("codigo") == identificador):
            return {
                "posicion": posicion,
                "turno": data
            }
        current = current.next
        posicion += 1

    return None


def buscar_turno_global(codigo):
    for empresa_id, subcolas in colas_virtuales.items():
        for cola_id, cola in subcolas.items():
            current = cola.front
            posicion = 1
            while current:
                data = current.data
                if (
                    data.get("id") == codigo
                    or data.get("nombre") == codigo
                    or data.get("codigo") == codigo
                ):
                    return {
                        "empresa_id": empresa_id,
                        "cola_id": cola_id,
                        "posicion": posicion,
                        "turno": data,
                        "turnoActual": obtener_turno_actual(empresa_id, cola_id)
                    }
                current = current.next
                posicion += 1
    return None

