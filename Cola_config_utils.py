import json
import os

config_path = "cola_config.json"
if not os.path.exists(config_path):
    with open(config_path, "w") as f:
        json.dump({}, f)

def cargar_configuracion():
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_configuracion(data):
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def obtener_configuracion(empresa_id):
    data = cargar_configuracion()
    return data.get(empresa_id, {})

def guardar_configuracion_empresa(empresa_id, config):
    data = cargar_configuracion()
    data[empresa_id] = config
    guardar_configuracion(data)

def agregar_turno(empresa_id, cola_id, nombre):
    cola_data = COLAS[empresa_id][cola_id]
    numero_turno = cola_data.get("contador", 0) + 1
    cola_data["contador"] = numero_turno

    nuevo_turno = {
        "id": str(uuid4()),
        "nombre": nombre,
        "numero": numero_turno
    }
    cola_data["turnos"].append(nuevo_turno)

    guardar_colas()
    return nuevo_turno

