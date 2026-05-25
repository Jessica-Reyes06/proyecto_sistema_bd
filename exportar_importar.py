import csv
from db_conexion import conexion


def importar_csv(tabla, ruta_csv):
    with open(ruta_csv, newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        encabezados = next(lector)

        placeholders = ",".join(["%s"] * len(encabezados))
        columnas = ",".join(encabezados)

        sql = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"

        cursor = conexion.cursor()
        for fila in lector:
            cursor.execute(sql, fila)

        conexion.commit()
        cursor.close()


def exportar_csv(tabla, ruta_destino):
    cursor = conexion.cursor()
    cursor.execute(f"SELECT * FROM {tabla}")

    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]

    with open(ruta_destino, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(columnas)
        for fila in filas:
            escritor.writerow(fila)

    cursor.close()
