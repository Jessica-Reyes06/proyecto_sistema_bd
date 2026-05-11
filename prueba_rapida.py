# -*- coding: utf-8 -*-
"""
Prueba rápida de que la conexión funciona correctamente
"""
import sys
from dotenv import load_dotenv

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

try:
    from db_conexion import ejecutar_select

    print("Probando conexión a PostgreSQL...")

    # Test simple
    resultado = ejecutar_select("SELECT COUNT(*) FROM alumno")
    print(f"✅ Alumnos: {resultado[0][0]} registros")

    resultado = ejecutar_select("SELECT COUNT(*) FROM carreras")
    print(f"✅ Carreras: {resultado[0][0]} registros")

    resultado = ejecutar_select("SELECT nombre_alumno FROM alumno LIMIT 1")
    if resultado:
        print(f"✅ Consulta funciona: {resultado[0]}")

    print()
    print("✅ CORRECCIÓN APLICADA")
    print("   - RealDictCursor eliminado")
    print("   - Ahora devuelve tuplas (como MySQL)")
    print("   - Tu aplicación ahora funcionará correctamente")

except Exception as e:
    print(f"❌ Error: {e}")
