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


def crear_tablas_nuevas():
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS actividades (
                id_actividad INT AUTO_INCREMENT PRIMARY KEY,
                tipo_actividad VARCHAR(150) NOT NULL,
                unidad VARCHAR(50) NOT NULL,
                id_grupo VARCHAR(50) NOT NULL,
                materia VARCHAR(150) NOT NULL,
                ponderacion VARCHAR(50) NOT NULL,
                detalles TEXT NOT NULL
            )
            """
        )
        conexion.commit()
        print("Tabla 'actividades' verificada")
    except Exception as e:
        print(f"No se pudo verificar la tabla 'actividades': {e}")
    finally:
        cursor.close()


crear_tablas_nuevas()


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
