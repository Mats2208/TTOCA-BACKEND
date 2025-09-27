import uuid
import json
from database import get_db_connection

def obtener_configuracion(empresa_id):
    """Obtiene la configuración completa de las colas de una empresa"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nombre, descripcion, prioridad, tiempo_estimado, contador, created_at, updated_at
                FROM cola_categorias 
                WHERE empresa_id = ?
                ORDER BY created_at ASC
            ''', (empresa_id,))
            
            categorias = []
            for row in cursor.fetchall():
                categoria = dict(row)
                # Convertir el campo prioridad de entero a booleano
                categoria['prioridad'] = bool(categoria['prioridad'])
                # Renombrar campo para mantener compatibilidad
                categoria['tiempoEstimado'] = categoria['tiempo_estimado']
                del categoria['tiempo_estimado']
                categorias.append(categoria)
            
            return {
                "categorias": categorias
            }
            
    except Exception as e:
        print(f"Error al obtener configuración: {e}")
        return {"categorias": []}

def guardar_configuracion_empresa(empresa_id, config):
    """Guarda la configuración completa de las colas de una empresa"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que la empresa existe
            cursor.execute('SELECT id FROM empresas WHERE id = ?', (empresa_id,))
            if not cursor.fetchone():
                return False, "Empresa no encontrada"
            
            # Obtener categorías actuales
            cursor.execute('SELECT id FROM cola_categorias WHERE empresa_id = ?', (empresa_id,))
            categorias_existentes = {row['id'] for row in cursor.fetchall()}
            
            categorias_nuevas = set()
            
            # Procesar cada categoría en la configuración
            if 'categorias' in config:
                for categoria in config['categorias']:
                    categoria_id = categoria.get('id')
                    if not categoria_id:
                        # Generar nuevo ID si no existe
                        categoria_id = str(uuid.uuid4())
                    
                    categorias_nuevas.add(categoria_id)
                    
                    # Insertar o actualizar categoría
                    cursor.execute('''
                        INSERT OR REPLACE INTO cola_categorias 
                        (id, empresa_id, nombre, descripcion, prioridad, tiempo_estimado, contador, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, 
                                COALESCE((SELECT contador FROM cola_categorias WHERE id = ?), 0),
                                CURRENT_TIMESTAMP)
                    ''', (
                        categoria_id,
                        empresa_id,
                        categoria.get('nombre', ''),
                        categoria.get('descripcion', ''),
                        bool(categoria.get('prioridad', False)),
                        categoria.get('tiempoEstimado', 5),
                        categoria_id  # Para preservar el contador existente
                    ))
            
            # Eliminar categorías que ya no están en la configuración
            categorias_a_eliminar = categorias_existentes - categorias_nuevas
            for categoria_id in categorias_a_eliminar:
                cursor.execute('''
                    DELETE FROM cola_categorias 
                    WHERE id = ? AND empresa_id = ?
                ''', (categoria_id, empresa_id))
            
            conn.commit()
            return True, "Configuración guardada correctamente"
            
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False, f"Error interno: {str(e)}"

def agregar_categoria(empresa_id, categoria_data):
    """Agrega una nueva categoría de cola a una empresa"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que la empresa existe
            cursor.execute('SELECT id FROM empresas WHERE id = ?', (empresa_id,))
            if not cursor.fetchone():
                return None, "Empresa no encontrada"
            
            # Generar ID único para la categoría
            categoria_id = str(uuid.uuid4())
            
            # Insertar nueva categoría
            cursor.execute('''
                INSERT INTO cola_categorias 
                (id, empresa_id, nombre, descripcion, prioridad, tiempo_estimado, contador)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                categoria_id,
                empresa_id,
                categoria_data.get('nombre', ''),
                categoria_data.get('descripcion', ''),
                bool(categoria_data.get('prioridad', False)),
                categoria_data.get('tiempoEstimado', 5),
                0  # Contador inicial
            ))
            
            conn.commit()
            
            # Retornar la categoría creada
            nueva_categoria = {
                "id": categoria_id,
                "nombre": categoria_data.get('nombre', ''),
                "descripcion": categoria_data.get('descripcion', ''),
                "prioridad": bool(categoria_data.get('prioridad', False)),
                "tiempoEstimado": categoria_data.get('tiempoEstimado', 5),
                "contador": 0
            }
            
            return nueva_categoria, "Categoría creada correctamente"
            
    except Exception as e:
        print(f"Error al agregar categoría: {e}")
        return None, f"Error interno: {str(e)}"

def actualizar_categoria(empresa_id, categoria_id, categoria_data):
    """Actualiza una categoría existente"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que la categoría pertenece a la empresa
            cursor.execute('''
                SELECT id FROM cola_categorias 
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            
            if not cursor.fetchone():
                return False, "Categoría no encontrada o no pertenece a la empresa"
            
            # Actualizar categoría
            cursor.execute('''
                UPDATE cola_categorias 
                SET nombre = ?, descripcion = ?, prioridad = ?, tiempo_estimado = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND empresa_id = ?
            ''', (
                categoria_data.get('nombre', ''),
                categoria_data.get('descripcion', ''),
                bool(categoria_data.get('prioridad', False)),
                categoria_data.get('tiempoEstimado', 5),
                categoria_id,
                empresa_id
            ))
            
            conn.commit()
            return True, "Categoría actualizada correctamente"
            
    except Exception as e:
        print(f"Error al actualizar categoría: {e}")
        return False, f"Error interno: {str(e)}"

def eliminar_categoria(empresa_id, categoria_id):
    """Elimina una categoría y todos sus turnos asociados"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que la categoría pertenece a la empresa
            cursor.execute('''
                SELECT id FROM cola_categorias 
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            
            if not cursor.fetchone():
                return False, "Categoría no encontrada o no pertenece a la empresa"
            
            # Eliminar categoría (esto también eliminará automáticamente todos los turnos asociados)
            cursor.execute('''
                DELETE FROM cola_categorias 
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            
            conn.commit()
            return True, "Categoría eliminada correctamente"
            
    except Exception as e:
        print(f"Error al eliminar categoría: {e}")
        return False, f"Error interno: {str(e)}"

def obtener_categoria(empresa_id, categoria_id):
    """Obtiene una categoría específica"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nombre, descripcion, prioridad, tiempo_estimado, contador, created_at, updated_at
                FROM cola_categorias 
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            
            result = cursor.fetchone()
            if result:
                categoria = dict(result)
                # Convertir el campo prioridad de entero a booleano
                categoria['prioridad'] = bool(categoria['prioridad'])
                # Renombrar campo para mantener compatibilidad
                categoria['tiempoEstimado'] = categoria['tiempo_estimado']
                del categoria['tiempo_estimado']
                return categoria
            
            return None
            
    except Exception as e:
        print(f"Error al obtener categoría: {e}")
        return None

def obtener_categorias_resumen(empresa_id):
    """Obtiene un resumen de todas las categorías con estadísticas básicas"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    cc.id, 
                    cc.nombre, 
                    cc.descripcion, 
                    cc.prioridad, 
                    cc.tiempo_estimado,
                    cc.contador,
                    COUNT(t.id) as turnos_en_espera
                FROM cola_categorias cc
                LEFT JOIN turnos t ON cc.id = t.categoria_id AND t.estado = 'en_espera'
                WHERE cc.empresa_id = ?
                GROUP BY cc.id, cc.nombre, cc.descripcion, cc.prioridad, cc.tiempo_estimado, cc.contador
                ORDER BY cc.created_at ASC
            ''', (empresa_id,))
            
            categorias = []
            for row in cursor.fetchall():
                categoria = dict(row)
                # Convertir el campo prioridad de entero a booleano
                categoria['prioridad'] = bool(categoria['prioridad'])
                # Renombrar campo para mantener compatibilidad
                categoria['tiempoEstimado'] = categoria['tiempo_estimado']
                del categoria['tiempo_estimado']
                categorias.append(categoria)
            
            return categorias
            
    except Exception as e:
        print(f"Error al obtener categorías resumen: {e}")
        return []

def resetear_contador_categoria(empresa_id, categoria_id):
    """Resetea el contador de una categoría a 0"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que la categoría pertenece a la empresa
            cursor.execute('''
                SELECT id FROM cola_categorias 
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            
            if not cursor.fetchone():
                return False, "Categoría no encontrada o no pertenece a la empresa"
            
            # Resetear contador
            cursor.execute('''
                UPDATE cola_categorias 
                SET contador = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND empresa_id = ?
            ''', (categoria_id, empresa_id))
            
            conn.commit()
            return True, "Contador reseteado correctamente"
            
    except Exception as e:
        print(f"Error al resetear contador: {e}")
        return False, f"Error interno: {str(e)}"