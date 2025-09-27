#!/usr/bin/env python3
"""
Script de despliegue para TTOCA Backend en producción

Este script automatiza las tareas comunes de despliegue y mantenimiento.

Uso:
    python deploy.py <comando>

Comandos:
    setup      - Configuración inicial en servidor
    start      - Inicia el servidor en modo producción
    backup     - Crea backup antes del despliegue
    migrate    - Ejecuta migraciones si es necesario
    status     - Verifica el estado del sistema
    logs       - Muestra logs del sistema
"""

import os
import sys
import subprocess
import sqlite3
from datetime import datetime

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando y maneja errores"""
    print(f"⏳ {descripcion}...")
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {descripcion} completado")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Error en {descripcion}")
            print(f"   {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {descripcion}: {e}")
        return False

def setup_produccion():
    """Configuración inicial para producción"""
    print("🚀 Configurando TTOCA Backend para producción")
    print("=" * 50)
    
    # Verificar Python
    if not ejecutar_comando("python --version", "Verificando Python"):
        return False
    
    # Instalar dependencias
    if not ejecutar_comando("pip install -r requirements.txt", "Instalando dependencias"):
        return False
    
    # Verificar base de datos
    if not os.path.exists('ttoca.db'):
        print("📁 Base de datos no encontrada, ejecutando migración...")
        if not ejecutar_comando("python migrate.py", "Migrando datos"):
            return False
    
    # Verificar integridad
    if not ejecutar_comando("python admin.py check", "Verificando integridad de la base de datos"):
        return False
    
    # Configurar variables de entorno para producción
    env_content = """# Variables de entorno para TTOCA Backend Producción
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-super-segura-aqui
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env creado - ¡IMPORTANTE: Configura SECRET_KEY!")
    
    print("\n🎉 Configuración de producción completada")
    print("\n⚠️  IMPORTANTE:")
    print("   1. Configura SECRET_KEY en .env")
    print("   2. Verifica las URLs en config.py")
    print("   3. Configura tu servidor web (nginx, apache)")
    print("   4. Considera usar gunicorn para producción")
    
    return True

def crear_backup():
    """Crea backup antes del despliegue"""
    print("💾 Creando backup pre-despliegue...")
    
    # Backup usando la herramienta admin
    if not ejecutar_comando("python admin.py backup", "Creando backup de la base de datos"):
        return False
    
    # Backup adicional del archivo de base de datos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_db = f"ttoca_backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2('ttoca.db', backup_db)
        print(f"✅ Backup adicional creado: {backup_db}")
        return True
    except Exception as e:
        print(f"❌ Error creando backup de DB: {e}")
        return False

def iniciar_servidor():
    """Inicia el servidor en modo producción"""
    print("🚀 Iniciando servidor en modo producción...")
    
    # Verificar que gunicorn esté instalado
    result = subprocess.run("pip show gunicorn", shell=True, capture_output=True)
    if result.returncode != 0:
        print("📦 Instalando Gunicorn para producción...")
        if not ejecutar_comando("pip install gunicorn", "Instalando Gunicorn"):
            print("⚠️  Continuando con servidor Flask integrado...")
            comando_servidor = "python app.py"
        else:
            comando_servidor = "gunicorn -w 4 -b 0.0.0.0:5000 app:app"
    else:
        comando_servidor = "gunicorn -w 4 -b 0.0.0.0:5000 app:app"
    
    print(f"▶️  Ejecutando: {comando_servidor}")
    print("   Presiona Ctrl+C para detener")
    
    # Configurar variables de entorno
    env = os.environ.copy()
    env['FLASK_ENV'] = 'production'
    
    try:
        subprocess.run(comando_servidor, shell=True, env=env)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")

def verificar_estado():
    """Verifica el estado del sistema"""
    print("🔍 Verificando estado del sistema TTOCA")
    print("=" * 40)
    
    # Verificar base de datos
    if os.path.exists('ttoca.db'):
        print("✅ Base de datos encontrada")
        
        # Obtener estadísticas básicas
        try:
            conn = sqlite3.connect('ttoca.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            usuarios = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM empresas")
            empresas = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM turnos WHERE estado = 'en_espera'")
            turnos_activos = cursor.fetchone()[0]
            
            print(f"   📊 Usuarios: {usuarios}")
            print(f"   🏢 Empresas: {empresas}")
            print(f"   🎫 Turnos activos: {turnos_activos}")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Error obteniendo estadísticas: {e}")
    else:
        print("❌ Base de datos no encontrada")
        return False
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias...")
    if ejecutar_comando("pip check", "Verificando dependencias"):
        print("✅ Todas las dependencias están correctas")
    
    # Verificar configuración
    print("\n⚙️  Verificando configuración...")
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
    else:
        print("⚠️  Archivo .env no encontrado (opcional)")
    
    return True

def mostrar_logs():
    """Muestra logs del sistema"""
    print("📋 Logs del Sistema")
    print("=" * 20)
    
    # Ejecutar verificación de integridad
    ejecutar_comando("python admin.py check", "Verificación de integridad")
    
    # Mostrar estadísticas
    ejecutar_comando("python admin.py stats", "Estadísticas del sistema")

def mostrar_ayuda():
    """Muestra la ayuda"""
    print(__doc__)

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        mostrar_ayuda()
        return
    
    comando = sys.argv[1].lower()
    
    comandos = {
        'setup': setup_produccion,
        'start': iniciar_servidor,
        'backup': crear_backup,
        'migrate': lambda: ejecutar_comando("python migrate.py", "Ejecutando migración"),
        'status': verificar_estado,
        'logs': mostrar_logs,
        'help': mostrar_ayuda
    }
    
    if comando in comandos:
        try:
            resultado = comandos[comando]()
            if resultado is False:
                print("\n❌ El comando falló")
                sys.exit(1)
        except Exception as e:
            print(f"\n💥 Error ejecutando '{comando}': {e}")
            sys.exit(1)
    else:
        print(f"❌ Comando desconocido: {comando}")
        print("Usa 'python deploy.py help' para ver comandos disponibles")
        sys.exit(1)

if __name__ == "__main__":
    main()