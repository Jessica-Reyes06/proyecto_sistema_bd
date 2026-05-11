import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Conexión a PostgreSQL
conexion = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

print(f"Conectado a PostgreSQL - Base de datos: {os.getenv('DB_NAME')}")


def ejecutar_insert(sql, datos):
    """Ejecuta una consulta INSERT con parámetros"""
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    cursor.close()


def ejecutar_select(sql, params=None):
    """Ejecuta una consulta SELECT con parámetros"""
    cursor = conexion.cursor()  # Sin RealDictCursor - devuelve tuplas como MySQL
    if params is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, params)
    resultado = cursor.fetchall()
    cursor.close()
    return resultado


def ejecutar_update(sql, valores):
    """Ejecuta una consulta UPDATE con parámetros"""
    cursor = conexion.cursor()
    cursor.execute(sql, valores)
    conexion.commit()
    cursor.close()


def ejecutar_delete(sql, valores):
    """Ejecuta una consulta DELETE con parámetros"""
    cursor = conexion.cursor()
    cursor.execute(sql, valores)
    conexion.commit()
    filas_afectadas = cursor.rowcount
    cursor.close()
    return filas_afectadas > 0


def ejecutar_select_todo(tabla):
    """Obtiene todos los registros de una tabla"""
    return ejecutar_select(f"SELECT * FROM {tabla}")


def obtener_registro_por_id(tabla, campo_id, valor_id):
    """Obtiene un registro específico por su ID"""
    return ejecutar_select(f"SELECT * FROM {tabla} WHERE {campo_id}=%s", (valor_id,))
