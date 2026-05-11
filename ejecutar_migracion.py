# -*- coding: utf-8 -*-
"""
Script para ejecutar automaticamente la migracion en PostgreSQL
Lee el archivo SQL generado y lo ejecuta en la base de datos PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Configurar codificacion para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Cargar variables de entorno
load_dotenv()

print("=" * 80)
print("EJECUTANDO MIGRACION EN POSTGRESQL")
print("=" * 80)
print(f"Host: {os.getenv('DB_HOST')}")
print(f"Base de datos: {os.getenv('DB_NAME')}")
print()

try:
    # Conectar a PostgreSQL
    print("[1/4] Conectando a PostgreSQL...")
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()
    print("[OK] Conexion exitosa a PostgreSQL")

    # Leer archivo SQL
    print("\n[2/4] Leyendo archivo SQL...")
    with open('migracion_mysql_postgres.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    print(f"[OK] Archivo leido ({len(sql_script)} caracteres)")

    # Dividir en sentencias individuales
    print("\n[3/4] Ejecutando migracion...")

    # Ejecutar cada sentencia
    # Dividir por ; pero ignorar comentarios
    sentencias = []
    sentencia_actual = []
    in_comment = False

    for linea in sql_script.split('\n'):
        stripped = linea.strip()

        # Manejar comentarios
        if stripped.startswith('--'):
            continue
        if stripped.startswith('/*'):
            in_comment = True
            continue
        if stripped.endswith('*/'):
            in_comment = False
            continue
        if in_comment:
            continue

        sentencia_actual.append(linea)

        if stripped.endswith(';'):
            sentencia_completa = '\n'.join(sentencia_actual)
            if sentencia_completa.strip():
                sentencias.append(sentencia_completa)
            sentencia_actual = []

    # Ejecutar sentencias
    ejecutadas = 0
    errores = []

    for i, sentencia in enumerate(sentencias, 1):
        sentencia = sentencia.strip()
        if not sentencia or sentencia.startswith('--'):
            continue

        try:
            # Solo mostrar sentencias importantes
            if any(keyword in sentencia.upper() for keyword in ['CREATE TABLE', 'INSERT INTO', 'SETVAL', 'DROP TABLE']):
                if 'CREATE TABLE' in sentencia.upper():
                    tabla = sentencia.split('"')[1]
                    print(f"   Creando tabla: {tabla}")
                elif 'INSERT INTO' in sentencia.upper():
                    tabla = sentencia.split('"')[1]
                    if i % 10 == 0:  # Mostrar cada 10 inserts
                        print(f"   Insertando en: {tabla}...")

            cursor.execute(sentencia)
            ejecutadas += 1

        except Exception as e:
            if 'already exists' not in str(e):
                errores.append(f"Sentencia {i}: {e}")
                print(f"   [ERROR] {e}")

    # Commit
    conn.commit()

    print(f"\n[OK] {ejecutadas} sentencias ejecutadas")

    # Verificar tablas creadas
    print("\n[4/4] Verificando tablas...")
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tablas_creadas = [row[0] for row in cursor.fetchall()]
    print(f"[OK] {len(tablas_creadas)} tablas creadas:")
    for tabla in tablas_creadas:
        print(f"   - {tabla}")

    # Verificar registros
    print("\nVerificando registros:")
    for tabla in tablas_creadas:
        cursor.execute(f'SELECT COUNT(*) FROM "{tabla}"')
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   - {tabla}: {count} registros")

    print(f"\n[OK] Migracion completada")

    cursor.close()
    conn.close()

    if errores:
        print(f"\n[WARNING] {len(errores)} errores encontrados (ver arriba)")

    print("\n" + "=" * 80)
    print("MIGRACION COMPLETADA EXITOSAMENTE")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] Error durante la migracion: {e}")
    import traceback
    traceback.print_exc()

    print("\nSoluciones posibles:")
    print("1. Verifica que el archivo migracion_mysql_postgres.sql existe")
    print("2. Verifica que las credenciales en .env sean correctas")
    print("3. Verifica que la base de datos PostgreSQL este accessible")
