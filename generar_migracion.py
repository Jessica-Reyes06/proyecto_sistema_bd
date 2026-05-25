# -*- coding: utf-8 -*-
"""
Script para generar migracion completa de MySQL a PostgreSQL
Incluye estructura de tablas y todos los datos
"""
import mysql.connector
import json
import sys
from datetime import datetime

# Configurar codificacion para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Configuracion MySQL
config_mysql = {
    "host": "viaduct.proxy.rlwy.net",
    "port": 56578,
    "user": "root",
    "password": "JcDUGyUdJGdIVdoZljhHhfDlnpwfLEgP",
    "database": "db_escolar"
}

# Mapeo de tipos MySQL a PostgreSQL
TIPOS_MYSQL_a_POSTGRES = {
    'int': 'INTEGER',
    'varchar': 'VARCHAR',
    'text': 'TEXT',
    'decimal': 'NUMERIC',
    'datetime': 'TIMESTAMP',
    'date': 'DATE',
    'year': 'INTEGER',  # PostgreSQL no tiene YEAR
    'tinyint': 'SMALLINT',
    'smallint': 'SMALLINT',
    'bigint': 'BIGINT',
    'float': 'DOUBLE PRECISION',
    'double': 'DOUBLE PRECISION',
    'boolean': 'BOOLEAN',
    'enum': 'VARCHAR(50)',  # Simplificacion
}

def convertir_tipo(tipo_mysql):
    """Convierte tipo de MySQL a PostgreSQL"""
    tipo_mysql = tipo_mysql.lower()
    for mysql_type, postgres_type in TIPOS_MYSQL_a_POSTGRES.items():
        if mysql_type in tipo_mysql:
            # Extraer parametros si existen (ej: varchar(100))
            if '(' in tipo_mysql and mysql_type in ['varchar', 'decimal', 'numeric', 'char']:
                return tipo_mysql.replace(mysql_type, postgres_type)
            return postgres_type
    return 'TEXT'  # Default fallback

def generar_create_table(nombre_tabla, columnas, foreign_keys):
    """Genera sentencia CREATE TABLE para PostgreSQL"""
    # Usar minúsculas para evitar problemas con mayúsculas/minúsculas en PostgreSQL
    nombre_tabla_lower = nombre_tabla.lower()

    sql = f"-- Tabla: {nombre_tabla}\n"
    sql += f"DROP TABLE IF EXISTS \"{nombre_tabla_lower}\" CASCADE;\n"
    sql += f"CREATE TABLE \"{nombre_tabla_lower}\" (\n"

    columnas_sql = []
    primary_key = None

    for columna in columnas:
        nombre = columna[0]
        tipo_mysql = columna[1]
        nulo = columna[2]
        clave = columna[3] if len(columna) > 3 else ''
        default = columna[4] if len(columna) > 4 else None
        extra = columna[5] if len(columna) > 5 else ''

        # Convertir tipo
        tipo_postgres = convertir_tipo(tipo_mysql)

        # Construir definicion de columna
        col_def = f'    "{nombre}" {tipo_postgres}'

        # NULL/NOT NULL
        if nulo == 'NO':
            col_def += ' NOT NULL'

        # Auto increment → SERIAL
        if 'auto_increment' in extra.lower():
            if tipo_mysql == 'int':
                col_def = f'    "{nombre}" SERIAL PRIMARY KEY'
            else:
                col_def += ' PRIMARY KEY'
            primary_key = nombre

        # Default value
        if default and default != 'NULL':
            if default == 'CURRENT_TIMESTAMP':
                col_def += ' DEFAULT CURRENT_TIMESTAMP'
            else:
                col_def += f" DEFAULT {default}"

        # Primary Key
        if clave == 'PRI' and primary_key is None:
            col_def += ' PRIMARY KEY'
            primary_key = nombre

        columnas_sql.append(col_def)

    # Foreign Keys
    for fk in foreign_keys:
        columna, tabla_ref, columna_ref = fk
        fk_def = f'    FOREIGN KEY ("{columna}") REFERENCES "{tabla_ref.lower()}" ("{columna_ref}")'
        columnas_sql.append(fk_def)

    sql += ',\n'.join(columnas_sql)
    sql += "\n);\n\n"

    return sql

def generar_insert_data(nombre_tabla, columnas, datos):
    """Genera sentencias INSERT para PostgreSQL"""
    nombre_tabla_lower = nombre_tabla.lower()

    if not datos:
        return f"-- Sin datos para {nombre_tabla}\n\n"

    sql = f"-- Datos para tabla: {nombre_tabla}\n"

    nombres_columnas = [col[0] for col in columnas]
    columnas_str = ', '.join([f'"{col}"' for col in nombres_columnas])

    for fila in datos:
        valores = []
        for valor in fila:
            if valor is None:
                valores.append('NULL')
            elif isinstance(valor, str):
                # Escapar comillas simples
                valor_escapado = valor.replace("'", "''")
                valores.append(f"'{valor_escapado}'")
            elif isinstance(valor, datetime):
                valores.append(f"'{valor.strftime('%Y-%m-%d %H:%M:%S')}'")
            else:
                valores.append(str(valor))

        valores_str = ', '.join(valores)
        sql += f'INSERT INTO "{nombre_tabla_lower}" ({columnas_str}) VALUES ({valores_str});\n'

    sql += '\n'
    return sql

def main():
    print("=" * 80)
    print("GENERANDO SCRIPT DE MIGRACION MYSQL → POSTGRESQL")
    print("=" * 80)

    try:
        # Conectar a MySQL
        print("\n[1/5] Conectando a MySQL...")
        conn = mysql.connector.connect(**config_mysql)
        cursor = conn.cursor()
        print("[OK] Conexion exitosa")

        # Obtener lista de tablas
        print("\n[2/5] Obteniendo tablas...")
        cursor.execute("SHOW TABLES")
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        print(f"[OK] {len(tablas)} tablas encontradas")

        # Ordenar tablas por dependencias (tablas sin FK primero)
        print("\n[3/5] Analizando dependencias...")
        estructura = {}

        for tabla in tablas:
            cursor.execute(f"DESCRIBE {tabla}")
            columnas = cursor.fetchall()

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

            estructura[tabla] = {
                'columnas': columnas,
                'foreign_keys': foreign_keys,
                'tiene_fk': len(foreign_keys) > 0
            }

        # Ordenamiento topológico real
        def ordenamiento_topologico():
            """Implementa ordenamiento topológico para respetar dependencias"""
            # Crear grafo de dependencias
            dependencias = {tabla: set() for tabla in tablas}

            for tabla in tablas:
                for fk in estructura[tabla]['foreign_keys']:
                    tabla_ref = fk[1]
                    if tabla_ref in dependencias:
                        dependencias[tabla].add(tabla_ref)

            # Algoritmo de Kahn
            grados_entrada = {tabla: len(deps) for tabla, deps in dependencias.items()}
            cola = [tabla for tabla, grado in grados_entrada.items() if grado == 0]
            resultado = []

            while cola:
                cola.sort()  # Orden alfabético entre nodos con mismo grado
                nodo = cola.pop(0)
                resultado.append(nodo)

                # Reducir grado de entrada de nodos dependientes
                for tabla, deps in dependencias.items():
                    if nodo in deps:
                        grados_entrada[tabla] -= 1
                        if grados_entrada[tabla] == 0:
                            cola.append(tabla)

            # Si hay ciclos, agregar tablas restantes al final
            for tabla in tablas:
                if tabla not in resultado:
                    resultado.append(tabla)

            return resultado

        tablas_ordenadas = ordenamiento_topologico()

        print(f"[OK] Orden calculado: {len(tablas_ordenadas)} tablas")

        # Generar script SQL
        print("\n[4/5] Generando script SQL...")
        nombre_archivo_sql = 'migracion_mysql_postgres.sql'

        with open(nombre_archivo_sql, 'w', encoding='utf-8') as f:
            # Cabecera
            f.write("-- ==================================================\n")
            f.write("-- MIGRACION MYSQL → POSTGRESQL\n")
            f.write(f"-- Base de datos: {config_mysql['database']}\n")
            f.write(f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Total tablas: {len(tablas)}\n")
            f.write("-- ==================================================\n\n")

            # Nota: No desactivamos triggers porque Heroku no tiene permisos de superusuario

            # CREATE TABLEs
            f.write("-- ==================================================\n")
            f.write("-- ESTRUCTURA DE TABLAS\n")
            f.write("-- ==================================================\n\n")

            for tabla in tablas_ordenadas:
                info = estructura[tabla]
                create_sql = generar_create_table(tabla, info['columnas'], info['foreign_keys'])
                f.write(create_sql)
                print(f"   CREATE TABLE: {tabla}")

            # INSERT DATA
            f.write("\n-- ==================================================\n")
            f.write("-- MIGRACION DE DATOS\n")
            f.write("-- ==================================================\n\n")

            total_filas = 0
            for tabla in tablas_ordenadas:
                cursor.execute(f"SELECT * FROM {tabla}")
                datos = cursor.fetchall()

                if datos:
                    info = estructura[tabla]
                    insert_sql = generar_insert_data(tabla, info['columnas'], datos)
                    f.write(insert_sql)
                    total_filas += len(datos)
                    print(f"   INSERT {len(datos)} filas: {tabla}")

            # Nota: No reactivamos triggers (Heroku no tiene permisos de superusuario)

            # Reset sequences
            f.write("-- ==================================================\n")
            f.write("-- RESET SECUENCIAS (SERIAL)\n")
            f.write("-- ==================================================\n\n")

            for tabla in tablas:
                info = estructura[tabla]
                # Buscar columna SERIAL (auto_increment)
                for col in info['columnas']:
                    if len(col) > 5 and 'auto_increment' in col[5].lower():
                        nombre_col = col[0]
                        tabla_lower = tabla.lower()
                        f.write(f"SELECT setval('\"{tabla_lower}_{nombre_col}_seq\"', (SELECT COALESCE(MAX(\"{nombre_col}\"), 1) FROM \"{tabla_lower}\"));\n")
                        break

            f.write("\n-- ==================================================\n")
            f.write("-- MIGRACION COMPLETADA\n")
            f.write(f"-- Total tablas: {len(tablas)}\n")
            f.write(f"-- Total filas migradas: {total_filas}\n")
            f.write("-- ==================================================\n")

        print(f"[OK] Script guardado en: {nombre_archivo_sql}")

        # Cerrar conexion
        cursor.close()
        conn.close()

        # Resumen
        print("\n[5/5] RESUMEN:")
        print(f"   - Tablas migradas: {len(tablas)}")
        print(f"   - Total filas: {total_filas}")
        print(f"   - Archivo SQL: {nombre_archivo_sql}")
        print(f"   - Tamano approx: {len(open(nombre_archivo_sql, 'r', encoding='utf-8').read()) // 1024} KB")

        print("\n" + "=" * 80)
        print("MIGRACION GENERADA EXITOSAMENTE")
        print("=" * 80)
        print("\nPara ejecutar la migracion en PostgreSQL:")
        print("1. Conectate a tu base de datos PostgreSQL en Heroku")
        print("2. Ejecuta: psql -h HOST -U USUARIO -d BASE_DATOS -f migracion_mysql_postgres.sql")
        print("O usa pgAdmin/DBeaver para ejecutar el archivo SQL")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
