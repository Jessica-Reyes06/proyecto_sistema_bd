#Funciones de recuperación y conversión 

from db_conexion import ejecutar_select


def obtener_carreras_ordenadas():
    """Obtiene todos los registros de carreras con campos en orden específico:
    id_carrera, nombre_carrera, tipo_carrera, numero_semestres, clave_carrera"""
    sql = """
    SELECT id_carrera, nombre_carrera, tipo_carrera, numero_semestres, clave_carrera 
    FROM Carreras 
    ORDER BY id_carrera ASC
    """
    return ejecutar_select(sql)


def obtener_materias_ordenadas():
    """Obtiene todos los registros de materias con campos en orden específico:
    id_materia, clave, nombre_materia, horas_semana, nombre_carrera, unidades
    Reemplaza id_carrera por nombre_carrera mediante JOIN"""
    sql = """
    SELECT m.id_materia, m.clave, m.nombre_materia, m.horas_semana, c.nombre_carrera, m.unidades
    FROM Materia m
    JOIN Carreras c ON m.id_carrera = c.id_carrera
    ORDER BY m.id_materia ASC
    """
    return ejecutar_select(sql)


def obtener_grupos_ordenadas():
    """Obtiene todos los registros de grupos con campos en orden específico:
    id_grupo, nombre_maestro, nombre_materia, cupo_maximo, periodo, years, alumnos_inscritos, horario, estado
    Reemplaza id_maestro por nombre_maestro e id_materia por nombre_materia mediante JOIN"""
    sql = """
    SELECT g.id_grupo, m.nombre_maestro, mat.nombre_materia, g.cupo_maximo, g.periodo, g.years, g.alumnos_inscritos, g.horario, g.estado
    FROM Grupo g
    JOIN Maestro m ON g.id_maestro = m.id_maestro
    JOIN Materia mat ON g.id_materia = mat.id_materia
    ORDER BY g.id_grupo ASC
    """
    return ejecutar_select(sql)


def obtener_alumnos_ordenados():
    """Obtiene todos los registros de alumnos con campos en orden específico:
    numero_control, nombre_alumno, apellido_paterno, apellido_materno, correo_alumno, nombre_carrera, estatus_alumno
    Reemplaza id_carrera por nombre_carrera mediante JOIN"""
    sql = """
    SELECT a.numero_control, a.nombre_alumno, a.apellido_paterno, a.apellido_materno, a.correo_alumno, c.nombre_carrera, a.estatus_alumno
    FROM Alumno a
    JOIN Carreras c ON a.id_carrera = c.id_carrera
    ORDER BY a.numero_control ASC
    """
    return ejecutar_select(sql)


def obtener_maestros_ordenados():
    """Obtiene todos los registros de maestros con campos en orden específico:
    matricula, nombre_maestro, apellido_paterno, apellido_materno, correo, estatus, grado_estudios, perfil_docente"""
    sql = """
    SELECT matricula, nombre_maestro, apellido_paterno, apellido_materno, correo, estatus, grado_estudios, perfil_docente
    FROM Maestro
    ORDER BY matricula ASC
    """
    return ejecutar_select(sql)


def obtener_administradores_ordenados():
    """Obtiene todos los registros de administradores con campos en orden específico:
    matricula, nombre, apellido_paterno, apellido_materno"""
    sql = """
    SELECT matricula, nombre, apellido_paterno, apellido_materno
    FROM Administrador
    ORDER BY matricula ASC
    """
    return ejecutar_select(sql)


def obtener_nombre_carrera_por_id(id_carrera):
    """Obtiene el nombre de una carrera por su ID"""
    resultado = ejecutar_select(
        "SELECT nombre_carrera FROM Carreras WHERE id_carrera=%s",
        (id_carrera,)
    )
    if resultado:
        return resultado[0][0]
    return "Carrera no encontrada"


def obtener_id_carrera_por_nombre(nombre_carrera):
    """Obtiene el ID de una carrera por su nombre. Retorna None si no existe."""
    resultado = ejecutar_select(
        "SELECT id_carrera FROM Carreras WHERE nombre_carrera=%s",
        (nombre_carrera,)
    )
    if resultado:
        return resultado[0][0]
    return None


def obtener_nombre_maestro_por_matricula(matricula_maestro):
    """Obtiene el nombre de un maestro por su matrícula"""
    resultado = ejecutar_select(
        "SELECT nombre_maestro FROM Maestro WHERE matricula_maestro=%s",
        (matricula_maestro,)
    )
    if resultado:
        return resultado[0][0]
    return "Maestro no encontrado"


def obtener_matricula_maestro_por_nombre(nombre_maestro):
    """Obtiene la matrícula de un maestro por su nombre. Retorna None si no existe."""
    resultado = ejecutar_select(
        "SELECT matricula_maestro FROM Maestro WHERE nombre_maestro=%s",
        (nombre_maestro,)
    )
    if resultado:
        return resultado[0][0]
    return None


def obtener_id_maestro_por_nombre(nombre_maestro):
    """Obtiene el ID de un maestro por su nombre. Retorna None si no existe."""
    resultado = ejecutar_select(
        "SELECT id_maestro FROM Maestro WHERE nombre_maestro=%s",
        (nombre_maestro,)
    )
    if resultado:
        return resultado[0][0]
    return None


def obtener_nombre_materia_por_id(id_materia):
    """Obtiene el nombre de una materia por su ID"""
    resultado = ejecutar_select(
        "SELECT nombre_materia FROM Materia WHERE id_materia=%s",
        (id_materia,)
    )
    if resultado:
        return resultado[0][0]
    return "Materia no encontrada"


def obtener_id_materia_por_nombre(nombre_materia):
    """Obtiene el ID de una materia por su nombre. Retorna None si no existe."""
    resultado = ejecutar_select(
        "SELECT id_materia FROM Materia WHERE nombre_materia=%s",
        (nombre_materia,)
    )
    if resultado:
        return resultado[0][0]
    return None
