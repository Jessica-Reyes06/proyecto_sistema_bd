import os
import mysql.connector

# Leer contraseña desde variable de entorno
conexion = mysql.connector.connect(
    host="mainline.proxy.rlwy.net",
    port=33989,
    user="root",
    password="eCjzlyNIPozVeLnSIFfMVLiaeAJRURPE",
    database="control_escolar"
)

print("Conectado a MySQL (db_conexion)")


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
