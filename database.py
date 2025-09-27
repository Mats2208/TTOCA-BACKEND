import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE_NAME = 'ttoca.db'

@contextmanager
def get_db_connection():
    """Context manager para manejar conexiones a la base de datos"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Inicializa la base de datos con todas las tablas necesarias"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de empresas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresas (
                id TEXT PRIMARY KEY,
                user_email TEXT NOT NULL,
                nombre TEXT NOT NULL,
                logo TEXT DEFAULT '',
                titular TEXT DEFAULT '',
                direccion TEXT DEFAULT '',
                telefono TEXT DEFAULT '',
                email TEXT DEFAULT '',
                horario TEXT DEFAULT '',
                config TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users (email) ON DELETE CASCADE
            )
        ''')
        
        # Tabla de categorías de cola
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cola_categorias (
                id TEXT PRIMARY KEY,
                empresa_id TEXT NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT DEFAULT '',
                prioridad BOOLEAN DEFAULT FALSE,
                tiempo_estimado INTEGER DEFAULT 5,
                contador INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabla de turnos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turnos (
                id TEXT PRIMARY KEY,
                categoria_id TEXT NOT NULL,
                empresa_id TEXT NOT NULL,
                nombre TEXT NOT NULL,
                numero INTEGER NOT NULL,
                codigo TEXT NOT NULL,
                estado TEXT DEFAULT 'en_espera',
                posicion INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES cola_categorias (id) ON DELETE CASCADE,
                FOREIGN KEY (empresa_id) REFERENCES empresas (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabla de turnos actuales (para llevar control del turno que se está atendiendo)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turnos_actuales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id TEXT NOT NULL,
                categoria_id TEXT NOT NULL,
                turno_id TEXT NOT NULL,
                turno_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas (id) ON DELETE CASCADE,
                FOREIGN KEY (categoria_id) REFERENCES cola_categorias (id) ON DELETE CASCADE,
                FOREIGN KEY (turno_id) REFERENCES turnos (id) ON DELETE CASCADE,
                UNIQUE(empresa_id, categoria_id)
            )
        ''')
        
        # Índices para mejorar el rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_empresas_user_email ON empresas (user_email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_categorias_empresa ON cola_categorias (empresa_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_turnos_categoria ON turnos (categoria_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_turnos_empresa ON turnos (empresa_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_turnos_estado ON turnos (estado)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_turnos_posicion ON turnos (posicion)')
        
        conn.commit()
        print("✅ Base de datos inicializada correctamente")

def migrate_from_json():
    """Migra datos existentes de archivos JSON a SQLite"""
    print("🔄 Iniciando migración de datos JSON a SQLite...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Determinar la ruta de los archivos JSON (backup o original)
        users_file = 'users.json'
        queue_file = 'Queue.json'
        config_file = 'cola_config.json'
        
        # Si los archivos están en backup, usar esos
        if os.path.exists('json_backup/users.json.backup'):
            users_file = 'json_backup/users.json.backup'
        if os.path.exists('json_backup/Queue.json.backup'):
            queue_file = 'json_backup/Queue.json.backup'
        if os.path.exists('json_backup/cola_config.json.backup'):
            config_file = 'json_backup/cola_config.json.backup'
        
        # Migrar usuarios y empresas desde users.json
        if os.path.exists(users_file):
            print("📁 Migrando usuarios y empresas...")
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            for email, user_info in users_data.items():
                # Insertar usuario
                cursor.execute('''
                    INSERT OR REPLACE INTO users (email, password)
                    VALUES (?, ?)
                ''', (email, user_info['password']))
                
                # Insertar empresas del usuario
                if 'empresas' in user_info:
                    for empresa in user_info['empresas']:
                        cursor.execute('''
                            INSERT OR REPLACE INTO empresas 
                            (id, user_email, nombre, logo, titular, direccion, telefono, email, horario, config)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            empresa['id'],
                            email,
                            empresa['nombre'],
                            empresa.get('logo', ''),
                            empresa.get('titular', ''),
                            empresa.get('direccion', ''),
                            empresa.get('telefono', ''),
                            empresa.get('email', ''),
                            empresa.get('horario', ''),
                            json.dumps(empresa.get('config', {}))
                        ))
        
        # Migrar configuraciones de cola desde cola_config.json
        if os.path.exists(config_file):
            print("📁 Migrando configuraciones de cola...")
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for empresa_id, config in config_data.items():
                if 'categorias' in config:
                    for categoria in config['categorias']:
                        cursor.execute('''
                            INSERT OR REPLACE INTO cola_categorias 
                            (id, empresa_id, nombre, descripcion, prioridad, tiempo_estimado, contador)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            categoria['id'],
                            empresa_id,
                            categoria['nombre'],
                            categoria.get('descripcion', ''),
                            categoria.get('prioridad', False),
                            categoria.get('tiempoEstimado', 5),
                            0  # Empezamos con contador en 0, se actualizará con los turnos
                        ))
        
        # Migrar turnos desde Queue.json
        if os.path.exists(queue_file):
            print("📁 Migrando turnos...")
            with open(queue_file, 'r', encoding='utf-8') as f:
                queue_data = json.load(f)
            
            for empresa_id, colas in queue_data.items():
                for categoria_id, cola_info in colas.items():
                    # Actualizar contador de la categoría
                    contador = cola_info.get('contador', 0)
                    cursor.execute('''
                        UPDATE cola_categorias 
                        SET contador = ?
                        WHERE id = ? AND empresa_id = ?
                    ''', (contador, categoria_id, empresa_id))
                    
                    # Insertar turnos
                    turnos = cola_info.get('turnos', [])
                    for i, turno in enumerate(turnos):
                        cursor.execute('''
                            INSERT OR REPLACE INTO turnos 
                            (id, categoria_id, empresa_id, nombre, numero, codigo, estado, posicion)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            turno['id'],
                            categoria_id,
                            empresa_id,
                            turno['nombre'],
                            turno['numero'],
                            turno.get('codigo', ''),
                            'en_espera',
                            i + 1  # Posición en la cola (1-indexed)
                        ))
        
        conn.commit()
        print("✅ Migración completada exitosamente")

def backup_json_files():
    """Crea backup de los archivos JSON antes de la migración"""
    backup_dir = 'json_backup'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    json_files = ['users.json', 'Queue.json', 'cola_config.json']
    for file in json_files:
        if os.path.exists(file):
            backup_path = os.path.join(backup_dir, f"{file}.backup")
            os.rename(file, backup_path)
            print(f"📦 Backup creado: {backup_path}")

if __name__ == "__main__":
    # Inicializar base de datos
    init_database()
    
    # Migrar datos existentes
    migrate_from_json()
    
    print("\n🎉 Configuración de base de datos completada!")
    print("La base de datos SQLite está lista para usar.")