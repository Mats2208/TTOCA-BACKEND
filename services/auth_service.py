import bcrypt
import uuid
import json
from core.database import get_db_connection
from datetime import datetime

def add_user(username, email, password):
    """Agrega un nuevo usuario a la base de datos"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return False  # Usuario ya existe
            
            # Hash de la contraseña
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Insertar usuario
            cursor.execute('''
                INSERT INTO users (email, password)
                VALUES (?, ?)
            ''', (email, hashed_password.decode('utf-8')))
            
            # El commit se hace automáticamente al salir del context manager
            return True
            
    except Exception as e:
        print(f"Error al agregar usuario: {e}")
        return False

def validate_user(email, password):
    """Valida las credenciales de un usuario"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            hashed_password = result['password']
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
            
    except Exception as e:
        print(f"Error al validar usuario: {e}")
        return False

def get_user_projects(email):
    """Obtiene todas las empresas de un usuario"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nombre, logo, titular, direccion, telefono, email, horario, config
                FROM empresas 
                WHERE user_email = ?
                ORDER BY created_at DESC
            ''', (email,))
            
            empresas = []
            for row in cursor.fetchall():
                empresa = dict(row)
                # Parsear config JSON
                try:
                    empresa['config'] = json.loads(empresa['config']) if empresa['config'] else {}
                except:
                    empresa['config'] = {}
                empresas.append(empresa)
            
            return empresas
            
    except Exception as e:
        print(f"Error al obtener proyectos del usuario: {e}")
        return []

def get_user_project_by_id(email, proyecto_id):
    """Obtiene una empresa específica de un usuario"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nombre, logo, titular, direccion, telefono, email, horario, config
                FROM empresas 
                WHERE user_email = ? AND id = ?
            ''', (email, proyecto_id))
            
            result = cursor.fetchone()
            if result:
                empresa = dict(result)
                # Parsear config JSON
                try:
                    empresa['config'] = json.loads(empresa['config']) if empresa['config'] else {}
                except:
                    empresa['config'] = {}
                return empresa
            
            return None
            
    except Exception as e:
        print(f"Error al obtener proyecto por ID: {e}")
        return None

def add_user_project(email, proyecto_data):
    """Agrega una nueva empresa a un usuario"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el usuario existe
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if not cursor.fetchone():
                return False, "Usuario no existe en la base de datos"
            
            # Crear nueva empresa
            nueva_empresa = {
                "id": str(uuid.uuid4())[:8],
                "nombre": proyecto_data.get("nombre"),
                "logo": proyecto_data.get("logo", ""),
                "titular": proyecto_data.get("titular", ""),
                "direccion": proyecto_data.get("direccion", ""),
                "telefono": proyecto_data.get("telefono", ""),
                "email": proyecto_data.get("email", ""),
                "horario": proyecto_data.get("horario", ""),
                "config": proyecto_data.get("config", {})
            }
            
            # Insertar empresa
            cursor.execute('''
                INSERT INTO empresas 
                (id, user_email, nombre, logo, titular, direccion, telefono, email, horario, config)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nueva_empresa["id"],
                email,
                nueva_empresa["nombre"],
                nueva_empresa["logo"],
                nueva_empresa["titular"],
                nueva_empresa["direccion"],
                nueva_empresa["telefono"],
                nueva_empresa["email"],
                nueva_empresa["horario"],
                json.dumps(nueva_empresa["config"])
            ))
            
            # El commit se hace automáticamente al salir del context manager
            return True, nueva_empresa
            
    except Exception as e:
        print(f"Error al agregar proyecto de usuario: {e}")
        return False, f"Error interno: {str(e)}"

def update_user_project(email, proyecto_id, proyecto_data):
    """Actualiza una empresa existente"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que la empresa pertenece al usuario
            cursor.execute('SELECT id FROM empresas WHERE id = ? AND user_email = ?', (proyecto_id, email))
            if not cursor.fetchone():
                return False, "Empresa no encontrada o no pertenece al usuario"
            
            # Actualizar empresa
            cursor.execute('''
                UPDATE empresas 
                SET nombre = ?, logo = ?, titular = ?, direccion = ?, 
                    telefono = ?, email = ?, horario = ?, config = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_email = ?
            ''', (
                proyecto_data.get("nombre", ""),
                proyecto_data.get("logo", ""),
                proyecto_data.get("titular", ""),
                proyecto_data.get("direccion", ""),
                proyecto_data.get("telefono", ""),
                proyecto_data.get("email", ""),
                proyecto_data.get("horario", ""),
                json.dumps(proyecto_data.get("config", {})),
                proyecto_id,
                email
            ))
            
            # El commit se hace automáticamente al salir del context manager
            return True, "Empresa actualizada correctamente"
            
    except Exception as e:
        print(f"Error al actualizar proyecto: {e}")
        return False, f"Error interno: {str(e)}"

def delete_user_project(email, proyecto_id):
    """Elimina una empresa de un usuario"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que la empresa pertenece al usuario
            cursor.execute('SELECT id FROM empresas WHERE id = ? AND user_email = ?', (proyecto_id, email))
            if not cursor.fetchone():
                return False, "Empresa no encontrada o no pertenece al usuario"
            
            # Eliminar empresa (esto también eliminará automáticamente las categorías y turnos asociados)
            cursor.execute('DELETE FROM empresas WHERE id = ? AND user_email = ?', (proyecto_id, email))
            
            # El commit se hace automáticamente al salir del context manager
            return True, "Empresa eliminada correctamente"
            
    except Exception as e:
        print(f"Error al eliminar proyecto: {e}")
        return False, f"Error interno: {str(e)}"