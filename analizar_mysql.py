# -*- coding: utf-8 -*-
"""
Script para analizar la estructura completa de MySQL en Railway
Y generar la documentación necesaria para la migración
"""
import mysql.connector
import json
import sys
from datetime import datetime

# Configurar codificacion para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Configuración MySQL
config_mysql = {
    "host": "viaduct.proxy.rlwy.net",
    "port": 56578,
    "user": "root",
    "password": "JcDUGyUdJGdIVdoZljhHhfDlnpwfLEgP",
    "database": "db_escolar"
}

print("=" * 80)
print("ANALIZANDO BASE DE DATOS MYSQL EN RAILWAY")
print("=" * 80)
print(f"Host: {config_mysql['host']}:{config_mysql['port']}")
print(f"Base de datos: {config_mysql['database']}")
print()

try:
    # Conectar a MySQL
    print("[1/6] Conectando a MySQL...")
    conexion = mysql.connector.connect(**config_mysql)
    cursor = conexion.cursor()
    print("[OK] Conexion exitosa a MySQL")

    # Obtener todas las tablas
    print("\n[2/6] Obteniendo lista de tablas...")
    cursor.execute("SHOW TABLES")
    tablas = [tabla[0] for tabla in cursor.fetchall()]
    print(f"✓ Encontradas {len(tablas)} tablas:")
    for i, tabla in enumerate(tablas, 1):
        print(f"   {i}. {tabla}")

    # Analizar cada tabla
    print("\n[3/6] Analizando estructura de cada tabla...")
    estructura_completa = {}

    for tabla in tablas:
        print(f"   Analizando: {tabla}")

        # Obtener estructura de la tabla
        cursor.execute(f"DESCRIBE {tabla}")
        columnas_info = cursor.fetchall()

        # Obtener informacion de claves foraneas
        try:
            cursor.execute(f"""
                SELECT
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = '{config_mysql['database']}'
                AND TABLE_NAME = '{tabla}'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            foreign_keys = cursor.fetchall()
        except:
            foreign_keys = []

        # Obtener count de registros
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cursor.fetchone()[0]

        estructura_completa[tabla] = {
            "columnas": columnas_info,
            "foreign_keys": foreign_keys,
            "num_registros": count
        }

    print("[OK] Estructura analizada correctamente")

    # Guardar en JSON
    print("\n[4/6] Guardando estructura en archivo JSON...")
    with open('estructura_mysql.json', 'w', encoding='utf-8') as f:
        json.dump(estructura_completa, f, indent=2, ensure_ascii=False, default=str)
    print("[OK] Guardado en: estructura_mysql.json")

    # Generar reporte
    print("\n[5/6] Generando reporte detallado...")
    with open('reporte_mysql.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("REPORTE DE BASE DE DATOS MYSQL - db_escolar\n")
        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        total_registros = 0

        for tabla, info in estructura_completa.items():
            f.write(f"\n{'=' * 80}\n")
            f.write(f"TABLA: {tabla}\n")
            f.write(f"Registros: {info['num_registros']}\n")
            f.write(f"{'=' * 80}\n\n")

            f.write("Columnas:\n")
            f.write(f"{'Nombre':<25} {'Tipo':<20} {'Nulo':<8} {'Clave':<10}\n")
            f.write("-" * 80 + "\n")

            for columna in info['columnas']:
                # columna = (Field, Type, Null, Key, Default, Extra)
                nombre = columna[0]
                tipo = columna[1]
                nulo = columna[2]
                clave = columna[3] if len(columna) > 3 else ''
                f.write(f"{nombre:<25} {tipo:<20} {nulo:<8} {clave:<10}\n")

            if info['foreign_keys']:
                f.write("\nClaves Foraneas:\n")
                for fk in info['foreign_keys']:
                    f.write(f"   {fk[0]} -> {fk[1]}.{fk[2]}\n")

            total_registros += info['num_registros']

        f.write(f"\n{'=' * 80}\n")
        f.write(f"TOTAL TABLAS: {len(tablas)}\n")
        f.write(f"TOTAL REGISTROS: {total_registros}\n")
        f.write("=" * 80 + "\n")

    print("[OK] Reporte guardado en: reporte_mysql.txt")

    # Mostrar resumen
    print("\n[6/6] RESUMEN:")
    print(f"   - Tablas encontradas: {len(tablas)}")

    total_registros = sum(info['num_registros'] for info in estructura_completa.values())
    print(f"   - Total registros: {total_registros}")

    print("\n   Top 5 tablas con mas datos:")
    tablas_ordenadas = sorted(
        estructura_completa.items(),
        key=lambda x: x[1]['num_registros'],
        reverse=True
    )
    for i, (tabla, info) in enumerate(tablas_ordenadas[:5], 1):
        print(f"      {i}. {tabla}: {info['num_registros']} registros")

    cursor.close()
    conexion.close()

    print("\n" + "=" * 80)
    print("ANALISIS COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print("\nArchivos generados:")
    print("   1. estructura_mysql.json - Estructura completa en formato JSON")
    print("   2. reporte_mysql.txt - Reporte legible")

except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
