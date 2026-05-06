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
    """Crea las tablas necesarias para los CRUD si no existen"""

    cursor = conexion.cursor()

    # Tabla de tipos_actividades (si no existe) - NECESARIA ANTES QUE calificaciones_actividades
    sql_tipos_actividades = """
    CREATE TABLE IF NOT EXISTS tipos_actividades (
        id_tipo INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100)
    )
    """

    # Tabla de salones
    sql_salones = """
    CREATE TABLE IF NOT EXISTS salones (
        id_salon VARCHAR(20) PRIMARY KEY,
        nombre_salon VARCHAR(100),
        capacidad INT,
        tipo VARCHAR(50),
        edificio VARCHAR(50),
        piso INT,
        estatus VARCHAR(50) DEFAULT 'Activo'
    )
    """

    # Tabla de calificaciones finales por periodo
    sql_calif_finales = """
    CREATE TABLE IF NOT EXISTS calificaciones_finales (
        id_calificacion INT AUTO_INCREMENT PRIMARY KEY,
        numero_control VARCHAR(8),
        id_grupo VARCHAR(20),
        calificacion_final DECIMAL(5,2),
        periodo VARCHAR(20),
        FOREIGN KEY (numero_control) REFERENCES alumnos(numero_control),
        FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo)
    )
    """

    # Tabla de calificaciones de actividades
    sql_calif_actividades = """
    CREATE TABLE IF NOT EXISTS calificaciones_actividades (
        id_calif_actividad INT AUTO_INCREMENT PRIMARY KEY,
        numero_control VARCHAR(8),
        id_actividad INT,
        calificacion DECIMAL(5,2),
        fecha_registro DATE,
        observaciones TEXT,
        FOREIGN KEY (numero_control) REFERENCES alumnos(numero_control),
        FOREIGN KEY (id_actividad) REFERENCES tipos_actividades(id_tipo)
    )
    """

    # Tabla de horarios (si no existe)
    sql_horario = """
    CREATE TABLE IF NOT EXISTS horario (
        id_horario INT AUTO_INCREMENT PRIMARY KEY,
        id_grupo VARCHAR(20),
        dia VARCHAR(20),
        hora_inicio TIME,
        hora_fin TIME,
        id_salon VARCHAR(20),
        FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo),
        FOREIGN KEY (id_salon) REFERENCES salones(id_salon)
    )
    """

    try:
        # PRIMERO crear tipos_actividades (si no existe)
        cursor.execute(sql_tipos_actividades)
        print("✓ Tabla 'tipos_actividades' verificada/creada")

        # Verificar y agregar columna id_registro a tabla registros si no existe
        cursor.execute("SHOW COLUMNS FROM registros LIKE 'id_registro'")
        if not cursor.fetchone():
            print("Agregando columna 'id_registro' a tabla 'registros'...")
            cursor.execute("ALTER TABLE registros ADD COLUMN id_registro INT AUTO_INCREMENT PRIMARY KEY FIRST")
            print("✓ Columna 'id_registro' agregada a 'registros'")

        cursor.execute(sql_salones)
        print("✓ Tabla 'salones' verificada/creada")

        cursor.execute(sql_calif_finales)
        print("✓ Tabla 'calificaciones_finales' verificada/creada")

        cursor.execute(sql_calif_actividades)
        print("✓ Tabla 'calificaciones_actividades' verificada/creada")

        cursor.execute(sql_horario)
        print("✓ Tabla 'horario' verificada/creada")

        conexion.commit()
        print("✓ Base de datos actualizada correctamente")

    except Exception as e:
        print(f"Error creando tablas: {e}")
        conexion.rollback()

    finally:
        cursor.close()


# Crear tablas nuevas automáticamente al iniciar (después de definir la función)
try:
    crear_tablas_nuevas()
except Exception as e:
    print(f"Advertencia: No se pudieron crear algunas tablas: {e}")
