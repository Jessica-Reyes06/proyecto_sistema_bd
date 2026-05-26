# -*- coding: utf-8 -*-
"""
Script para limpiar todas las tablas de la base de datos PostgreSQL
"""
import sys
import os
from dotenv import load_dotenv
import psycopg2

# Configurar codificacion para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Cargar variables de entorno
load_dotenv()

print("=" * 80)
print("LIMPIANDO BASE DE DATOS POSTGRESQL")
print("=" * 80)

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()

    # Obtener todas las tablas del usuario
    cursor.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)
    tablas = [row[0] for row in cursor.fetchall()]

    print(f"\nEncontradas {len(tablas)} tablas:")
    for tabla in tablas:
        print(f"   - {tabla}")

    # Eliminar todas las tablas
    print("\nEliminando tablas...")
    for tabla in tablas:
        if not tabla.startswith('pg_'):
            cursor.execute(f'DROP TABLE IF EXISTS "{tabla}" CASCADE;')
            print(f"   Eliminada: {tabla}")

    conn.commit()

    print("\n[OK] Base de datos limpia")
    print("Ahora puedes ejecutar la migracion nuevamente")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
