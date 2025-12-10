"""
Utilidades de administración para la base de datos TTOCA

Este módulo proporciona funciones útiles para administrar la base de datos,
como limpiezas, estadísticas y mantenimiento.
"""

from core.database import get_db_connection
import sqlite3
from datetime import datetime, timedelta

def obtener_estadisticas_generales():
    """Obtiene estadísticas generales del sistema"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Usuarios totales
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_usuarios = cursor.fetchone()['count']
            
            # Empresas totales
            cursor.execute("SELECT COUNT(*) as count FROM empresas")
            total_empresas = cursor.fetchone()['count']
            
            # Categorías totales
            cursor.execute("SELECT COUNT(*) as count FROM cola_categorias")
            total_categorias = cursor.fetchone()['count']
            
            # Turnos activos (en espera)
            cursor.execute("SELECT COUNT(*) as count FROM turnos WHERE estado = 'en_espera'")
            turnos_activos = cursor.fetchone()['count']
            
            # Turnos atendidos hoy
            cursor.execute("""
                SELECT COUNT(*) as count FROM turnos 
                WHERE estado = 'llamado' AND DATE(updated_at) = DATE('now')
            """)
            turnos_hoy = cursor.fetchone()['count']
            
            # Turnos atendidos esta semana
            cursor.execute("""
                SELECT COUNT(*) as count FROM turnos 
                WHERE estado = 'llamado' AND updated_at >= DATE('now', '-7 days')
            """)
            turnos_semana = cursor.fetchone()['count']
            
            # Empresa más activa (con más turnos hoy)
            cursor.execute("""
                SELECT e.nombre, COUNT(t.id) as turnos_hoy
                FROM empresas e
                LEFT JOIN turnos t ON e.id = t.empresa_id AND DATE(t.created_at) = DATE('now')
                GROUP BY e.id, e.nombre
                ORDER BY turnos_hoy DESC
                LIMIT 1
            """)
            empresa_activa = cursor.fetchone()
            
            return {
                "usuarios_totales": total_usuarios,
                "empresas_totales": total_empresas,
                "categorias_totales": total_categorias,
                "turnos_activos": turnos_activos,
                "turnos_atendidos_hoy": turnos_hoy,
                "turnos_atendidos_semana": turnos_semana,
                "empresa_mas_activa": {
                    "nombre": empresa_activa['nombre'] if empresa_activa else "N/A",
                    "turnos_hoy": empresa_activa['turnos_hoy'] if empresa_activa else 0
                }
            }
            
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return None

def limpiar_turnos_completados(dias_antiguedad=1):
    """Limpia turnos completados más antiguos que X días"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM turnos 
                WHERE estado = 'llamado' AND updated_at < datetime('now', '-{} days')
            """.format(dias_antiguedad))
            
            turnos_eliminados = cursor.rowcount
            
            # También limpiar registros de turnos actuales antiguos
            cursor.execute("""
                DELETE FROM turnos_actuales 
                WHERE created_at < datetime('now', '-{} days')
            """.format(dias_antiguedad))
            
            turnos_actuales_eliminados = cursor.rowcount
            
            # El commit se hace automáticamente al salir del context manager
            
            return {
                "turnos_eliminados": turnos_eliminados,
                "turnos_actuales_eliminados": turnos_actuales_eliminados
            }
            
    except Exception as e:
        print(f"Error al limpiar turnos: {e}")
        return None

def obtener_actividad_por_empresa():
    """Obtiene estadísticas de actividad por empresa"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    e.nombre,
                    e.user_email,
                    COUNT(DISTINCT cc.id) as categorias,
                    COUNT(CASE WHEN t.estado = 'en_espera' THEN t.id END) as turnos_activos,
                    COUNT(CASE WHEN t.estado = 'llamado' AND DATE(t.updated_at) = DATE('now') THEN t.id END) as turnos_hoy,
                    COUNT(CASE WHEN t.estado = 'llamado' AND t.updated_at >= DATE('now', '-7 days') THEN t.id END) as turnos_semana
                FROM empresas e
                LEFT JOIN cola_categorias cc ON e.id = cc.empresa_id
                LEFT JOIN turnos t ON e.id = t.empresa_id
                GROUP BY e.id, e.nombre, e.user_email
                ORDER BY turnos_hoy DESC, turnos_semana DESC
            """)
            
            empresas = []
            for row in cursor.fetchall():
                empresas.append(dict(row))
            
            return empresas
            
    except Exception as e:
        print(f"Error al obtener actividad por empresa: {e}")
        return []

def obtener_turnos_por_periodo(empresa_id, dias=7):
    """Obtiene estadísticas de turnos por período para una empresa"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    DATE(created_at) as fecha,
                    COUNT(*) as total_turnos,
                    COUNT(CASE WHEN estado = 'llamado' THEN 1 END) as turnos_completados,
                    COUNT(CASE WHEN estado = 'en_espera' THEN 1 END) as turnos_pendientes
                FROM turnos
                WHERE empresa_id = ? AND created_at >= DATE('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY fecha DESC
            """.format(dias), (empresa_id,))
            
            estadisticas = []
            for row in cursor.fetchall():
                estadisticas.append(dict(row))
            
            return estadisticas
            
    except Exception as e:
        print(f"Error al obtener turnos por período: {e}")
        return []

def verificar_integridad_base_datos():
    """Verifica la integridad de la base de datos"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            problemas = []
            
            # Verificar empresas sin usuarios
            cursor.execute("""
                SELECT e.id, e.nombre FROM empresas e
                LEFT JOIN users u ON e.user_email = u.email
                WHERE u.email IS NULL
            """)
            empresas_huerfanas = cursor.fetchall()
            if empresas_huerfanas:
                problemas.append({
                    "tipo": "Empresas sin usuario",
                    "cantidad": len(empresas_huerfanas),
                    "detalles": [dict(row) for row in empresas_huerfanas]
                })
            
            # Verificar turnos sin categoría
            cursor.execute("""
                SELECT t.id, t.nombre FROM turnos t
                LEFT JOIN cola_categorias cc ON t.categoria_id = cc.id
                WHERE cc.id IS NULL
            """)
            turnos_huerfanos = cursor.fetchall()
            if turnos_huerfanos:
                problemas.append({
                    "tipo": "Turnos sin categoría",
                    "cantidad": len(turnos_huerfanos),
                    "detalles": [dict(row) for row in turnos_huerfanos]
                })
            
            # Verificar inconsistencias en posiciones
            cursor.execute("""
                SELECT categoria_id, empresa_id, COUNT(*) as duplicados
                FROM turnos
                WHERE estado = 'en_espera'
                GROUP BY categoria_id, empresa_id, posicion
                HAVING COUNT(*) > 1
            """)
            posiciones_duplicadas = cursor.fetchall()
            if posiciones_duplicadas:
                problemas.append({
                    "tipo": "Posiciones duplicadas en colas",
                    "cantidad": len(posiciones_duplicadas),
                    "detalles": [dict(row) for row in posiciones_duplicadas]
                })
            
            return {
                "integridad_ok": len(problemas) == 0,
                "problemas": problemas
            }
            
    except Exception as e:
        print(f"Error al verificar integridad: {e}")
        return None

def reparar_posiciones_cola():
    """Repara las posiciones de los turnos en todas las colas"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener todas las colas activas
            cursor.execute("""
                SELECT DISTINCT categoria_id, empresa_id
                FROM turnos
                WHERE estado = 'en_espera'
            """)
            
            colas_reparadas = 0
            
            for row in cursor.fetchall():
                categoria_id = row['categoria_id']
                empresa_id = row['empresa_id']
                
                # Obtener turnos ordenados por fecha de creación
                cursor.execute("""
                    SELECT id FROM turnos
                    WHERE categoria_id = ? AND empresa_id = ? AND estado = 'en_espera'
                    ORDER BY created_at ASC
                """, (categoria_id, empresa_id))
                
                turnos = cursor.fetchall()
                
                # Actualizar posiciones
                for i, turno in enumerate(turnos):
                    cursor.execute("""
                        UPDATE turnos 
                        SET posicion = ? 
                        WHERE id = ?
                    """, (i + 1, turno['id']))
                
                colas_reparadas += 1
            
            # El commit se hace automáticamente al salir del context manager
            
            return {
                "colas_reparadas": colas_reparadas,
                "mensaje": f"Se repararon las posiciones de {colas_reparadas} colas"
            }
            
    except Exception as e:
        print(f"Error al reparar posiciones: {e}")
        return None

def exportar_backup_completo():
    """Exporta un backup completo de la base de datos en formato JSON"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "usuarios": [],
                "empresas": [],
                "categorias": [],
                "turnos": [],
                "turnos_actuales": []
            }
            
            # Exportar usuarios
            cursor.execute("SELECT * FROM users")
            for row in cursor.fetchall():
                backup_data["usuarios"].append(dict(row))
            
            # Exportar empresas
            cursor.execute("SELECT * FROM empresas")
            for row in cursor.fetchall():
                backup_data["empresas"].append(dict(row))
            
            # Exportar categorías
            cursor.execute("SELECT * FROM cola_categorias")
            for row in cursor.fetchall():
                backup_data["categorias"].append(dict(row))
            
            # Exportar turnos
            cursor.execute("SELECT * FROM turnos")
            for row in cursor.fetchall():
                backup_data["turnos"].append(dict(row))
            
            # Exportar turnos actuales
            cursor.execute("SELECT * FROM turnos_actuales")
            for row in cursor.fetchall():
                backup_data["turnos_actuales"].append(dict(row))
            
            # Guardar backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_completo_{timestamp}.json"
            
            import json
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
            
            return {
                "archivo": backup_filename,
                "registros_exportados": {
                    "usuarios": len(backup_data["usuarios"]),
                    "empresas": len(backup_data["empresas"]),
                    "categorias": len(backup_data["categorias"]),
                    "turnos": len(backup_data["turnos"]),
                    "turnos_actuales": len(backup_data["turnos_actuales"])
                }
            }
            
    except Exception as e:
        print(f"Error al exportar backup: {e}")
        return None