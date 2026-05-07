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

    cursor = conexion.cursor()

    # Tablas principales del sistema
    sql_alumnos = """
    CREATE TABLE IF NOT EXISTS alumnos (
        numero_control VARCHAR(8) PRIMARY KEY,
        nombre_alumno VARCHAR(100),
        apellido_paterno VARCHAR(100),
        apellido_materno VARCHAR(100),
        correo_alumno VARCHAR(100),
        carrera VARCHAR(100),
        semestre INT,
        estatus_alumno VARCHAR(50)
    )
    """

    sql_maestros = """
    CREATE TABLE IF NOT EXISTS maestros (
        matricula_maestro VARCHAR(20) PRIMARY KEY,
        nombre_maestro VARCHAR(100),
        apellido_paterno VARCHAR(100),
        apellido_materno VARCHAR(100),
        correo VARCHAR(100),
        estatus VARCHAR(50),
        grado_estudios VARCHAR(100),
        perfil_docente VARCHAR(100),
        carga_academica INT,
        tipo_contrato VARCHAR(50),
        cedula_profesional VARCHAR(50)
    )
    """

    sql_administradores = """
    CREATE TABLE IF NOT EXISTS administradores (
        matricula VARCHAR(20) PRIMARY KEY,
        nombre VARCHAR(100),
        apellido_paterno VARCHAR(100),
        apellido_materno VARCHAR(100),
        area VARCHAR(100),
        id_usuario VARCHAR(50)
    )
    """

    sql_usuarios = """
    CREATE TABLE IF NOT EXISTS usuarios (
        usuario VARCHAR(50) PRIMARY KEY,
        contrasena VARCHAR(100),
        rol VARCHAR(50)
    )
    """

    sql_carreras = """
    CREATE TABLE IF NOT EXISTS carreras (
        id_carrera INT AUTO_INCREMENT PRIMARY KEY,
        nombre_carrera VARCHAR(100),
        tipo_carrera VARCHAR(50),
        horas_semana INT,
        creditos INT
    )
    """

    sql_tipos_actividades = """
    CREATE TABLE IF NOT EXISTS tipos_actividades (
        id_tipo INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100)
    )
    """

    sql_materias = """
    CREATE TABLE IF NOT EXISTS materias (
        id_materia VARCHAR(20) PRIMARY KEY,
        nombre_materia VARCHAR(100),
        horas_semana INT,
        creditos INT,
        tipo VARCHAR(50)
    )
    """

    sql_grupos = """
    CREATE TABLE IF NOT EXISTS grupos (
        id_grupo VARCHAR(20) PRIMARY KEY,
        matricula_maestro VARCHAR(20),
        id_materia VARCHAR(20),
        cupo_maximo INT,
        estado VARCHAR(50),
        FOREIGN KEY (matricula_maestro) REFERENCES maestros(matricula_maestro),
        FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
    )
    """

    sql_registros = """
    CREATE TABLE IF NOT EXISTS registros (
        id_registro INT AUTO_INCREMENT PRIMARY KEY,
        numero_control VARCHAR(8),
        id_grupo VARCHAR(20),
        fecha_registro DATE,
        estatus_materia VARCHAR(50),
        tipo_registro VARCHAR(50),
        FOREIGN KEY (numero_control) REFERENCES alumnos(numero_control),
        FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo)
    )
    """

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

    tablas = [
        ("alumnos", sql_alumnos),
        ("maestros", sql_maestros),
        ("administradores", sql_administradores),
        ("usuarios", sql_usuarios),
        ("carreras", sql_carreras),
        ("tipos_actividades", sql_tipos_actividades),
        ("materias", sql_materias),
        ("grupos", sql_grupos),
        ("registros", sql_registros),
        ("salones", sql_salones),
        ("calificaciones_finales", sql_calif_finales),
        ("calificaciones_actividades", sql_calif_actividades),
        ("horario", sql_horario),
    ]

    try:
        print("\n📊 Creando/verificando tablas en db_escolar...")

        for nombre_tabla, sql in tablas:
            try:
                cursor.execute(sql)
                print(f"✓ Tabla '{nombre_tabla}' verificada/creada")
            except Exception as e:
                print(f"❌ Error creando tabla '{nombre_tabla}': {e}")

        conexion.commit()
        print("\n✓ Base de datos 'db_escolar' actualizada correctamente")

    except Exception as e:
        print(f"Error general creando tablas: {e}")
        conexion.rollback()

    finally:
        cursor.close()


# Crear tablas nuevas automáticamente al iniciar (después de definir la función)
try:
    crear_tablas_nuevas()
except Exception as e:
    print(f"Advertencia: No se pudieron crear algunas tablas: {e}")
