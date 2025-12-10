#!/usr/bin/env python3
"""
Herramienta de administración de la base de datos TTOCA

Este script proporciona comandos útiles para administrar la base de datos SQLite.

Uso:
    python scripts/admin.py <comando> [opciones]

Comandos disponibles:
    stats              - Muestra estadísticas generales del sistema
    clean              - Limpia turnos antiguos
    activity           - Muestra actividad por empresa
    check              - Verifica integridad de la base de datos
    repair             - Repara posiciones de colas
    backup             - Crea backup completo en JSON
    help               - Muestra esta ayuda
"""

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from services.admin_service import (
    obtener_estadisticas_generales,
    limpiar_turnos_completados,
    obtener_actividad_por_empresa,
    verificar_integridad_base_datos,
    reparar_posiciones_cola,
    exportar_backup_completo
)

def mostrar_ayuda():
    """Muestra la ayuda del comando"""
    print(__doc__)

def mostrar_estadisticas():
    """Muestra estadísticas generales del sistema"""
    print("📊 Estadísticas Generales del Sistema")
    print("=" * 40)
    
    stats = obtener_estadisticas_generales()
    if not stats:
        print("❌ Error al obtener estadísticas")
        return
    
    print(f"👤 Usuarios totales: {stats['usuarios_totales']}")
    print(f"🏢 Empresas totales: {stats['empresas_totales']}")
    print(f"📋 Categorías totales: {stats['categorias_totales']}")
    print(f"🎫 Turnos activos: {stats['turnos_activos']}")
    print(f"✅ Turnos atendidos hoy: {stats['turnos_atendidos_hoy']}")
    print(f"📈 Turnos atendidos esta semana: {stats['turnos_atendidos_semana']}")
    print(f"🏆 Empresa más activa: {stats['empresa_mas_activa']['nombre']} ({stats['empresa_mas_activa']['turnos_hoy']} turnos hoy)")

def limpiar_turnos():
    """Limpia turnos antiguos"""
    dias = 1
    if len(sys.argv) > 2:
        try:
            dias = int(sys.argv[2])
        except ValueError:
            print("❌ El número de días debe ser un entero")
            return
    
    print(f"🧹 Limpiando turnos completados de hace más de {dias} días...")
    
    resultado = limpiar_turnos_completados(dias)
    if not resultado:
        print("❌ Error al limpiar turnos")
        return
    
    print(f"✅ Turnos eliminados: {resultado['turnos_eliminados']}")
    print(f"✅ Turnos actuales eliminados: {resultado['turnos_actuales_eliminados']}")

def mostrar_actividad():
    """Muestra actividad por empresa"""
    print("🏢 Actividad por Empresa")
    print("=" * 50)
    
    empresas = obtener_actividad_por_empresa()
    if not empresas:
        print("❌ Error al obtener actividad por empresa")
        return
    
    if not empresas:
        print("ℹ️  No hay empresas registradas")
        return
    
    for empresa in empresas:
        print(f"\n📍 {empresa['nombre']} ({empresa['user_email']})")
        print(f"   📋 Categorías: {empresa['categorias']}")
        print(f"   🎫 Turnos activos: {empresa['turnos_activos']}")
        print(f"   📅 Turnos hoy: {empresa['turnos_hoy']}")
        print(f"   📊 Turnos esta semana: {empresa['turnos_semana']}")

def verificar_integridad():
    """Verifica la integridad de la base de datos"""
    print("🔍 Verificando Integridad de la Base de Datos")
    print("=" * 45)
    
    resultado = verificar_integridad_base_datos()
    if not resultado:
        print("❌ Error al verificar integridad")
        return
    
    if resultado['integridad_ok']:
        print("✅ La base de datos está íntegra")
    else:
        print(f"⚠️  Se encontraron {len(resultado['problemas'])} problema(s):")
        for problema in resultado['problemas']:
            print(f"\n🚨 {problema['tipo']}: {problema['cantidad']} registro(s)")
            if problema['cantidad'] <= 5:  # Mostrar detalles solo si son pocos
                for detalle in problema['detalles']:
                    print(f"   - {detalle}")

def reparar_colas():
    """Repara las posiciones de las colas"""
    print("🔧 Reparando Posiciones de Colas")
    print("=" * 35)
    
    resultado = reparar_posiciones_cola()
    if not resultado:
        print("❌ Error al reparar posiciones")
        return
    
    print(f"✅ {resultado['mensaje']}")

def crear_backup():
    """Crea un backup completo"""
    print("💾 Creando Backup Completo")
    print("=" * 25)
    
    resultado = exportar_backup_completo()
    if not resultado:
        print("❌ Error al crear backup")
        return
    
    print(f"✅ Backup creado: {resultado['archivo']}")
    print("\n📊 Registros exportados:")
    for tipo, cantidad in resultado['registros_exportados'].items():
        print(f"   {tipo}: {cantidad}")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        mostrar_ayuda()
        return
    
    comando = sys.argv[1].lower()
    
    comandos = {
        'stats': mostrar_estadisticas,
        'estadisticas': mostrar_estadisticas,
        'clean': limpiar_turnos,
        'limpiar': limpiar_turnos,
        'activity': mostrar_actividad,
        'actividad': mostrar_actividad,
        'check': verificar_integridad,
        'verificar': verificar_integridad,
        'repair': reparar_colas,
        'reparar': reparar_colas,
        'backup': crear_backup,
        'help': mostrar_ayuda,
        'ayuda': mostrar_ayuda
    }
    
    if comando in comandos:
        try:
            comandos[comando]()
        except Exception as e:
            print(f"❌ Error al ejecutar comando '{comando}': {e}")
    else:
        print(f"❌ Comando desconocido: {comando}")
        print("Usa 'python admin.py help' para ver los comandos disponibles")

if __name__ == "__main__":
    main()