#!/usr/bin/env python3
"""
Script de migración de JSON a SQLite para TTOCA Backend

Este script migra todos los datos existentes de archivos JSON a una base de datos SQLite.
- Crea backup de los archivos JSON originales
- Inicializa la estructura de la base de datos SQLite
- Migra todos los datos preservando la integridad
- Valida la migración comparando datos

Uso:
    python migrate.py
"""

import os
import json
import sqlite3
from datetime import datetime
from database import init_database, migrate_from_json, backup_json_files

def validar_migracion():
    """Valida que la migración se haya realizado correctamente"""
    print("\n🔍 Validando migración...")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('ttoca.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Contar usuarios
        cursor.execute("SELECT COUNT(*) as count FROM users")
        usuarios_count = cursor.fetchone()['count']
        print(f"✅ Usuarios migrados: {usuarios_count}")
        
        # Contar empresas
        cursor.execute("SELECT COUNT(*) as count FROM empresas")
        empresas_count = cursor.fetchone()['count']
        print(f"✅ Empresas migradas: {empresas_count}")
        
        # Contar categorías
        cursor.execute("SELECT COUNT(*) as count FROM cola_categorias")
        categorias_count = cursor.fetchone()['count']
        print(f"✅ Categorías de cola migradas: {categorias_count}")
        
        # Contar turnos
        cursor.execute("SELECT COUNT(*) as count FROM turnos")
        turnos_count = cursor.fetchone()['count']
        print(f"✅ Turnos migrados: {turnos_count}")
        
        # Mostrar algunos datos de ejemplo
        print("\n📊 Datos de ejemplo:")
        
        # Mostrar usuarios
        cursor.execute("SELECT email FROM users LIMIT 3")
        for row in cursor.fetchall():
            print(f"   👤 Usuario: {row['email']}")
        
        # Mostrar empresas
        cursor.execute("SELECT nombre, user_email FROM empresas LIMIT 3")
        for row in cursor.fetchall():
            print(f"   🏢 Empresa: {row['nombre']} (propietario: {row['user_email']})")
        
        # Mostrar categorías
        cursor.execute("SELECT cc.nombre, e.nombre as empresa FROM cola_categorias cc JOIN empresas e ON cc.empresa_id = e.id LIMIT 3")
        for row in cursor.fetchall():
            print(f"   📋 Categoría: {row['nombre']} en {row['empresa']}")
        
        conn.close()
        
        print("\n✅ Validación completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la validación: {e}")
        return False

def mostrar_comparacion():
    """Muestra una comparación entre los datos originales y migrados"""
    print("\n📈 Comparación de datos:")
    
    # Datos originales
    usuarios_json = 0
    empresas_json = 0
    categorias_json = 0
    turnos_json = 0
    
    # Contar datos en backups JSON
    backup_dir = 'json_backup'
    
    if os.path.exists(os.path.join(backup_dir, 'users.json.backup')):
        with open(os.path.join(backup_dir, 'users.json.backup'), 'r', encoding='utf-8') as f:
            users_data = json.load(f)
            usuarios_json = len(users_data)
            for user in users_data.values():
                if 'empresas' in user:
                    empresas_json += len(user['empresas'])
    
    if os.path.exists(os.path.join(backup_dir, 'cola_config.json.backup')):
        with open(os.path.join(backup_dir, 'cola_config.json.backup'), 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            for empresa_config in config_data.values():
                if 'categorias' in empresa_config:
                    categorias_json += len(empresa_config['categorias'])
    
    if os.path.exists(os.path.join(backup_dir, 'Queue.json.backup')):
        with open(os.path.join(backup_dir, 'Queue.json.backup'), 'r', encoding='utf-8') as f:
            queue_data = json.load(f)
            for empresa_colas in queue_data.values():
                for cola in empresa_colas.values():
                    turnos_json += len(cola.get('turnos', []))
    
    # Datos en SQLite
    conn = sqlite3.connect('ttoca.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    usuarios_sqlite = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM empresas")
    empresas_sqlite = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cola_categorias")
    categorias_sqlite = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM turnos")
    turnos_sqlite = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"   👤 Usuarios: JSON = {usuarios_json}, SQLite = {usuarios_sqlite}")
    print(f"   🏢 Empresas: JSON = {empresas_json}, SQLite = {empresas_sqlite}")
    print(f"   📋 Categorías: JSON = {categorias_json}, SQLite = {categorias_sqlite}")
    print(f"   🎫 Turnos: JSON = {turnos_json}, SQLite = {turnos_sqlite}")

def main():
    """Función principal de migración"""
    print("🚀 TTOCA Backend - Migración de JSON a SQLite")
    print("=" * 50)
    
    # Verificar si ya existe la base de datos
    if os.path.exists('ttoca.db'):
        respuesta = input("⚠️  La base de datos SQLite ya existe. ¿Desea recrearla? (s/N): ").lower()
        if respuesta == 's' or respuesta == 'si':
            os.remove('ttoca.db')
            print("🗑️  Base de datos anterior eliminada.")
        else:
            print("ℹ️  Usando base de datos existente.")
    
    try:
        # Paso 1: Crear backup de archivos JSON
        print("\n📦 Paso 1: Creando backup de archivos JSON...")
        backup_json_files()
        
        # Paso 2: Inicializar base de datos
        print("\n🏗️  Paso 2: Inicializando estructura de base de datos SQLite...")
        init_database()
        
        # Paso 3: Migrar datos
        print("\n🔄 Paso 3: Migrando datos de JSON a SQLite...")
        migrate_from_json()
        
        # Paso 4: Validar migración
        if validar_migracion():
            # Paso 5: Mostrar comparación
            mostrar_comparacion()
            
            print("\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
            print("\nℹ️  Información importante:")
            print("   📁 Los archivos JSON originales han sido movidos a 'json_backup/'")
            print("   🗄️  La nueva base de datos SQLite está en 'ttoca.db'")
            print("   🚀 El servidor ya está configurado para usar SQLite")
            print("   🧹 Los turnos antiguos se limpiarán automáticamente cada día")
            
            print("\n⚡ Próximos pasos:")
            print("   1. Ejecuta: python app.py")
            print("   2. Prueba tu aplicación para verificar que todo funciona")
            print("   3. Los archivos de backup se pueden eliminar después de verificar")
            
        else:
            print("\n❌ La migración falló durante la validación.")
            return False
            
    except Exception as e:
        print(f"\n💥 Error durante la migración: {e}")
        print("⚠️  Por favor, revisa los logs y contacta al soporte si el problema persiste.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ ¡Todo listo para usar tu nuevo backend con SQLite!")
    else:
        print("\n🚨 La migración no se completó correctamente.")
        exit(1)