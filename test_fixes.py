#!/usr/bin/env python3
"""
Script de prueba para verificar las correcciones de concurrencia en la base de datos.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection
from db_cola_utils import agregar_turno, siguiente_turno, obtener_turnos, obtener_turno_actual
import json

def test_database_fixes():
    """Prueba las correcciones de la base de datos"""
    
    print("🧪 Iniciando pruebas de correcciones de base de datos...")
    print("=" * 60)
    
    # IDs de prueba (usa los de tu base de datos real)
    empresa_id = "test_empresa"
    categoria_id = "test_categoria"
    
    try:
        # Test 1: Verificar que podemos obtener una conexión
        print("\n✓ Test 1: Verificando conexión a base de datos...")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM empresas")
            result = cursor.fetchone()
            print(f"  → Empresas en BD: {result['count']}")
        
        # Test 2: Verificar que existen empresas y categorías
        print("\n✓ Test 2: Listando empresas y categorías...")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, nombre FROM empresas LIMIT 5")
            empresas = cursor.fetchall()
            if empresas:
                print(f"  → Encontradas {len(empresas)} empresas:")
                for emp in empresas:
                    print(f"    - {emp['nombre']} ({emp['id']})")
                    
                # Usar la primera empresa para pruebas
                empresa_id = empresas[0]['id']
                
                # Buscar categorías de esta empresa
                cursor.execute("SELECT id, nombre FROM cola_categorias WHERE empresa_id = ?", (empresa_id,))
                categorias = cursor.fetchall()
                if categorias:
                    print(f"  → Encontradas {len(categorias)} categorías para {empresas[0]['nombre']}:")
                    for cat in categorias:
                        print(f"    - {cat['nombre']} ({cat['id']})")
                    categoria_id = categorias[0]['id']
                else:
                    print("  ⚠ No se encontraron categorías. Usa el frontend para crear una.")
                    return
            else:
                print("  ⚠ No se encontraron empresas. Crea una empresa desde el frontend.")
                return
        
        # Test 3: Listar turnos existentes
        print(f"\n✓ Test 3: Listando turnos existentes para categoría {categoria_id}...")
        turnos = obtener_turnos(empresa_id, categoria_id)
        print(f"  → Turnos en espera: {len(turnos)}")
        for turno in turnos[:3]:  # Mostrar solo los primeros 3
            print(f"    - Turno #{turno['numero']}: {turno['nombre']} (pos: {turno['posicion']})")
        
        # Test 4: Verificar turno actual
        print(f"\n✓ Test 4: Verificando turno actual...")
        turno_actual = obtener_turno_actual(empresa_id, categoria_id)
        if turno_actual:
            print(f"  → Turno actual: #{turno_actual['numero']} - {turno_actual['nombre']}")
        else:
            print("  → No hay turno actual (correcto si no se ha llamado ninguno)")
        
        # Test 5: Crear un turno de prueba
        print(f"\n✓ Test 5: Creando turno de prueba...")
        nuevo_turno = agregar_turno(empresa_id, categoria_id, {
            "nombre": "Test Automático",
            "tipo": "General"
        })
        if nuevo_turno:
            print(f"  → Turno creado: #{nuevo_turno['numero']} - {nuevo_turno['nombre']}")
            print(f"  → Código: {nuevo_turno['codigo']}")
        else:
            print("  ✗ Error al crear turno")
        
        # Test 6: Verificar que el turno aparece en la lista
        print(f"\n✓ Test 6: Verificando que el turno aparece en la lista...")
        turnos_despues = obtener_turnos(empresa_id, categoria_id)
        print(f"  → Turnos en espera ahora: {len(turnos_despues)}")
        
        # Test 7: Llamar al siguiente turno (si hay turnos)
        if turnos_despues:
            print(f"\n✓ Test 7: Llamando al siguiente turno...")
            turno_llamado = siguiente_turno(empresa_id, categoria_id)
            if turno_llamado:
                print(f"  → Turno llamado: #{turno_llamado['numero']} - {turno_llamado['nombre']}")
                
                # Verificar que ahora es el turno actual
                turno_actual_nuevo = obtener_turno_actual(empresa_id, categoria_id)
                if turno_actual_nuevo and turno_actual_nuevo['id'] == turno_llamado['id']:
                    print("  ✓ El turno ahora aparece como turno actual (¡CORRECTO!)")
                else:
                    print("  ✗ El turno NO aparece como turno actual (ERROR)")
                
                # Verificar que los turnos restantes tienen posiciones correctas
                turnos_finales = obtener_turnos(empresa_id, categoria_id)
                print(f"  → Turnos restantes: {len(turnos_finales)}")
                posiciones_correctas = all(
                    turno['posicion'] == i + 1 
                    for i, turno in enumerate(turnos_finales)
                )
                if posiciones_correctas:
                    print("  ✓ Las posiciones están correctas (¡CORRECTO!)")
                else:
                    print("  ✗ Las posiciones NO están correctas (ERROR)")
        else:
            print("\n  ⚠ No hay turnos para llamar")
        
        print("\n" + "=" * 60)
        print("✅ Pruebas completadas!")
        print("\nSi ves '¡CORRECTO!' en los tests 7, entonces las correcciones funcionan.")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_fixes()
