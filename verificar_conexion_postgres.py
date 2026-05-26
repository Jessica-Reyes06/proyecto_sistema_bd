# -*- coding: utf-8 -*-
"""
Script para verificar la conexion a PostgreSQL en Heroku
"""
import os
import sys
from dotenv import load_dotenv

# Configurar codificacion para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Cargar variables de entorno
load_dotenv()

print("=== Verificando conexion a PostgreSQL ===")
print(f"Host: {os.getenv('DB_HOST')}")
print(f"Puerto: {os.getenv('DB_PORT')}")
print(f"Usuario: {os.getenv('DB_USER')}")
print(f"Base de datos: {os.getenv('DB_NAME')}")
print()

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    # Intentar conectar
    conexion = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    print("[OK] Conexion exitosa a PostgreSQL")

    # Probar una consulta simple
    cursor = conexion.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"Version de PostgreSQL: {version[0]}")

    # Listar tablas
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tablas = cursor.fetchall()
    print(f"\nTablas en la base de datos ({len(tablas)}):")
    for tabla in tablas:
        print(f"   - {tabla[0]}")

    cursor.close()
    conexion.close()

    print("\n[OK] Todo funciona correctamente")

except Exception as e:
    print(f"[ERROR] Error de conexion: {e}")
    print("\nSoluciones posibles:")
    print("1. Verifica que las credenciales en el archivo .env sean correctas")
    print("2. Instala las dependencias: pip install psycopg2-binary python-dotenv")
    print("3. Verifica que la base de datos este accessible desde tu ubicacion")
