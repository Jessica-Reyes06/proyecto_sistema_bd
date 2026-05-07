import os
import mysql.connector

# Leer contraseña desde variable de entorno
conexion = mysql.connector.connect(
    host="mainline.proxy.rlwy.net",
    port=33989,
    user="root",
    password="eCjzlyNIPozVeLnSIFfMVLiaeAJRURPE",
    database="db_escolar"
)

print("Conectado a MySQL - Base de datos: db_escolar")


def ejecutar_insert(sql, datos):
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    cursor.close()


def ejecutar_select(sql, params=None):
    cursor = conexion.cursor()
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


def crear_tablas_nuevas():
    """Crea todas las tablas necesarias para el sistema si no existen"""
    # La función de creación automática de tablas se ha eliminado.
    # Si necesita restaurarla en el futuro, reimplemente aquí.


# La llamada automática a `crear_tablas_nuevas()` fue eliminada intencionalmente.
