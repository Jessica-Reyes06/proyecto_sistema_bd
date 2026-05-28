"""
Funciones para manejo de auditoría de cambios de administradores
"""
from db_conexion import ejecutar_insert, ejecutar_select


# Mapeo de nombres de tablas: nombre_tabla -> nombre_singular
TABLAS_NOMBRES = {
    "alumno": ("alumno", "alumnos"),
    "maestro": ("maestro", "maestros"),
    "grupo": ("grupo", "grupos"),
    "materia": ("materia", "materias"),
    "carreras": ("carrera", "carreras"),
    "administrador": ("administrador", "administradores"),
    "registro": ("inscripción", "inscripciones"),
    "cuentas": ("cuenta", "cuentas"),
    "roles": ("rol", "roles"),
    "actividad": ("actividad", "actividades"),
    "tipos_actividades": ("tipo de actividad", "tipos de actividades"),
}

# Mapeo de identificadores visibles por tabla
IDENTIFICADORES = {
    "alumno": ("numero_control", "id_alumno"),
    "maestro": ("matricula_maestro", "id_maestro"),
    "grupo": ("clave_grupo", "id_grupo"),
    "materia": ("clave", "id_materia"),
    "carreras": ("clave_carrera", "id_carrera"),
    "administrador": ("matricula", "id_administrador"),
}


def obtener_identificador(tabla, id_valor):
    """
    Obtiene el identificador visible de un registro (numero_control, clave, etc).
    
    Args:
        tabla: Nombre de la tabla
        id_valor: ID del registro en la BD
    
    Returns:
        El identificador visible (numero_control, clave_grupo, etc) o el ID si no existe
    """
    if tabla not in IDENTIFICADORES:
        return str(id_valor)
    
    campo_visible, campo_id = IDENTIFICADORES[tabla]
    
    try:
        sql = f'SELECT "{campo_visible}" FROM "{tabla}" WHERE "{campo_id}" = %s LIMIT 1'
        resultado = ejecutar_select(sql, (id_valor,))
        return str(resultado[0][0]) if resultado else str(id_valor)
    except Exception as e:
        print(f"Error obteniendo identificador de {tabla}: {e}")
        return str(id_valor)


def obtener_nombre_registro(tabla, id_valor):
    """
    Obtiene el nombre/descripción legible de un registro.
    
    Args:
        tabla: Nombre de la tabla
        id_valor: ID del registro
    
    Returns:
        Nombre del registro (ej: "Juan Pérez", "ISC-101") o None
    """
    try:
        if tabla == "alumno":
            sql = """SELECT CONCAT(nombre_alumno, ' ', apellido_paterno, ' ', apellido_materno) 
                     FROM "alumno" WHERE id_alumno = %s LIMIT 1"""
        elif tabla == "maestro":
            sql = """SELECT CONCAT(nombre_maestro, ' ', apellido_paterno, ' ', apellido_materno) 
                     FROM "maestro" WHERE id_maestro = %s LIMIT 1"""
        elif tabla == "grupo":
            sql = """SELECT clave_grupo FROM "grupo" WHERE id_grupo = %s LIMIT 1"""
        elif tabla == "materia":
            sql = """SELECT nombre_materia FROM "materia" WHERE id_materia = %s LIMIT 1"""
        elif tabla == "carreras":
            sql = """SELECT nombre_carrera FROM "carreras" WHERE id_carrera = %s LIMIT 1"""
        elif tabla == "administrador":
            sql = """SELECT CONCAT(nombre_administrador, ' ', apellido_paterno, ' ', apellido_materno) 
                     FROM "administrador" WHERE id_administrador = %s LIMIT 1"""
        else:
            return None
        
        resultado = ejecutar_select(sql, (id_valor,))
        return str(resultado[0][0]) if resultado else None
    except Exception as e:
        print(f"Error obteniendo nombre de {tabla}: {e}")
        return None


def obtener_admin_actual():
    """
    Obtiene el nombre del administrador actual.
    Retorna el primer administrador disponible en la BD.
    
    Returns:
        Nombre del administrador o "Admin Desconocido"
    """
    try:
        sql = """SELECT CONCAT(nombre, ' ', apellido_paterno, ' ', apellido_materno) 
                 FROM "administrador" 
                 ORDER BY id_administrador ASC 
                 LIMIT 1"""
        resultado = ejecutar_select(sql)
        return resultado[0][0] if resultado else "Admin Desconocido"
    except Exception:
        return "Admin Desconocido"


# Mapeo de tablas -> (campo_busqueda, campo_id)
CAMPOS_BUSQUEDA = {
    "alumno": ("numero_control", "id_alumno"),
    "maestro": ("matricula_maestro", "id_maestro"),
    "grupo": ("clave_grupo", "id_grupo"),
    "materia": ("clave", "id_materia"),
    "carreras": ("clave_carrera", "id_carrera"),
    "administrador": ("matricula", "id_administrador"),
    "actividad": ("id_tipo", "id_actividad"),
    "tipos_actividades": ("nombre_tipo", "id_tipo_actividad"),
    "registro": ("id_alumno", "id_registro"),
    "calificaciones_finales": ("numero_control", "id_final"),
    "calificaciones_actividades": ("numero_control", "id_actividad_calif"),
    "salones": ("id_salon", "id_salon"),
}


def obtener_id_recien_insertado(tabla, valor_identificador):
    """
    Obtiene el ID auto-generado de un registro recién insertado.
    
    Busca el registro usando el identificador (numero_control, clave, etc.)
    y retorna el ID de la tabla.
    
    Args:
        tabla: Nombre de la tabla
        valor_identificador: Valor del campo de búsqueda (ej: "21490" para numero_control)
    
    Returns:
        ID del registro insertado o None si no se encuentra
    
    Ejemplos:
        obtener_id_recien_insertado("alumno", "21490") → 1
        obtener_id_recien_insertado("materia", "ISC-101") → 5
    """
    try:
        if tabla not in CAMPOS_BUSQUEDA:
            return None
        
        campo_busqueda, campo_id = CAMPOS_BUSQUEDA[tabla]
        
        sql = f'SELECT "{campo_id}" FROM "{tabla}" WHERE "{campo_busqueda}" = %s LIMIT 1'
        resultado = ejecutar_select(sql, (valor_identificador,))
        
        return resultado[0][0] if resultado else None
    except Exception as e:
        print(f"Error obteniendo ID recién insertado de {tabla}: {e}")
        return None


def registrar_auditoria(nombre_admin, tabla_afectada, tipo_operacion, id_registro=None, nombre_registro=None, es_bulk=False):
    """
    Registra automáticamente un cambio en la auditoría con descripción generada automáticamente.
    
    Args:
        nombre_admin: Nombre del administrador (ej: "Andy")
        tabla_afectada: Nombre de la tabla modificada ("alumno", "maestro", etc)
        tipo_operacion: "INSERT", "UPDATE" o "DELETE"
        id_registro: ID del registro afectado
        nombre_registro: Nombre/descripción del registro (ej: "Juan Pérez", "ISC-101")
        es_bulk: Si es True, genera descripción genérica para operaciones CSV
    
    Returns:
        True si se registró, False si hubo error
    
    Ejemplos:
        registrar_auditoria("Andy", "alumno", "INSERT", "21490", "Juan Pérez")
        → "Andy registró alumno 21490 - Juan Pérez"
        
        registrar_auditoria("Andy", "grupo", "UPDATE", "ISC-101")
        → "Andy actualizó grupo ISC-101"
        
        registrar_auditoria("Andy", "alumno", "INSERT", es_bulk=True)
        → "Andy registró alumnos por csv"
    """
    try:
        # Obtener nombres singular y plural de la tabla
        tabla_singular, tabla_plural = TABLAS_NOMBRES[tabla_afectada]
        
        if id_registro:
            identificador = obtener_identificador(tabla_afectada, id_registro)
            nombre_registro = obtener_nombre_registro(tabla_afectada, id_registro)

        # Generar descripción automáticamente
        if es_bulk:
            # Operación en lote (CSV) - usar plural
            if tipo_operacion == "INSERT":
                descripcion = f"{nombre_admin} registró {tabla_plural} por csv"
            else:
                descripcion = f"{nombre_admin} realizó cambios en {tabla_afectada} por csv"
        else:
            # Operación individual
            if tipo_operacion == "INSERT":
                if identificador and nombre_registro:
                    descripcion = f"{nombre_admin} registró {tabla_singular} {identificador} - {nombre_registro}"
                elif identificador:
                    descripcion = f"{nombre_admin} registró {tabla_singular} {identificador}"
                else:
                    descripcion = f"{nombre_admin} registró {tabla_singular}"
            
            elif tipo_operacion == "UPDATE":
                if identificador and nombre_registro:
                    descripcion = f"{nombre_admin} actualizó {tabla_singular} {identificador} - {nombre_registro}"
                elif identificador:
                    descripcion = f"{nombre_admin} actualizó {tabla_singular} {identificador}"
                else:
                    descripcion = f"{nombre_admin} actualizó {tabla_singular}"
            
            elif tipo_operacion == "DELETE":
                if identificador and nombre_registro:
                    descripcion = f"{nombre_admin} eliminó {tabla_singular} {identificador} - {nombre_registro}"
                elif identificador:
                    descripcion = f"{nombre_admin} eliminó {tabla_singular} {identificador}"
                else:
                    descripcion = f"{nombre_admin} eliminó {tabla_singular}"
            else:
                descripcion = f"{nombre_admin} realizó cambios en {tabla_afectada}"
        
        # Obtener ID del admin
        sql_admin = """SELECT id_administrador FROM "administrador" 
                       WHERE CONCAT(nombre, ' ', apellido_paterno, ' ', apellido_materno) ILIKE %s LIMIT 1"""
        resultado = ejecutar_select(sql_admin, (f"%{nombre_admin}%",))
        id_admin = resultado[0][0] if resultado else None
        
        # Insertar en auditoría
        sql = """INSERT INTO "auditoria_cambios" 
                 (id_admin, tabla_afectada, tipo_operacion, id_registro, descripcion, fecha_hora)
                 VALUES (%s, %s, %s, %s, %s, NOW())"""
        
        params = (id_admin, tabla_afectada, tipo_operacion, id_registro, descripcion)
        ejecutar_insert(sql, params)
        return True
    except Exception as e:
        print(f"Error registrando auditoría: {e}")
        return False




def obtener_ultimos_cambios(cantidad=15):
    """
    Obtiene los últimos cambios registrados en la auditoría.
    
    Args:
        cantidad: Número de cambios a mostrar (default 15)
    
    Returns:
        Lista de tuplas: (administrador, tabla, operacion, descripcion, fecha_hora)
    """
    try:
        sql = """SELECT 
                    CONCAT(adm.nombre, ' ', adm.apellido_paterno, ' ', adm.apellido_materno) as administrador,
                    ac.tabla_afectada,
                    ac.tipo_operacion,
                    ac.descripcion,
                    ac.fecha_hora
                 FROM "auditoria_cambios" ac
                 LEFT JOIN "administrador" adm ON ac.id_admin = adm.id_administrador
                 ORDER BY ac.fecha_hora DESC
                 LIMIT %s"""
        
        resultados = ejecutar_select(sql, (cantidad,))
        return resultados if resultados else []
    except Exception as e:
        print(f"Error obteniendo cambios: {e}")
        return []
