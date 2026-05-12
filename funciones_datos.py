#Funciones de recuperación y conversión 

from db_conexion import ejecutar_select


def obtener_carreras_ordenadas():
    """Obtiene todos los registros de carreras con campos en orden específico:
    id_carrera, nombre_carrera, tipo_carrera, numero_semestres, clave_carrera"""
    sql = """
    SELECT id_carrera, nombre_carrera, tipo_carrera, numero_semestres, clave_carrera 
    FROM carreras 
    ORDER BY id_carrera ASC
    """
    return ejecutar_select(sql)


def obtener_materias_ordenadas():
    """Obtiene todos los registros de materias con campos en orden específico:
    id_materia, clave, nombre_materia, horas_semana, nombre_carrera, unidades
    Reemplaza id_carrera por nombre_carrera mediante JOIN"""
    sql = """
    SELECT m.id_materia, m.clave, m.nombre_materia, m.horas_semana, c.nombre_carrera
    FROM materia m
    JOIN carreras c ON m.id_carrera = c.id_carrera
    ORDER BY m.id_materia ASC
    """
    return ejecutar_select(sql)


def obtener_grupos_ordenadas():
    sql = """
        SELECT g.clave_grupo, m.nombre_maestro, mat.nombre_materia, g.cupo_maximo, g.periodo, g.years, 
            COUNT(r.id_registro) AS alumnos_inscritos, g.estado
    FROM grupo g
    JOIN maestro m ON g.id_maestro = m.id_maestro
    JOIN materia mat ON g.id_materia = mat.id_materia
    LEFT JOIN registro r ON r.id_grupo = g.id_grupo
    GROUP BY g.id_grupo, m.nombre_maestro, mat.nombre_materia
    ORDER BY g.clave_grupo ASC
    """
    return ejecutar_select(sql)


def obtener_alumnos_ordenados():
    """Obtiene todos los registros de alumnos con campos en orden específico:
    numero_control, nombre_alumno, apellido_paterno, apellido_materno, correo_alumno, nombre_carrera, estatus_alumno
    Reemplaza id_carrera por nombre_carrera mediante JOIN"""
    sql = """
    SELECT a.numero_control, a.nombre_alumno, a.apellido_paterno, a.apellido_materno, a.correo_alumno, c.nombre_carrera, a.estatus_alumno
    FROM alumno a
    JOIN carreras c ON a.id_carrera = c.id_carrera
    ORDER BY a.numero_control ASC
    """
    return ejecutar_select(sql)


def obtener_maestros_ordenados():
    """Obtiene todos los registros de maestros con campos en orden específico:
    matricula, nombre_maestro, apellido_paterno, apellido_materno, correo, estatus, perfil_docente"""
    sql = """
    SELECT matricula, nombre_maestro, apellido_paterno, apellido_materno, correo, estatus, perfil_docente
    FROM maestro
    ORDER BY matricula ASC
    """
    return ejecutar_select(sql)

def obtener_administradores_ordenados():
    """Obtiene todos los registros de administradores con campos en orden específico:
    matricula, nombre, apellido_paterno, apellido_materno"""
    sql = """
    SELECT matricula, nombre, apellido_paterno, apellido_materno
    FROM administrador
    ORDER BY matricula ASC
    """
    return ejecutar_select(sql)


def obtener_registros_ordenados():
    """Obtiene inscripciones en el orden visible requerido para la interfaz."""
    sql = """
    SELECT
        r.id_registro,
        CONCAT(a.nombre_alumno, ' ', a.apellido_paterno, ' ', a.apellido_materno) AS alumno,
        a.numero_control,
        g.clave_grupo,
        m.nombre_materia,
        r.estatus_materia,
        r.tipo_registro
    FROM registro r
    LEFT JOIN alumno a ON r.id_alumno = a.id_alumno
    LEFT JOIN grupo g ON r.id_grupo = g.id_grupo
    LEFT JOIN materia m ON g.id_materia = m.id_materia
    ORDER BY r.id_registro DESC
    """
    return ejecutar_select(sql)


def obtener_nombre_carrera_por_id(id_carrera):
    """Obtiene el nombre de una carrera por su ID"""
    resultado = ejecutar_select(
        "SELECT nombre_carrera FROM carreras WHERE id_carrera=%s",
        (id_carrera,)
    )
    if resultado:
        return resultado[0][0]
    return "Carrera no encontrada"


def obtener_id_carrera_por_nombre(nombre_carrera):
    """Obtiene el ID de una carrera por su nombre. Retorna None si no existe."""
    resultado = ejecutar_select(
        "SELECT id_carrera FROM carreras WHERE nombre_carrera=%s",
        (nombre_carrera,)
    )
    if resultado:
        return resultado[0][0]
    return None


def obtener_nombre_maestro_por_matricula(matricula_maestro):
    """Obtiene el nombre de un maestro por su matrícula"""
    resultado = ejecutar_select(
        "SELECT nombre_maestro FROM maestro WHERE matricula_maestro=%s",
        (matricula_maestro,)
    )
    if resultado:
        return resultado[0][0]
    return "Maestro no encontrado"


def obtener_matricula_maestro_por_nombre(nombre_maestro):
    """Obtiene la matrícula de un maestro por su nombre. Retorna None si no existe."""
    resultado = ejecutar_select(
        "SELECT matricula_maestro FROM maestro WHERE nombre_maestro=%s",
        (nombre_maestro,)
    )
    if resultado:
        return resultado[0][0]
    return None


def obtener_id_maestro_por_nombre(nombre_maestro):
    """Obtiene el ID de un maestro por su nombre. Retorna None si no existe."""
    resultado = ejecutar_select(
        "SELECT id_maestro FROM maestro WHERE nombre_maestro=%s",
        (nombre_maestro,)
    )
    if resultado:
        return resultado[0][0]
    return None


def obtener_nombre_materia_por_id(id_materia):
    """Obtiene el nombre de una materia por su ID"""
    resultado = ejecutar_select(
        "SELECT nombre_materia FROM materia WHERE id_materia=%s",
        (id_materia,)
    )
    if resultado:
        return resultado[0][0]
    return "Materia no encontrada"


def obtener_id_materia_por_nombre(nombre_materia):
    """Obtiene el ID de una materia por su nombre. Retorna None si no existe."""
    resultado = ejecutar_select(
        "SELECT id_materia FROM materia WHERE nombre_materia=%s",
        (nombre_materia,)
    )
    if resultado:
        return resultado[0][0]
    return None
