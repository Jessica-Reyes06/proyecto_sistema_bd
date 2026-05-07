import os
import mysql.connector

# Primero conectarse sin especificar base de datos para crearla si no existe
try:
    conexion_temp = mysql.connector.connect(
        host="mainline.proxy.rlwy.net",
        port=33989,
        user="root",
        password="eCjzlyNIPozVeLnSIFfMVLiaeAJRURPE"
    )
    cursor_temp = conexion_temp.cursor()
    cursor_temp.execute("CREATE DATABASE IF NOT EXISTS db_escolar")
    cursor_temp.close()
    conexion_temp.close()
    print("✓ Base de datos 'db_escolar' verificada/creada")
except Exception as e:
    print(f"❌ Error al crear base de datos: {e}")

# Ahora conectarse a la base de datos db_escolar
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


def verificar_y_actualizar_columnas():
    """Verifica que todas las tablas tengan las columnas correctas y agrega las faltantes"""

    # Definición completa de tablas y sus columnas
    estructuras_tablas = {
        "Cuentas": [
            ("id_cuenta", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_rol", "INT"),
            ("password", "VARCHAR(255)")
        ],
        "Roles": [
            ("id_rol", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("nombre", "VARCHAR(100)")
        ],
        "Administrador": [
            ("id_administrador", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("matricula", "VARCHAR(20)"),
            ("nombre", "VARCHAR(100)"),
            ("apellido_paterno", "VARCHAR(100)"),
            ("apellido_materno", "VARCHAR(100)"),
            ("id_cuenta", "INT")
        ],
        "Alumno": [
            ("id_alumno", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_cuenta", "INT"),
            ("numero_control", "VARCHAR(8)"),
            ("nombre_alumno", "VARCHAR(100)"),
            ("apellido_paterno", "VARCHAR(100)"),
            ("apellido_materno", "VARCHAR(100)"),
            ("correo_alumno", "VARCHAR(100)"),
            ("id_carrera", "INT"),
            ("semestre", "INT"),
            ("estatus_alumno", "VARCHAR(50)")
        ],
        "Maestro": [
            ("id_maestro", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_cuenta", "INT"),
            ("matricula", "VARCHAR(20)"),
            ("nombre_maestro", "VARCHAR(100)"),
            ("apellido_paterno", "VARCHAR(100)"),
            ("apellido_materno", "VARCHAR(100)"),
            ("correo", "VARCHAR(100)"),
            ("estatus", "VARCHAR(50)"),
            ("grado_estudios", "VARCHAR(100)"),
            ("perfil_docente", "VARCHAR(100)"),
            ("carga_academica", "INT"),
            ("tipo_contrato", "VARCHAR(50)"),
            ("cedula_profesional", "VARCHAR(50)")
        ],
        "Carreras": [
            ("id_carrera", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("nombre_carrera", "VARCHAR(100)"),
            ("tipo_carrera", "VARCHAR(50)"),
            ("numero_semestres", "INT")
        ],
        "Solicitudes": [
            ("id_solicitud", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_cuenta", "INT"),
            ("motivo", "TEXT"),
            ("estado", "VARCHAR(50)"),
            ("id_administrador", "INT")
        ],
        "Grupo": [
            ("id_grupo", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_maestro", "INT"),
            ("id_materia", "INT"),
            ("cupo_maximo", "INT"),
            ("periodo", "VARCHAR(50)"),
            ("horario", "TEXT"),
            ("alumnos_inscritos", "INT DEFAULT 0")
        ],
        "Materia": [
            ("id_materia", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("clave", "VARCHAR(20)"),
            ("nombre_materia", "VARCHAR(100)"),
            ("horas_semana", "INT"),
            ("creditos", "INT"),
            ("id_carrera", "INT")
        ],
        "Registro": [
            ("id_registro", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_alumno", "INT"),
            ("id_grupo", "INT"),
            ("estatus_materia", "VARCHAR(50)"),
            ("tipo_registro", "VARCHAR(50)")
        ],
        "Unidad": [
            ("id_unidad", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_materia", "INT"),
            ("numero_unidad", "INT"),
            ("tema_unidad", "VARCHAR(200)"),
            ("descripcion", "TEXT")
        ],
        "BonusUnidad": [
            ("id_bonusUnidad", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_registro", "INT"),
            ("id_unidad", "INT"),
            ("valor", "DECIMAL(5,2)"),
            ("justificacion", "TEXT")
        ],
        "BonusMateria": [
            ("id_bonusMateria", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_registro", "INT"),
            ("valor", "DECIMAL(5,2)"),
            ("justificacion", "TEXT")
        ],
        "Calificacion_final": [
            ("id_final", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_registro", "INT"),
            ("calificacion", "DECIMAL(5,2)")
        ],
        "Calificaciones_unidad": [
            ("id_calificacion_unidad", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_registro", "INT"),
            ("id_unidad", "INT"),
            ("calificacion", "DECIMAL(5,2)"),
            ("intentos", "INT DEFAULT 1")
        ],
        "Resultado": [
            ("id_resultado", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_registro", "INT"),
            ("id_actividad", "INT"),
            ("calificacion", "DECIMAL(5,2)"),
            ("fecha_registro", "DATE"),
            ("observaciones", "TEXT")
        ],
        "Tipos_actividades": [
            ("id_tipo", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("nombre", "VARCHAR(100)")
        ],
        "Actividad": [
            ("id_actividad", "INT AUTO_INCREMENT PRIMARY KEY"),
            ("id_tipo", "INT"),
            ("id_unidad", "INT"),
            ("ponderacion", "DECIMAL(5,2)"),
            ("detalles", "TEXT")
        ]
    }

    cursor = conexion.cursor()

    try:
        print("\n🔍 Verificando y actualizando columnas de las tablas...")

        for nombre_tabla, columnas_esperadas in estructuras_tablas.items():
            # Verificar si la tabla existe
            cursor.execute(f"SHOW TABLES LIKE '{nombre_tabla}'")
            if not cursor.fetchone():
                print(f"⚠️  Tabla '{nombre_tabla}' no existe aún")
                continue

            # Obtener columnas actuales
            cursor.execute(f"DESCRIBE {nombre_tabla}")
            columnas_actuales = {fila[0]: fila[1] for fila in cursor.fetchall()}

            # Verificar y agregar columnas faltantes
            columnas_agregadas = []
            for nombre_columna, definicion in columnas_esperadas:
                if nombre_columna not in columnas_actuales:
                    try:
                        # Extraer tipo de dato (sin PRIMARY KEY, etc.)
                        tipo_dato = " ".join(definicion.split()[1:]) if " " in definicion else definicion

                        # Si es PRIMARY KEY, manejarlo diferente
                        if "PRIMARY KEY" in definicion.upper():
                            # Verificar si ya existe una primary key
                            cursor.execute(f"SHOW KEYS FROM {nombre_tabla} WHERE Key_name = 'PRIMARY'")
                            if not cursor.fetchone():
                                cursor.execute(f"ALTER TABLE {nombre_tabla} ADD COLUMN {nombre_columna} {tipo_dato}")
                                columnas_agregadas.append(nombre_columna)
                        else:
                            cursor.execute(f"ALTER TABLE {nombre_tabla} ADD COLUMN {nombre_columna} {tipo_dato}")
                            columnas_agregadas.append(nombre_columna)
                    except Exception as e:
                        print(f"  ⚠️  No se pudo agregar columna '{nombre_columna}' en '{nombre_tabla}': {e}")

            if columnas_agregadas:
                print(f"  ✓ Tabla '{nombre_tabla}': {len(columnas_agregadas)} columnas agregadas: {', '.join(columnas_agregadas)}")
            else:
                print(f"  ✓ Tabla '{nombre_tabla}': todas las columnas correctas")

        conexion.commit()
        print("\n✓ Verificación y actualización de columnas completada")

    except Exception as e:
        print(f"❌ Error verificando columnas: {e}")
        conexion.rollback()

    finally:
        cursor.close()


def eliminar_tablas_obsoletas():
    """Elimina las tablas que ya no se usan: Edificio, Salon, Horario"""
    cursor = conexion.cursor()

    tablas_obsoletas = ["Horario", "Salon", "Edificio"]

    try:
        print("\n🗑️  Verificando tablas obsoletas...")

        for tabla in tablas_obsoletas:
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            if cursor.fetchone():
                print(f"  ⚠️  Tabla '{tabla}' existe - eliminando...")
                cursor.execute(f"DROP TABLE {tabla}")
                print(f"  ✓ Tabla '{tabla}' eliminada")
            else:
                print(f"  ✓ Tabla '{tabla}' no existe (ok)")

        if any(tabla_obsoleta for tabla_obsoleta in tablas_obsoletas):
            conexion.commit()
            print("✓ Tablas obsoletas eliminadas correctamente")
        return True

    except Exception as e:
        print(f"  ⚠️  Error eliminando tablas obsoletas: {e}")
        conexion.rollback()
        return False

    finally:
        cursor.close()


def crear_tablas_nuevas():
    """Crea todas las tablas necesarias para el sistema si no existen"""

    cursor = conexion.cursor()

    # 1. Cuentas
    sql_cuentas = """
    CREATE TABLE IF NOT EXISTS Cuentas (
        id_cuenta INT AUTO_INCREMENT PRIMARY KEY,
        id_rol INT,
        password VARCHAR(255),
        FOREIGN KEY (id_rol) REFERENCES Roles(id_rol)
    )
    """

    # 2. Roles
    sql_roles = """
    CREATE TABLE IF NOT EXISTS Roles (
        id_rol INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100)
    )
    """

    # 3. Administrador
    sql_administrador = """
    CREATE TABLE IF NOT EXISTS Administrador (
        id_administrador INT AUTO_INCREMENT PRIMARY KEY,
        matricula VARCHAR(20),
        nombre VARCHAR(100),
        apellido_paterno VARCHAR(100),
        apellido_materno VARCHAR(100),
        id_cuenta INT,
        FOREIGN KEY (id_cuenta) REFERENCES Cuentas(id_cuenta)
    )
    """

    # 4. Alumno
    sql_alumno = """
    CREATE TABLE IF NOT EXISTS Alumno (
        id_alumno INT AUTO_INCREMENT PRIMARY KEY,
        id_cuenta INT,
        numero_control VARCHAR(8),
        nombre_alumno VARCHAR(100),
        apellido_paterno VARCHAR(100),
        apellido_materno VARCHAR(100),
        correo_alumno VARCHAR(100),
        id_carrera INT,
        semestre INT,
        estatus_alumno VARCHAR(50),
        FOREIGN KEY (id_cuenta) REFERENCES Cuentas(id_cuenta),
        FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
    )
    """

    # 5. Maestro
    sql_maestro = """
    CREATE TABLE IF NOT EXISTS Maestro (
        id_maestro INT AUTO_INCREMENT PRIMARY KEY,
        id_cuenta INT,
        matricula VARCHAR(20),
        nombre_maestro VARCHAR(100),
        apellido_paterno VARCHAR(100),
        apellido_materno VARCHAR(100),
        correo VARCHAR(100),
        estatus VARCHAR(50),
        grado_estudios VARCHAR(100),
        perfil_docente VARCHAR(100),
        carga_academica INT,
        tipo_contrato VARCHAR(50),
        cedula_profesional VARCHAR(50),
        FOREIGN KEY (id_cuenta) REFERENCES Cuentas(id_cuenta)
    )
    """

    # 6. Carreras
    sql_carreras = """
    CREATE TABLE IF NOT EXISTS Carreras (
        id_carrera INT AUTO_INCREMENT PRIMARY KEY,
        nombre_carrera VARCHAR(100),
        tipo_carrera VARCHAR(50),
        numero_semestres INT
    )
    """

    # 7. Solicitudes
    sql_solicitudes = """
    CREATE TABLE IF NOT EXISTS Solicitudes (
        id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
        id_cuenta INT,
        motivo TEXT,
        estado VARCHAR(50),
        id_administrador INT,
        FOREIGN KEY (id_cuenta) REFERENCES Cuentas(id_cuenta),
        FOREIGN KEY (id_administrador) REFERENCES Administrador(id_administrador)
    )
    """

    # 8. Materia
    sql_materia = """
    CREATE TABLE IF NOT EXISTS Materia (
        id_materia INT AUTO_INCREMENT PRIMARY KEY,
        clave VARCHAR(20),
        nombre_materia VARCHAR(100),
        horas_semana INT,
        creditos INT,
        id_carrera INT,
        FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
    )
    """

    # 9. Grupo
    sql_grupo = """
    CREATE TABLE IF NOT EXISTS Grupo (
        id_grupo INT AUTO_INCREMENT PRIMARY KEY,
        id_maestro INT,
        id_materia INT,
        cupo_maximo INT,
        periodo VARCHAR(50),
        horario TEXT,
        alumnos_inscritos INT DEFAULT 0,
        FOREIGN KEY (id_maestro) REFERENCES Maestro(id_maestro),
        FOREIGN KEY (id_materia) REFERENCES Materia(id_materia)
    )
    """

    # 12. Materia
    sql_materia = """
    CREATE TABLE IF NOT EXISTS Materia (
        id_materia INT AUTO_INCREMENT PRIMARY KEY,
        clave VARCHAR(20),
        nombre_materia VARCHAR(100),
        horas_semana INT,
        creditos INT,
        id_carrera INT,
        FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
    )
    """

    # 13. Registro
    sql_registro = """
    CREATE TABLE IF NOT EXISTS Registro (
        id_registro INT AUTO_INCREMENT PRIMARY KEY,
        id_alumno INT,
        id_grupo INT,
        estatus_materia VARCHAR(50),
        tipo_registro VARCHAR(50),
        FOREIGN KEY (id_alumno) REFERENCES Alumno(id_alumno),
        FOREIGN KEY (id_grupo) REFERENCES Grupo(id_grupo)
    )
    """

    # 14. Unidad
    sql_unidad = """
    CREATE TABLE IF NOT EXISTS Unidad (
        id_unidad INT AUTO_INCREMENT PRIMARY KEY,
        id_materia INT,
        numero_unidad INT,
        tema_unidad VARCHAR(200),
        descripcion TEXT,
        FOREIGN KEY (id_materia) REFERENCES Materia(id_materia)
    )
    """

    # 15. BonusUnidad
    sql_bonus_unidad = """
    CREATE TABLE IF NOT EXISTS BonusUnidad (
        id_bonusUnidad INT AUTO_INCREMENT PRIMARY KEY,
        id_registro INT,
        id_unidad INT,
        valor DECIMAL(5,2),
        justificacion TEXT,
        FOREIGN KEY (id_registro) REFERENCES Registro(id_registro),
        FOREIGN KEY (id_unidad) REFERENCES Unidad(id_unidad)
    )
    """

    # 16. BonusMateria
    sql_bonus_materia = """
    CREATE TABLE IF NOT EXISTS BonusMateria (
        id_bonusMateria INT AUTO_INCREMENT PRIMARY KEY,
        id_registro INT,
        valor DECIMAL(5,2),
        justificacion TEXT,
        FOREIGN KEY (id_registro) REFERENCES Registro(id_registro)
    )
    """

    # 17. Calificacion_final
    sql_calificacion_final = """
    CREATE TABLE IF NOT EXISTS Calificacion_final (
        id_final INT AUTO_INCREMENT PRIMARY KEY,
        id_registro INT,
        calificacion DECIMAL(5,2),
        FOREIGN KEY (id_registro) REFERENCES Registro(id_registro)
    )
    """

    # 18. Calificaciones_unidad
    sql_calificaciones_unidad = """
    CREATE TABLE IF NOT EXISTS Calificaciones_unidad (
        id_calificacion_unidad INT AUTO_INCREMENT PRIMARY KEY,
        id_registro INT,
        id_unidad INT,
        calificacion DECIMAL(5,2),
        intentos INT DEFAULT 1,
        FOREIGN KEY (id_registro) REFERENCES Registro(id_registro),
        FOREIGN KEY (id_unidad) REFERENCES Unidad(id_unidad)
    )
    """

    # 19. Resultado
    sql_resultado = """
    CREATE TABLE IF NOT EXISTS Resultado (
        id_resultado INT AUTO_INCREMENT PRIMARY KEY,
        id_registro INT,
        id_actividad INT,
        calificacion DECIMAL(5,2),
        fecha_registro DATE,
        observaciones TEXT,
        FOREIGN KEY (id_registro) REFERENCES Registro(id_registro),
        FOREIGN KEY (id_actividad) REFERENCES Actividad(id_actividad)
    )
    """

    # 20. Tipos_actividades
    sql_tipos_actividades = """
    CREATE TABLE IF NOT EXISTS Tipos_actividades (
        id_tipo INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100)
    )
    """

    # 21. Actividad
    sql_actividad = """
    CREATE TABLE IF NOT EXISTS Actividad (
        id_actividad INT AUTO_INCREMENT PRIMARY KEY,
        id_tipo INT,
        id_unidad INT,
        ponderacion DECIMAL(5,2),
        detalles TEXT,
        FOREIGN KEY (id_tipo) REFERENCES Tipos_actividades(id_tipo),
        FOREIGN KEY (id_unidad) REFERENCES Unidad(id_unidad)
    )
    """

    # Lista de tablas en orden de creación (primero las independientes)
    tablas = [
        ("Roles", sql_roles),
        ("Cuentas", sql_cuentas),
        ("Carreras", sql_carreras),
        ("Administrador", sql_administrador),
        ("Alumno", sql_alumno),
        ("Maestro", sql_maestro),
        ("Solicitudes", sql_solicitudes),
        ("Materia", sql_materia),
        ("Grupo", sql_grupo),
        ("Registro", sql_registro),
        ("Unidad", sql_unidad),
        ("Tipos_actividades", sql_tipos_actividades),
        ("Actividad", sql_actividad),
        ("BonusUnidad", sql_bonus_unidad),
        ("BonusMateria", sql_bonus_materia),
        ("Calificacion_final", sql_calificacion_final),
        ("Calificaciones_unidad", sql_calificaciones_unidad),
        ("Resultado", sql_resultado),
    ]

    try:
        print("\n📊 Creando/verificando 18 tablas en db_escolar...")

        for nombre_tabla, sql in tablas:
            try:
                cursor.execute(sql)
                print(f"✓ Tabla '{nombre_tabla}' verificada/creada")
            except Exception as e:
                print(f"❌ Error creando tabla '{nombre_tabla}': {e}")

        conexion.commit()
        print("\n✓ Base de datos 'db_escolar' actualizada correctamente con 18 tablas")

    except Exception as e:
        print(f"Error general creando tablas: {e}")
        conexion.rollback()

    finally:
        cursor.close()


# Crear tablas nuevas automáticamente al iniciar (después de definir la función)
try:
    eliminar_tablas_obsoletas()
    crear_tablas_nuevas()
    verificar_y_actualizar_columnas()
except Exception as e:
    print(f"Advertencia: No se pudieron crear algunas tablas: {e}")
