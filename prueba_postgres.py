# -*- coding: utf-8 -*-
"""
Script para probar que la migracion funciona correctamente
Ejecuta consultas de prueba a PostgreSQL
"""
import sys
import os
from dotenv import load_dotenv

# Configurar codificacion para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Cargar variables de entorno
load_dotenv()

print("=" * 80)
print("PRUEBA DE CONEXION Y CONSULTAS A POSTGRESQL")
print("=" * 80)
print(f"Host: {os.getenv('DB_HOST')}")
print(f"Base de datos: {os.getenv('DB_NAME')}")
print()

try:
    # Importar despues de cargar .env
    from db_conexion import conexion, ejecutar_select, ejecutar_select_todo

    print("[OK] Modulo db_conexion importado correctamente")

    # Prueba 1: Contar registros por tabla
    print("\n[TEST 1] Contando registros por tabla...")
    tablas = ['Roles', 'Cuentas', 'Alumno', 'Maestro', 'Administrador',
              'Carreras', 'Materia', 'Grupo', 'Registro', 'Unidad', 'Actividad']

    total_registros = 0
    for tabla in tablas:
        try:
            resultado = ejecutar_select(f"SELECT COUNT(*) FROM {tabla}")
            count = resultado[0][0]
            total_registros += count
            if count > 0:
                print(f"   - {tabla}: {count} registros")
        except Exception as e:
            print(f"   - {tabla}: ERROR - {e}")

    print(f"\n[OK] Total de registros migrados: {total_registros}")

    # Prueba 2: Consultas con JOINs
    print("\n[TEST 2] Probando JOINs...")

    # JOIN Alumno con Carreras
    try:
        query = """
            SELECT a.nombre_alumno, c.nombre_carrera
            FROM Alumno a
            JOIN Carreras c ON a.id_carrera = c.id_carrera
            LIMIT 3
        """
        resultado = ejecutar_select(query)
        print(f"   Alumnos con Carreras ({len(resultado)} registros):")
        for fila in resultado[:3]:
            print(f"      - {fila[0]} → {fila[1]}")
    except Exception as e:
        print(f"   ERROR en JOIN Alumno-Carreras: {e}")

    # JOIN Maestro con Grupo
    try:
        query = """
            SELECT m.nombre_maestro, mat.nombre_materia
            FROM Maestro m
            JOIN Grupo g ON m.id_maestro = g.id_maestro
            JOIN Materia mat ON g.id_materia = mat.id_materia
            LIMIT 3
        """
        resultado = ejecutar_select(query)
        print(f"\n   Maestros con Materias ({len(resultado)} registros):")
        for fila in resultado[:3]:
            print(f"      - {fila[0]} → {fila[1]}")
    except Exception as e:
        print(f"   ERROR en JOIN Maestro-Materia: {e}")

    # Prueba 3: Consultas complejas
    print("\n[TEST 3] Consultas complejas...")

    try:
        # Contar alumnos por carrera
        query = """
            SELECT c.nombre_carrera, COUNT(a.id_alumno) as total
            FROM Carreras c
            LEFT JOIN Alumno a ON c.id_carrera = a.id_carrera
            GROUP BY c.nombre_carrera
            ORDER BY total DESC
        """
        resultado = ejecutar_select(query)
        print("   Alumnos por carrera:")
        for fila in resultado[:5]:
            print(f"      - {fila[0]}: {fila[1]} alumnos")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 80)
    print("PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("=" * 80)
    print("\nTu base de datos PostgreSQL esta lista para usar!")
    print("Puedes ejecutar tu aplicacion normalmente.")

    # Cerrar conexion
    if conexion:
        conexion.close()
        print("\nConexion cerrada.")

except Exception as e:
    print(f"\n[ERROR] Error durante las pruebas: {e}")
    import traceback
    traceback.print_exc()

    print("\nSoluciones posibles:")
    print("1. Verifica que el archivo .env exista y tenga las credenciales correctas")
    print("2. Verifica que la migracion se haya ejecutado correctamente")
    print("3. Verifica que psycopg2-binary y python-dotenv esten instalados")
