import uuid
import random
import string
import json
from database import get_db_connection

def generar_codigo_corto():
    """Genera un código corto alfanumérico para los turnos"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def iniciar_cola(empresa_id, categoria_id):
    """Inicializa una cola (categoría) si no existe"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si la categoría existe
            cursor.execute('''
                SELECT id FROM cola_categorias 
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            
            if not cursor.fetchone():
                # La categoría no existe, esto significa que hay un error en el sistema
                return False
            
            return True
            
    except Exception as e:
        print(f"Error al inicializar cola: {e}")
        return False

def agregar_turno(empresa_id, categoria_id, turno_obj):
    """Agrega un nuevo turno a la cola"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener y actualizar el contador de la categoría
            cursor.execute('''
                SELECT contador FROM cola_categorias 
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            
            result = cursor.fetchone()
            if not result:
                return None  # La categoría no existe
            
            nuevo_contador = result['contador'] + 1
            
            # Actualizar contador
            cursor.execute('''
                UPDATE cola_categorias 
                SET contador = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND empresa_id = ?
            ''', (nuevo_contador, categoria_id, empresa_id))
            
            # Obtener la siguiente posición en la cola
            cursor.execute('''
                SELECT COALESCE(MAX(posicion), 0) + 1 as next_position
                FROM turnos 
                WHERE categoria_id = ? AND empresa_id = ? AND estado = 'en_espera'
            ''', (categoria_id, empresa_id))
            
            next_position = cursor.fetchone()['next_position']
            
            # Preparar datos del turno
            turno_obj["id"] = str(uuid.uuid4())
            turno_obj["numero"] = nuevo_contador
            turno_obj["codigo"] = generar_codigo_corto()
            
            # Insertar turno
            cursor.execute('''
                INSERT INTO turnos 
                (id, categoria_id, empresa_id, nombre, numero, codigo, estado, posicion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                turno_obj["id"],
                categoria_id,
                empresa_id,
                turno_obj["nombre"],
                turno_obj["numero"],
                turno_obj["codigo"],
                'en_espera',
                next_position
            ))
            
            # El commit se hace automáticamente al salir del context manager
            return turno_obj
            
    except Exception as e:
        print(f"Error al agregar turno: {e}")
        return None

def siguiente_turno(empresa_id, categoria_id):
    """Obtiene el siguiente turno en la cola y lo marca como llamado"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener el turno con menor posición (primero en la cola)
            cursor.execute('''
                SELECT id, categoria_id, empresa_id, nombre, numero, codigo, posicion
                FROM turnos 
                WHERE categoria_id = ? AND empresa_id = ? AND estado = 'en_espera'
                ORDER BY posicion ASC
                LIMIT 1
            ''', (categoria_id, empresa_id))
            
            result = cursor.fetchone()
            if not result:
                return None  # No hay turnos en espera
            
            turno = dict(result)
            
            # Marcar el turno como llamado
            cursor.execute('''
                UPDATE turnos 
                SET estado = 'llamado', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (turno['id'],))
            
            # Actualizar posiciones de los turnos restantes
            cursor.execute('''
                UPDATE turnos 
                SET posicion = posicion - 1, updated_at = CURRENT_TIMESTAMP
                WHERE categoria_id = ? AND empresa_id = ? AND estado = 'en_espera' AND posicion > ?
            ''', (categoria_id, empresa_id, turno['posicion']))
            
            # Guardar como turno actual dentro de la misma transacción
            cursor.execute('''
                INSERT OR REPLACE INTO turnos_actuales 
                (empresa_id, categoria_id, turno_id, turno_data)
                VALUES (?, ?, ?, ?)
            ''', (empresa_id, categoria_id, turno['id'], json.dumps(turno)))
            
            # El commit se hace automáticamente al salir del context manager
            return turno
            
    except Exception as e:
        print(f"Error al obtener siguiente turno: {e}")
        return None

def obtener_turnos(empresa_id, categoria_id):
    """Obtiene todos los turnos en espera de una cola"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, categoria_id, empresa_id, nombre, numero, codigo, posicion, created_at
                FROM turnos 
                WHERE categoria_id = ? AND empresa_id = ? AND estado = 'en_espera'
                ORDER BY posicion ASC
            ''', (categoria_id, empresa_id))
            
            turnos = []
            for row in cursor.fetchall():
                turnos.append(dict(row))
            
            return turnos
            
    except Exception as e:
        print(f"Error al obtener turnos: {e}")
        return []

def eliminar_cola(empresa_id, categoria_id):
    """Elimina una cola (categoría) completa"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Eliminar la categoría (esto también eliminará automáticamente todos los turnos asociados)
            cursor.execute('''
                DELETE FROM cola_categorias 
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            
            # El commit se hace automáticamente al salir del context manager
            if cursor.rowcount > 0:
                return True
            
            return False
            
    except Exception as e:
        print(f"Error al eliminar cola: {e}")
        return False

def guardar_turno_actual(empresa_id, categoria_id, turno_id, turno_data):
    """Guarda el turno que está siendo atendido actualmente"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO turnos_actuales 
                (empresa_id, categoria_id, turno_id, turno_data)
                VALUES (?, ?, ?, ?)
            ''', (empresa_id, categoria_id, turno_id, json.dumps(turno_data)))
            
            # El commit se hace automáticamente al salir del context manager
            
    except Exception as e:
        print(f"Error al guardar turno actual: {e}")

def obtener_turno_actual(empresa_id, categoria_id):
    """Obtiene el turno que está siendo atendido actualmente"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT turno_data 
                FROM turnos_actuales 
                WHERE empresa_id = ? AND categoria_id = ?
            ''', (empresa_id, categoria_id))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result['turno_data'])
            
            return None
            
    except Exception as e:
        print(f"Error al obtener turno actual: {e}")
        return None

def obtener_posicion_turno(empresa_id, categoria_id, identificador):
    """Obtiene la posición de un turno específico en la cola"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, categoria_id, empresa_id, nombre, numero, codigo, posicion, created_at
                FROM turnos 
                WHERE categoria_id = ? AND empresa_id = ? AND estado = 'en_espera' 
                AND (id = ? OR nombre = ? OR codigo = ?)
                LIMIT 1
            ''', (categoria_id, empresa_id, identificador, identificador, identificador))
            
            result = cursor.fetchone()
            if result:
                turno = dict(result)
                return {
                    "posicion": turno["posicion"],
                    "turno": turno
                }
            
            return None
            
    except Exception as e:
        print(f"Error al obtener posición del turno: {e}")
        return None

def buscar_turno_global(codigo):
    """Busca un turno en todas las colas usando código, ID o nombre"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.*, ta.turno_data as turno_actual_data
                FROM turnos t
                LEFT JOIN turnos_actuales ta ON t.categoria_id = ta.categoria_id AND t.empresa_id = ta.empresa_id
                WHERE t.estado = 'en_espera' AND (t.id = ? OR t.nombre = ? OR t.codigo = ?)
                LIMIT 1
            ''', (codigo, codigo, codigo))
            
            result = cursor.fetchone()
            if result:
                turno = dict(result)
                turno_actual = None
                
                if turno['turno_actual_data']:
                    turno_actual = json.loads(turno['turno_actual_data'])
                
                # Remover el campo turno_actual_data del resultado principal
                del turno['turno_actual_data']
                
                return {
                    "empresa_id": turno["empresa_id"],
                    "cola_id": turno["categoria_id"],  # Mantenemos compatibilidad con el nombre anterior
                    "posicion": turno["posicion"],
                    "turno": turno,
                    "turnoActual": turno_actual
                }
            
            return None
            
    except Exception as e:
        print(f"Error al buscar turno global: {e}")
        return None

def obtener_estadisticas_cola(empresa_id, categoria_id):
    """Obtiene estadísticas de una cola específica"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Turnos en espera
            cursor.execute('''
                SELECT COUNT(*) as en_espera FROM turnos 
                WHERE categoria_id = ? AND empresa_id = ? AND estado = 'en_espera'
            ''', (categoria_id, empresa_id))
            en_espera = cursor.fetchone()['en_espera']
            
            # Turnos atendidos hoy
            cursor.execute('''
                SELECT COUNT(*) as atendidos_hoy FROM turnos 
                WHERE categoria_id = ? AND empresa_id = ? AND estado = 'llamado' 
                AND DATE(updated_at) = DATE('now')
            ''', (categoria_id, empresa_id))
            atendidos_hoy = cursor.fetchone()['atendidos_hoy']
            
            # Tiempo estimado de espera
            cursor.execute('''
                SELECT tiempo_estimado FROM cola_categorias 
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            tiempo_estimado_por_turno = cursor.fetchone()['tiempo_estimado']
            
            tiempo_estimado_total = en_espera * tiempo_estimado_por_turno
            
            return {
                "turnos_en_espera": en_espera,
                "turnos_atendidos_hoy": atendidos_hoy,
                "tiempo_estimado_minutos": tiempo_estimado_total
            }
            
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return {
            "turnos_en_espera": 0,
            "turnos_atendidos_hoy": 0,
            "tiempo_estimado_minutos": 0
        }

def limpiar_turnos_antiguos():
    """Limpia turnos llamados de hace más de 1 día (tarea de mantenimiento)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM turnos 
                WHERE estado = 'llamado' AND updated_at < datetime('now', '-1 day')
            ''')
            
            turnos_eliminados = cursor.rowcount
            
            # También limpiar turnos_actuales antiguos
            cursor.execute('''
                DELETE FROM turnos_actuales 
                WHERE created_at < datetime('now', '-1 day')
            ''')
            
            # El commit se hace automáticamente al salir del context manager
            return turnos_eliminados
            
    except Exception as e:
        print(f"Error al limpiar turnos antiguos: {e}")
        return 0