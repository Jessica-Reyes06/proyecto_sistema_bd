import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from customtkinter import *
from PIL import Image
import importlib
from db_conexion import ejecutar_select, ejecutar_insert
from codigo_alumnos import funciones_Alumnos as funciones_alumnos


ventana = None
frame_contenido = None
matricula_maestro = None
nombre_maestro = None

COLOR_SIDE = "#e3efff"
COLOR_MAIN = "#0E7490"
COLOR_HOVER = "#155E75"
COLOR_AZUL = "#2563EB"
BUTTON_FONT = ("Arial", 16)
FORMAL_FONT = ("Arial", 16)
FORMAL_FONT_SMALL = ("Arial", 13)
FORMAL_FONT_BOLD = ("Arial", 16, "bold")
FORMAL_FONT_TITLE = ("Arial", 30, "bold")
BONUS_UNIDAD_TABLE = None
BONUS_MATERIA_TABLE = None
_btn_nav_activo = [None]


def limpiar_frame(frame):
    for w in frame.winfo_children():
        w.destroy()


def mostrar_maximizada():
    ventana.state("zoomed")
    ventana.deiconify()


def cerrar_sesion():
    global ventana
    if ventana is not None:
        ventana.destroy()
    import interfaz_login
    importlib.reload(interfaz_login)


def crear_icono(ruta, size=(20, 20), color=None):
    """Crea un CTkImage desde ruta. Si se pasa `color` (hex), pinta la silueta del icono de ese color.
    Esto funciona asumiendo que el recurso tiene un canal alpha con la forma del icono.
    """
    try:
        img = Image.open(ruta).convert("RGBA")
        if color:
            # convertir hex a RGB
            hexc = color.lstrip("#")
            r = int(hexc[0:2], 16)
            g = int(hexc[2:4], 16)
            b = int(hexc[4:6], 16)
            color_img = Image.new("RGBA", img.size, (r, g, b, 255))
            alpha = img.split()[3]
            colored = Image.new("RGBA", img.size)
            colored.paste(color_img, (0, 0), mask=alpha)
            return CTkImage(light_image=colored, size=size)
        return CTkImage(light_image=img, size=size)
    except Exception:
        return None


def obtener_datos_maestro(matricula):
    sql = """
        SELECT nombre_maestro, apellido_paterno, apellido_materno,
               COALESCE(correo, ''),
               COALESCE(perfil_docente, ''),
               COALESCE(cedula_profesional, '')
        FROM maestro
        WHERE matricula = %s
        LIMIT 1
    """
    filas = ejecutar_select(sql, (matricula,))
    return filas[0] if filas else None


def obtener_grupos_maestro(matricula):
    sql = """
        SELECT G.clave_grupo, G.id_grupo, G.id_materia, M.nombre_materia
        FROM grupo G
        JOIN materia M ON G.id_materia = M.id_materia
        JOIN maestro MA ON G.id_maestro = MA.id_maestro
        WHERE MA.matricula = %s
        ORDER BY G.clave_grupo
    """
    return ejecutar_select(sql, (matricula,))


def obtener_materias_maestro(matricula):
    sql = """
        SELECT DISTINCT M.id_materia, M.nombre_materia
        FROM grupo G
        JOIN materia M ON G.id_materia = M.id_materia
        JOIN maestro MA ON G.id_maestro = MA.id_maestro
        WHERE MA.matricula = %s
        ORDER BY M.nombre_materia
    """
    return ejecutar_select(sql, (matricula,))


def obtener_unidades_grupo(id_grupo):
    sql = """
        SELECT id_materia
        FROM grupo
        WHERE id_grupo = %s
        LIMIT 1
    """
    filas = ejecutar_select(sql, (id_grupo,))
    if not filas:
        return []
    id_materia = filas[0][0]

    sql2 = """
        SELECT id_unidad, numero_unidad, tema_unidad
        FROM unidad
        WHERE id_grupo = %s
        ORDER BY numero_unidad, id_unidad
    """
    return ejecutar_select(sql2, (id_grupo,))


def obtener_actividades_grupo(id_grupo):
    sql = """
        SELECT DISTINCT A.id_unidad
        FROM actividad A
        JOIN unidad U ON A.id_unidad = U.id_unidad
        WHERE U.id_grupo = %s
        ORDER BY A.id_unidad
    """
    filas = ejecutar_select(sql, (id_grupo,))
    if not filas:
        return []
    ids_unidad = [f[0] for f in filas]
    marcadores = ",".join(["%s"] * len(ids_unidad))
    sql2 = f"""
        SELECT A.id_actividad,
               A.id_unidad,
               U.numero_unidad,
               A.id_tipo,
               COALESCE(TA.nombre, '') AS tipo_actividad,
               A.detalles,
               A.ponderacion
        FROM actividad A
        JOIN unidad U ON A.id_unidad = U.id_unidad
        LEFT JOIN tipos_actividades TA ON A.id_tipo = TA.id_tipo
        WHERE A.id_unidad IN ({marcadores})
        ORDER BY U.numero_unidad, A.id_actividad
    """
    return ejecutar_select(sql2, tuple(ids_unidad))


def eliminar_actividad_por_id(id_grupo, id_actividad):
    sql_resultado = "DELETE FROM resultado WHERE id_actividad = %s"
    sql_actividad = """
        DELETE FROM actividad
        WHERE id_actividad = %s
          AND id_unidad IN (SELECT id_unidad FROM unidad WHERE id_grupo = %s)
    """
    ejecutar_insert(sql_resultado, (id_actividad,))
    ejecutar_insert(sql_actividad, (id_actividad, id_grupo))


def obtener_alumnos_actividad(id_grupo, id_actividad):
    sql = """
        SELECT R.id_registro, A.numero_control, A.nombre_alumno, A.apellido_paterno, A.apellido_materno,
               RES.id_resultado,
               CASE
                   WHEN RES.observaciones LIKE 'ENTREGA_ALUMNO:%' THEN NULL
                   WHEN RES.calificacion = 0
                        AND (RES.observaciones IS NULL OR TRIM(RES.observaciones) = '') THEN NULL
                   ELSE RES.calificacion
               END AS calificacion,
               RES.observaciones,
               CASE
                   WHEN RES.id_resultado IS NULL THEN 'Sin entrega'
                   WHEN RES.observaciones LIKE 'ENTREGA_ALUMNO:%' THEN 'Por revisar'
                   WHEN RES.calificacion = 0
                        AND (RES.observaciones IS NULL OR TRIM(RES.observaciones) = '') THEN 'Por revisar'
                   WHEN RES.calificacion IS NULL THEN 'Por revisar'
                   ELSE 'Revisada'
               END AS estado
        FROM registro R
        JOIN alumno A ON R.id_alumno = A.id_alumno
        LEFT JOIN resultado RES ON R.id_registro = RES.id_registro AND RES.id_actividad = %s
        WHERE R.id_grupo = %s
        ORDER BY A.numero_control
    """
    return ejecutar_select(sql, (id_actividad, id_grupo))


def asegurar_tablas_bonus():
    global BONUS_UNIDAD_TABLE, BONUS_MATERIA_TABLE
    if BONUS_UNIDAD_TABLE is not None and BONUS_MATERIA_TABLE is not None:
        return BONUS_UNIDAD_TABLE, BONUS_MATERIA_TABLE
    BONUS_UNIDAD_TABLE = "bonusunidad"
    BONUS_MATERIA_TABLE = "bonusmateria"
    return BONUS_UNIDAD_TABLE, BONUS_MATERIA_TABLE


def a_numero(valor):
    try:
        if valor is None:
            return None
        if isinstance(valor, str):
            valor = valor.strip().replace("%", "")
            if valor == "":
                return None
        return float(valor)
    except Exception:
        return None


def obtener_suma_ponderaciones(id_grupo, id_unidad):
    sql = """
        SELECT COALESCE(SUM(ponderacion), 0)
        FROM actividad
        WHERE id_unidad = %s
    """
    filas = ejecutar_select(sql, (id_unidad,))
    return float(filas[0][0]) if filas and filas[0] and filas[0][0] is not None else 0.0


def obtener_bonus_unidad(id_registro, id_unidad):
    tabla_bonus_unidad, _ = asegurar_tablas_bonus()
    sql = """
        SELECT COALESCE(SUM(valor), 0)
        FROM {tabla}
        WHERE id_registro = %s
          AND id_unidad = %s
    """.format(tabla=tabla_bonus_unidad)
    filas = ejecutar_select(sql, (id_registro, id_unidad))
    if not filas:
        return 0.0
    return a_numero(filas[0][0]) or 0.0


def guardar_bonus_unidad(id_registro, id_unidad, valor_bonus, justificacion_texto=""):
    tabla_bonus_unidad, _ = asegurar_tablas_bonus()
    sql = """
        INSERT INTO {tabla} (id_registro, id_unidad, valor, justificacion)
        VALUES (%s, %s, %s, %s)
    """.format(tabla=tabla_bonus_unidad)
    detalle = justificacion_texto.strip() if justificacion_texto else "sin justificación"
    ejecutar_insert(sql, (id_registro, id_unidad, valor_bonus, detalle))


def obtener_bonus_materia(id_registro, id_grupo):
    _, tabla_bonus_materia = asegurar_tablas_bonus()
    sql = """
        SELECT COALESCE(SUM(valor), 0)
        FROM {tabla} BM
        JOIN registro R ON BM.id_registro = R.id_registro
        WHERE BM.id_registro = %s
          AND R.id_grupo = %s
    """.format(tabla=tabla_bonus_materia)
    filas = ejecutar_select(sql, (id_registro, id_grupo))
    if not filas:
        return 0.0
    return a_numero(filas[0][0]) or 0.0


def guardar_bonus_materia(id_registro, id_grupo, valor_bonus, justificacion_texto=""):
    _, tabla_bonus_materia = asegurar_tablas_bonus()
    sql = """
        INSERT INTO {tabla} (id_registro, valor, justificacion)
        VALUES (%s, %s, %s)
    """.format(tabla=tabla_bonus_materia)
    detalle = justificacion_texto.strip() if justificacion_texto else "sin justificación"
    ejecutar_insert(sql, (id_registro, valor_bonus, detalle))


def obtener_alumnos_grupo(id_grupo):
    sql = """
        SELECT R.id_registro, A.numero_control, A.nombre_alumno, A.apellido_paterno, A.apellido_materno
        FROM registro R
        JOIN alumno A ON R.id_alumno = A.id_alumno
        WHERE R.id_grupo = %s
        ORDER BY A.apellido_paterno, A.apellido_materno, A.nombre_alumno
    """
    return ejecutar_select(sql, (id_grupo,))


def obtener_materia_grupo(id_grupo):
    sql = """
        SELECT id_materia
        FROM grupo
        WHERE id_grupo = %s
        LIMIT 1
    """
    filas = ejecutar_select(sql, (id_grupo,))
    return filas[0][0] if filas else None


def bonus_unidad_view(frame, id_grupo):
    limpiar_frame(frame)
    CTkLabel(frame, text="Bonus unidad", text_color="black", anchor="w",
             font=("Arial Rounded MT Bold", 24)).pack(fill="x", padx=10, pady=10)
    CTkLabel(frame, text="Asigna puntos extra por alumno y por unidad.",
             text_color="gray").pack(anchor="w", padx=10)

    alumnos = obtener_alumnos_grupo(id_grupo)
    unidades = obtener_unidades_grupo(id_grupo)

    if not alumnos or not unidades:
        CTkLabel(frame, text="Se requieren alumnos y unidades para aplicar bonus.",
                 text_color="#B00020", font=("Arial Rounded MT Bold", 13)).pack(anchor="w", padx=10, pady=10)
        return

    form = CTkFrame(frame, fg_color="white")
    form.pack(fill="x", padx=10, pady=10)

    opciones_alumno = [
        f"{r} - {nc} - {n} {ap} {am}" for r, nc, n, ap, am in alumnos]
    # mantener lista de ids por índice y mostrar al usuario solo el número/tema
    unidad_ids = [str(id_u).strip() for id_u, num, tema in unidades]
    opciones_unidad = [f"Unidad {num}: {tema}" for id_u, num, tema in unidades]

    cb_alumno = CTkComboBox(form, values=opciones_alumno, state="readonly")
    cb_unidad = CTkComboBox(form, values=opciones_unidad, state="readonly")
    e_bonus = CTkEntry(form, placeholder_text="Bonus unidad (ej. 2.5)")
    e_just = CTkEntry(form, placeholder_text="Justificación del bonus")
    for w in (cb_alumno, cb_unidad, e_bonus, e_just):
        w.pack(fill="x", padx=10, pady=6)
    cb_alumno.set(opciones_alumno[0])
    cb_unidad.set(opciones_unidad[0])

    estado = CTkLabel(form, text="", text_color="gray")
    estado.pack(anchor="w", padx=10, pady=6)

    def aplicar():
        bonus = a_numero(e_bonus.get())
        if bonus is None:
            estado.configure(text="Bonus inválido.", text_color="#B00020")
            return

        id_registro = cb_alumno.get().split(" - ", 1)[0].strip()
        # Obtener id_unidad por índice desde el mapeo interno; soportar formato antiguo si aparece
        selected_unidad = cb_unidad.get()
        id_unidad = None
        try:
            idx = opciones_unidad.index(selected_unidad)
            id_unidad = unidad_ids[idx]
        except Exception:
            try:
                id_unidad = cb_unidad.get().split(" - ", 1)[0].strip()
            except Exception:
                id_unidad = None
        _, final_antes = obtener_resumen_alumno(id_registro, id_grupo)

        max_bonus_permitido = max(0.0, round(100.0 - final_antes, 2))
        if bonus > max_bonus_permitido:
            estado.configure(
                text=f"Bonus excedido. Máximo permitido: {max_bonus_permitido:.2f}",
                text_color="#B00020",
            )
            return

        guardar_bonus_unidad(id_registro, id_unidad, bonus, e_just.get())
        _, final_despues = obtener_resumen_alumno(id_registro, id_grupo)
        estado.configure(
            text=f"Bonus unidad aplicado. Final: {final_antes:.2f} -> {final_despues:.2f}",
            text_color="#1B5E20",
        )

    CTkButton(form, text="Aplicar bonus unidad", fg_color=COLOR_MAIN, hover_color=COLOR_HOVER,
              font=BUTTON_FONT, command=aplicar).pack(anchor="e", padx=10, pady=(4, 10))


def bonus_materia_view(frame, id_grupo):
    limpiar_frame(frame)
    CTkLabel(frame, text="Bonus materia", text_color="black", anchor="w",
             font=("Arial Rounded MT Bold", 24)).pack(fill="x", padx=10, pady=10)
    CTkLabel(frame, text="Asigna puntos extra finales por alumno en la materia del grupo.",
             text_color="gray").pack(anchor="w", padx=10)

    alumnos = obtener_alumnos_grupo(id_grupo)
    id_materia = obtener_materia_grupo(id_grupo)
    if not alumnos or not id_materia:
        CTkLabel(frame, text="No se encontró materia o alumnos para este grupo.",
                 text_color="#B00020", font=("Arial Rounded MT Bold", 13)).pack(anchor="w", padx=10, pady=10)
        return

    form = CTkFrame(frame, fg_color="white")
    form.pack(fill="x", padx=10, pady=10)

    opciones_alumno = [
        f"{r} - {nc} - {n} {ap} {am}" for r, nc, n, ap, am in alumnos]
    cb_alumno = CTkComboBox(form, values=opciones_alumno, state="readonly")
    cb_alumno.pack(fill="x", padx=10, pady=6)
    cb_alumno.set(opciones_alumno[0])

    CTkLabel(form, text=f"Materia: {id_materia}", text_color="black",
             font=("Arial Rounded MT Bold", 13)).pack(anchor="w", padx=10, pady=(0, 6))
    e_bonus = CTkEntry(form, placeholder_text="Bonus materia (ej. 3)")
    e_bonus.pack(fill="x", padx=10, pady=6)
    e_just = CTkEntry(form, placeholder_text="Justificación del bonus")
    e_just.pack(fill="x", padx=10, pady=6)

    estado = CTkLabel(form, text="", text_color="gray")
    estado.pack(anchor="w", padx=10, pady=6)

    def aplicar():
        bonus = a_numero(e_bonus.get())
        if bonus is None:
            estado.configure(text="Bonus inválido.", text_color="#B00020")
            return

        id_registro = cb_alumno.get().split(" - ", 1)[0].strip()
        _, final_unidades = obtener_resumen_alumno(id_registro, id_grupo)

        max_bonus_permitido = max(0.0, round(100.0 - final_unidades, 2))
        if bonus > max_bonus_permitido:
            estado.configure(
                text=f"Bonus excedido. Máximo permitido: {max_bonus_permitido:.2f}",
                text_color="#B00020",
            )
            return

        bonus_actual = obtener_bonus_materia(id_registro, id_grupo)
        final_antes = min(100.0, final_unidades + bonus_actual)
        guardar_bonus_materia(id_registro, id_grupo, bonus, e_just.get())
        final_despues = min(100.0, final_unidades + bonus)
        estado.configure(
            text=f"Bonus materia aplicado. Final: {final_antes:.2f} -> {final_despues:.2f}",
            text_color="#1B5E20",
        )

    CTkButton(form, text="Aplicar bonus materia", fg_color=COLOR_MAIN, hover_color=COLOR_HOVER,
              font=BUTTON_FONT, command=aplicar).pack(anchor="e", padx=10, pady=(4, 10))


def obtener_resumen_alumno(id_registro, id_grupo):
    sql = """
        SELECT A.id_unidad, A.ponderacion, RES.calificacion
        FROM unidad U
        JOIN actividad A ON A.id_unidad = U.id_unidad
        LEFT JOIN resultado RES
            ON RES.id_registro = %s AND RES.id_actividad = A.id_actividad
        WHERE U.id_grupo = %s
    """
    filas = ejecutar_select(sql, (id_registro, id_grupo))
    if not filas:
        return 0.0, 0.0

    unidades = {}
    tiene_pendientes = False
    for id_unidad, ponderacion, calificacion in filas:
        clave = str(id_unidad).strip()
        if clave not in unidades:
            unidades[clave] = {"base": 0.0}

        por = a_numero(ponderacion) or 0.0
        cal = a_numero(calificacion)
        if cal is None:
            tiene_pendientes = True
            continue
        unidades[clave]["base"] += cal * (por / 100.0)

    if not unidades:
        return 0.0, 0.0

    suma_base = 0.0
    suma_final = 0.0
    for clave, data in unidades.items():
        bonus = obtener_bonus_unidad(id_registro, clave)
        base = min(100.0, data["base"])
        final = min(100.0, base + bonus)
        suma_base += base
        suma_final += final

    promedio_base = round(suma_base / len(unidades), 2)
    promedio_final = round(suma_final / len(unidades), 2)
    return promedio_base, promedio_final


def obtener_etiquetas_unidad(ids_unidad):
    if not ids_unidad:
        return {}
    marcadores = ",".join(["%s"] * len(ids_unidad))
    sql = f"""
        SELECT id_unidad, numero_unidad
        FROM unidad
        WHERE id_unidad IN ({marcadores})
    """
    filas = ejecutar_select(sql, tuple(ids_unidad))
    etiquetas = {}
    conteo_numero = {}
    for id_u, numero_u in filas:
        clave_num = str(numero_u).strip()
        conteo_numero[clave_num] = conteo_numero.get(clave_num, 0) + 1

    for id_u, numero_u in filas:
        id_txt = str(id_u).strip()
        num_txt = str(numero_u).strip()
        if conteo_numero.get(num_txt, 0) > 1:
            etiquetas[id_txt] = f"Unidad {num_txt} ({id_txt})"
        else:
            etiquetas[id_txt] = f"Unidad {num_txt}"
    return etiquetas


def obtener_unidades_con_actividad_grupo(id_grupo):
    sql = """
        SELECT DISTINCT A.id_unidad
        FROM actividad A
        JOIN unidad U ON A.id_unidad = U.id_unidad
        WHERE U.id_grupo = %s
        ORDER BY A.id_unidad
    """
    filas = ejecutar_select(sql, (id_grupo,))
    return [str(f[0]).strip() for f in filas if f and f[0] is not None]


def calcular_calificaciones_unidad_alumno(id_registro, id_grupo):
    sql = """
        SELECT A.id_unidad, A.ponderacion, RES.calificacion
        FROM unidad U
        JOIN actividad A ON A.id_unidad = U.id_unidad
        LEFT JOIN resultado RES
            ON RES.id_actividad = A.id_actividad
            AND RES.id_registro = %s
        WHERE U.id_grupo = %s
        ORDER BY U.numero_unidad, A.id_actividad
    """
    filas = ejecutar_select(sql, (id_registro, id_grupo))

    por_unidad = {}
    for id_unidad, ponderacion, calificacion in filas:
        clave = str(id_unidad).strip()
        if clave not in por_unidad:
            por_unidad[clave] = {"ponderada": 0.0,
                                 "pendiente": False, "tiene_calif": False}

        por = a_numero(ponderacion) or 0.0
        cal = a_numero(calificacion)
        if cal is None:
            por_unidad[clave]["pendiente"] = True
            continue

        por_unidad[clave]["ponderada"] += cal * (por / 100.0)
        por_unidad[clave]["tiene_calif"] = True

    return por_unidad


def obtener_resumen_alumno(id_registro, id_grupo):
    sql = """
        SELECT A.id_unidad, A.ponderacion, RES.calificacion
        FROM unidad U
        JOIN actividad A ON A.id_unidad = U.id_unidad
        LEFT JOIN resultado RES
            ON RES.id_registro = %s AND RES.id_actividad = A.id_actividad
        WHERE U.id_grupo = %s
    """
    filas = ejecutar_select(sql, (id_registro, id_grupo))
    if not filas:
        return 0.0, 0.0

    unidades = {}
    for id_unidad, ponderacion, calificacion in filas:
        clave = str(id_unidad).strip()
        if clave not in unidades:
            unidades[clave] = {"base": 0.0}

        por = a_numero(ponderacion) or 0.0
        cal = a_numero(calificacion)
        if cal is None:
            continue
        unidades[clave]["base"] += cal * (por / 100.0)

    if not unidades:
        return 0.0, 0.0

    suma_base = 0.0
    suma_final = 0.0
    for clave, data in unidades.items():
        bonus = obtener_bonus_unidad(id_registro, clave)
        base = min(100.0, data["base"])
        final = min(100.0, base + bonus)
        suma_base += base
        suma_final += final

    promedio_base = round(suma_base / len(unidades), 2)
    promedio_final = round(suma_final / len(unidades), 2)
    return promedio_base, promedio_final


def crear_tabla_participantes_con_calificaciones(parent, id_grupo):
    # Obtener clave_grupo
    sql_clave = "SELECT clave_grupo FROM grupo WHERE id_grupo = %s LIMIT 1"
    resultado_clave = ejecutar_select(sql_clave, (id_grupo,))
    clave_grupo = resultado_clave[0][0] if resultado_clave else id_grupo

    participantes_sql = """
        SELECT R.id_registro, A.nombre_alumno, A.apellido_paterno, A.apellido_materno
        FROM registro R
        JOIN alumno A ON R.id_alumno = A.id_alumno
        WHERE R.id_grupo = %s
        ORDER BY A.apellido_paterno, A.apellido_materno, A.nombre_alumno
    """
    participantes = ejecutar_select(participantes_sql, (id_grupo,))
    id_materia_grupo = obtener_materia_grupo(id_grupo)

    ids_unidad = obtener_unidades_con_actividad_grupo(id_grupo)
    etiquetas_unidad = obtener_etiquetas_unidad(ids_unidad)

    tabla = CTkFrame(parent)
    tabla.pack(fill="both", expand=True)

    encabezados = ["Nombre", "A. Paterno", "A. Materno"]
    encabezados.extend([etiquetas_unidad.get(
        uid, f"U{uid}") for uid in ids_unidad])
    encabezados.append("Final")

    header = CTkFrame(tabla, fg_color="#1f6aa5")
    header.pack(fill="x")
    for i, texto in enumerate(encabezados):
        header.grid_columnconfigure(i, weight=1)
        CTkLabel(header, text=texto, text_color="white",
                 font=("Arial", 13, "bold"), anchor="w",
                 ).grid(row=0, column=i, padx=10, pady=10, sticky="w")

    cuerpo = CTkScrollableFrame(tabla, fg_color="#ffffff")
    cuerpo.pack(fill="both", expand=True)

    if not participantes:
        CTkLabel(cuerpo, text=f"No hay alumnos inscritos en el grupo {clave_grupo}.",
                 text_color="#444444", font=("Arial", 13)).pack(pady=20)
        return

    for fila_idx, (id_registro, nombre, ap_pat, ap_mat) in enumerate(participantes):
        datos_base = [nombre, ap_pat, ap_mat]
        califs_unidad = calcular_calificaciones_unidad_alumno(
            id_registro, id_grupo)

        valores_unidad = []
        for uid in ids_unidad:
            info_u = califs_unidad.get(uid)
            if not info_u or not info_u["tiene_calif"]:
                valores_unidad.append("0.00")
                continue
            valor_u = round(min(100.0, info_u["ponderada"]), 2)
            valores_unidad.append(f"{valor_u:.2f}")

        _, final_unidades = obtener_resumen_alumno(id_registro, id_grupo)
        bonus_materia = obtener_bonus_materia(
            id_registro, id_grupo) if id_materia_grupo else 0.0
        final_real = min(100.0, final_unidades + bonus_materia)
        final_txt = f"{final_real:.2f}"

        # Determinar color de fondo según calificación final
        color_fila = "#C8E6C9" if final_real >= 70 else "#FFCDD2"  # Verde o rojo claro

        fila = datos_base + valores_unidad + [final_txt]
        for col_idx, valor in enumerate(fila):
            cuerpo.grid_columnconfigure(col_idx, weight=1)
            CTkLabel(cuerpo, text=str(valor), text_color="#111111",
                     font=("Arial Rounded MT Bold", 14), anchor="w", justify="left",
                     fg_color=color_fila
                     ).grid(row=fila_idx, column=col_idx, padx=10, pady=8, sticky="ew")


def agregar_unidad_general(frame):
    limpiar_frame(frame)
    CTkLabel(frame, text="Agregar Unidad", text_color="black", anchor="w",
             font=("Arial Rounded MT Bold", 30)).pack(fill="x", padx=10, pady=10)
    CTkLabel(frame, text="Selecciona un grupo para asignar la nueva unidad.",
             text_color="gray").pack(anchor="w", padx=12, pady=(0, 8))

    grupos = obtener_grupos_maestro(matricula_maestro)
    if not grupos:
        CTkLabel(frame, text="No tienes grupos asignados.", text_color="#B00020",
                 font=("Arial Rounded MT Bold", 16)).pack(anchor="w", padx=12, pady=12)
        return

    form = CTkFrame(frame, fg_color="white")
    form.pack(padx=20, pady=10, fill="both", expand=True)

    e_numero = CTkOptionMenu(form, values=["Selecciona un grupo primero"], text_color="black", fg_color="#F0F0F0", button_color="#E0E0E0", button_hover_color="#D0D0D0")
    e_numero.configure(state="disabled")
    e_tema = CTkEntry(form, placeholder_text="Tema de la unidad")
    e_desc = CTkEntry(form, placeholder_text="Descripción")
    e_numero.pack(fill="x", padx=10, pady=6)
    e_tema.pack(fill="x", padx=10, pady=6)
    e_desc.pack(fill="x", padx=10, pady=6)

    CTkLabel(form, text="Grupos", text_color="black",
             font=("Arial Rounded MT Bold", 16)).pack(anchor="w", padx=10, pady=(10, 6))

    lista = CTkScrollableFrame(form, fg_color="#F8FCFD", height=240)
    lista.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    grupo_seleccionado = StringVar(value="")

    def actualizar_opciones_unidad():
        unidades_disponibles = mostrar_unidades_disponibles()
        if not unidades_disponibles:
            e_numero.configure(values=["Selecciona un grupo primero"])
            e_numero.set("Selecciona un grupo primero")
            e_numero.configure(state="disabled")
            return

        e_numero.configure(values=unidades_disponibles)
        e_numero.set(unidades_disponibles[0])
        e_numero.configure(state="normal")

    for clave_grupo, id_grupo, _, nombre_materia in grupos:
        fila = CTkFrame(lista, fg_color="white")
        fila.pack(fill="x", padx=4, pady=4)
        CTkRadioButton(
            fila,
            text=f"Grupo {clave_grupo} - {nombre_materia}",
            variable=grupo_seleccionado,
            value=str(id_grupo),
            command=actualizar_opciones_unidad,
        ).pack(anchor="w", padx=10, pady=8)

    estado = CTkLabel(form, text="", text_color="gray")
    estado.pack(anchor="w", padx=10, pady=6)

    def mostrar_unidades_disponibles():
        grupo = grupo_seleccionado.get().strip()
        if not grupo:
            estado.configure(
                text="Selecciona un grupo.",
                text_color="#B00020",
            )
            return {}

        sql = """
            SELECT
                g.id_grupo,
                g.id_materia,
                m.unidades AS total_unidades
            FROM grupo g
            JOIN materia m ON g.id_materia = m.id_materia
            WHERE g.id_grupo = %s
        """
        numero_unidades = ejecutar_select(sql, (grupo,))
        if not numero_unidades:
            estado.configure(
                text="No se encontró información para el grupo seleccionado.",
                text_color="#B00020",
            )
            return {}

        unidades = obtener_unidades_grupo(grupo)

        total = int(numero_unidades[0][2] if numero_unidades else 5)
        existentes = set()
        for fila in unidades or []:
            try:
                existentes.add(int(fila[1]))
            except Exception:
                continue

        unidades_disponibles = [
            str(numero)
            for numero in range(1, total + 1)
            if numero not in existentes
        ]

        return unidades_disponibles

    def guardar_unidad_general():
        numero = e_numero.get().strip()
        tema = e_tema.get().strip()
        descripcion = e_desc.get().strip()
        grupo = grupo_seleccionado.get().strip()

        if not numero or not tema:
            estado.configure(
                text="Número de unidad y tema son obligatorios.", text_color="#B00020")
            return
        if not grupo:
            estado.configure(
                text="Selecciona un grupo.", text_color="#B00020")
            return

        sql = """
            INSERT INTO unidad (numero_unidad, tema_unidad, descripcion, id_grupo)
            VALUES (%s, %s, %s, %s)
        """
        try:
            ejecutar_insert(sql, (numero, tema, descripcion, grupo))
            estado.configure(
                text="Unidad agregada correctamente.", text_color="#1B5E20")
            actualizar_opciones_unidad()
        except Exception as ex:
            estado.configure(
                text=f"Error al agregar unidad: {ex}", text_color="#B00020")

    actualizar_opciones_unidad()

    CTkButton(form, text="Guardar unidad", fg_color=COLOR_MAIN, hover_color=COLOR_HOVER,
              font=BUTTON_FONT, command=guardar_unidad_general).pack(anchor="e", padx=10, pady=(0, 10))


def menu_opciones(frame_menu):
    global nombre_maestro, matricula_maestro, _btn_nav_activo

    # ── Logo ──────────────────────────────────────────────────────────────
    try:
        logo_img = CTkImage(light_image=Image.open(
            "carpeta_iconos/general/logo.jpeg"), size=(200, 95))
        frame_logo = CTkFrame(frame_menu, fg_color="#FFFFFF", corner_radius=0)
        frame_logo.pack(fill="x")
        CTkLabel(frame_logo, text="", image=logo_img,
                 bg_color="#FFFFFF").pack(padx=10, pady=8)
    except Exception:
        frame_logo = CTkFrame(frame_menu, fg_color="#FFFFFF",
                              corner_radius=0, height=65)
        frame_logo.pack(fill="x")

    # ── Perfil del usuario ────────────────────────────────────────────────
    frame_user = CTkFrame(frame_menu, fg_color=COLOR_SIDE)
    frame_user.pack(pady=(14, 5), padx=12, fill="x")

    try:
        avatar_img = CTkImage(light_image=Image.open(
            "carpeta_iconos/iconos_alumnos/avatar.png"), size=(80, 80))
        frame_circle = CTkFrame(
            frame_user, fg_color="#A8D8E8", corner_radius=50, width=96, height=96)
        frame_circle.pack(pady=(10, 6))
        frame_circle.pack_propagate(False)
        CTkLabel(frame_circle, text="", image=avatar_img,
                 fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
    except Exception:
        CTkLabel(frame_user, text="👤", font=("Arial", 50)).pack(pady=10)

    CTkLabel(frame_user,
             text=nombre_maestro or "Maestro",
             text_color="#0a0a0a",
             font=("Arial Rounded MT Bold", 15),
             wraplength=210,
             justify="center").pack(pady=(2, 2))
    CTkLabel(frame_user,
             text=matricula_maestro or "-",
             text_color="gray",
             font=("Arial", 13)).pack(pady=(0, 12))

    # ── Cerrar Sesión al fondo (debe empaquetar antes de expand=True) ─────
    frame_bottom = CTkFrame(frame_menu, fg_color=COLOR_SIDE, corner_radius=0)
    frame_bottom.pack(side="bottom", fill="x", padx=8, pady=10)
    try:
        salida_icon = crear_icono("carpeta_iconos/iconos_alumnos/salida.png", size=(22, 22), color="#1a1a1a")
    except Exception:
        salida_icon = None
    CTkButton(frame_bottom,
              text="  Cerrar Sesión",
              image=salida_icon,
              anchor="w",
              fg_color="white",
              hover_color="#EAF6FF",
              text_color="#1a1a1a",
              font=BUTTON_FONT,
              command=cerrar_sesion,
              corner_radius=12,
              height=56).pack(pady=10, padx=12, fill="x")

    # ── Botones de navegación ─────────────────────────────────────────────
    frame_nav = CTkFrame(frame_menu, fg_color=COLOR_SIDE)
    frame_nav.pack(pady=(5, 0), padx=10, fill="both", expand=True)

    _btn_nav_activo[0] = None

    btn_grupos = nav_btn(
        frame_nav, "Mis Grupos",
        crear_icono("carpeta_iconos/iconos_alumnos/hogar.png", size=(22,22), color="#1a1a1a"),
        lambda: mis_grupos(frame_contenido))

    nav_btn(
        frame_nav, "Agregar Unidad",
        crear_icono("carpeta_iconos/iconos_alumnos/lista.png", size=(22,22), color="#1a1a1a"),
        lambda: agregar_unidad_general(frame_contenido))

    nav_btn(
        frame_nav, "Configuracion de Perfil",
        crear_icono("carpeta_iconos/iconos_admin/usuario.png", size=(22,22), color="#1a1a1a"),
        lambda: Configuracion_Perfil_Maestro())

    # Activar "Mis Grupos" por defecto
    btn_grupos.configure(
        fg_color=COLOR_MAIN, text_color="white", hover_color=COLOR_HOVER)
    _btn_nav_activo[0] = btn_grupos


def Configuracion_Perfil_Maestro():
    global matricula_maestro, frame_contenido
    limpiar_frame(frame_contenido)

    encabezado = CTkFrame(frame_contenido, fg_color="white")
    encabezado.pack(fill="x", padx=10, pady=(10, 6))

    CTkLabel(
        encabezado,
        text="Configuracion de Perfil",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 30)
    ).pack(fill="x", anchor="w", pady=(10, 4), padx=12)

    CTkLabel(
        encabezado,
        text="Consulta tu informacion y actualiza tu contrasena",
        text_color="gray",
        anchor="w",
        font=("Arial", 16)
    ).pack(fill="x", anchor="w", padx=12, pady=(0, 10))

    tarjeta_info = CTkFrame(frame_contenido, fg_color=COLOR_SIDE)
    tarjeta_info.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    if not matricula_maestro:
        CTkLabel(
            tarjeta_info,
            text="No hay una sesion de maestro activa.",
            text_color="black",
            anchor="w",
            font=("Arial", 16)
        ).pack(fill="x", padx=10, pady=10)
        return

    consulta_maestro = """
        SELECT
            TRIM(nombre_maestro),
            TRIM(apellido_paterno),
            TRIM(apellido_materno),
            COALESCE(TRIM(correo), ''),
            COALESCE(TRIM(perfil_docente), ''),
            COALESCE(TRIM(cedula_profesional), '')
        FROM maestro
        WHERE matricula = %s
        LIMIT 1
    """
    datos_maestro = ejecutar_select(consulta_maestro, (matricula_maestro,))

    if not datos_maestro:
        CTkLabel(
            tarjeta_info,
            text="No se encontro informacion del maestro en sesion.",
            text_color="black",
            anchor="w",
            font=("Arial", 16)
        ).pack(fill="x", padx=10, pady=10)
        return

    nombre, ap_paterno, ap_materno, correo, perfil_docente, cedula_profesional = datos_maestro[
        0]
    nombre_completo = " ".join(
        [parte for parte in [nombre, ap_paterno, ap_materno] if parte])

    CTkLabel(
        tarjeta_info,
        text=f"Nombre: {nombre_completo}",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 20)
    ).pack(fill="x", padx=12, pady=(10, 6))

    CTkLabel(
        tarjeta_info,
        text=f"Matricula: {matricula_maestro}",
        text_color="#333333",
        anchor="w",
        font=("Arial", 16)
    ).pack(fill="x", padx=12, pady=4)

    CTkLabel(
        tarjeta_info,
        text=f"Correo: {correo if correo else 'Sin correo registrado'}",
        text_color="#333333",
        anchor="w",
        font=("Arial", 16)
    ).pack(fill="x", padx=12, pady=4)

    CTkLabel(
        tarjeta_info,
        text=f"Perfil docente: {perfil_docente if perfil_docente else 'Sin perfil registrado'}",
        text_color="#333333",
        anchor="w",
        font=("Arial", 16)
    ).pack(fill="x", padx=12, pady=4)

    CTkLabel(
        tarjeta_info,
        text=f"Cedula profesional: {cedula_profesional if cedula_profesional else 'Sin cedula registrada'}",
        text_color="#333333",
        anchor="w",
        font=("Arial", 16)
    ).pack(fill="x", padx=12, pady=(4, 10))

    frame_formulario = CTkFrame(tarjeta_info, fg_color=COLOR_MAIN)
    frame_formulario.pack(fill="x", padx=12, pady=(5, 10))
    frame_formulario.pack_forget()

    CTkLabel(
        frame_formulario,
        text="Nueva contrasena",
        text_color="white",
        anchor="w",
        font=("Arial Rounded MT Bold", 14)
    ).pack(fill="x", padx=10, pady=(10, 5))

    entry_nueva = CTkEntry(
        frame_formulario,
        show="*",
        width=340,
        fg_color="white",
        text_color="black",
        border_color=COLOR_HOVER
    )
    entry_nueva.pack(fill="x", padx=10, pady=(0, 10))

    CTkLabel(
        frame_formulario,
        text="Confirmar contrasena",
        text_color="white",
        anchor="w",
        font=("Arial Rounded MT Bold", 14)
    ).pack(fill="x", padx=10, pady=(0, 5))

    entry_confirmar = CTkEntry(
        frame_formulario,
        show="*",
        width=340,
        fg_color="white",
        text_color="black",
        border_color=COLOR_HOVER
    )
    entry_confirmar.pack(fill="x", padx=10, pady=(0, 10))

    estado_contrasena = {"visible": False}

    def alternar_visibilidad_contrasena():
        if estado_contrasena["visible"]:
            entry_nueva.configure(show="*")
            entry_confirmar.configure(show="*")
            boton_mostrar.configure(text="Mostrar contrasena")
            estado_contrasena["visible"] = False
        else:
            entry_nueva.configure(show="")
            entry_confirmar.configure(show="")
            boton_mostrar.configure(text="Ocultar contrasena")
            estado_contrasena["visible"] = True

    label_estado = CTkLabel(
        frame_formulario,
        text="",
        text_color="white",
        anchor="w",
        justify="left",
        font=("Arial", 14)
    )
    label_estado.pack(fill="x", padx=10, pady=(0, 10))

    def guardar_nueva_contrasena():
        nueva = entry_nueva.get().strip()
        confirmar = entry_confirmar.get().strip()

        if not nueva or not confirmar:
            label_estado.configure(
                text="Completa ambos campos.", text_color="#a11")
            return

        if nueva != confirmar:
            label_estado.configure(
                text="Las contrasenas no coinciden.", text_color="#a11")
            return

        try:
            sql_update = """
                UPDATE cuentas
                SET password = %s
                WHERE id_cuenta = (
                    SELECT id_cuenta
                    FROM maestro
                    WHERE matricula = %s
                    LIMIT 1
                )
            """
            ejecutar_insert(sql_update, (nueva, matricula_maestro))
            label_estado.configure(
                text="Contrasena actualizada correctamente.", text_color="#1d6f42")
            entry_nueva.delete(0, "end")
            entry_confirmar.delete(0, "end")
        except Exception:
            label_estado.configure(
                text="No fue posible actualizar la contrasena.", text_color="#a11")

    frame_botones = CTkFrame(frame_formulario, fg_color="transparent")
    frame_botones.pack(fill="x", padx=10, pady=(0, 10))

    boton_mostrar = CTkButton(
        frame_botones,
        text="Mostrar contrasena",
        fg_color=COLOR_HOVER,
        hover_color=COLOR_MAIN,
        text_color="white",
        font=("Arial Rounded MT Bold", 12),
        width=180,
        command=alternar_visibilidad_contrasena
    )
    boton_mostrar.pack(side="left")

    boton_guardar = CTkButton(
        frame_botones,
        text="Guardar contrasena",
        fg_color=COLOR_MAIN,
        hover_color=COLOR_HOVER,
        text_color="white",
        font=("Arial Rounded MT Bold", 14),
        command=guardar_nueva_contrasena
    )
    boton_guardar.pack(side="right")

    estado_formulario = {"visible": False}

    def alternar_formulario():
        if estado_formulario["visible"]:
            frame_formulario.pack_forget()
            estado_formulario["visible"] = False
        else:
            frame_formulario.pack(fill="x", padx=12, pady=(5, 10))
            estado_formulario["visible"] = True

    CTkButton(
        tarjeta_info,
        text="Modificar contrasena",
        fg_color=COLOR_MAIN,
        hover_color=COLOR_HOVER,
        text_color="white",
        font=("Arial Rounded MT Bold", 14),
        command=alternar_formulario
    ).pack(anchor="e", padx=12, pady=(0, 12))


def nav_btn(parent, texto, img, cmd):
    """Botón de navegación con soporte de estado activo."""
    def on_click():
        if _btn_nav_activo[0] is not None:
            try:
                _btn_nav_activo[0].configure(
                    fg_color="white",
                    text_color="#1a1a1a",
                    hover_color="#EAF6FF"
                )
            except Exception:
                pass
        b.configure(fg_color=COLOR_MAIN, text_color="white",
                    hover_color=COLOR_HOVER)
        _btn_nav_activo[0] = b
        cmd()

    b = CTkButton(
        parent,
        text=f"  {texto}",
        image=img,
        anchor="w",
        fg_color="white",
        hover_color="#EAF6FF",
        text_color="#1a1a1a",
        font=BUTTON_FONT,
        command=on_click,
        corner_radius=12,
        height=56
    )
    b.pack(pady=10, padx=12, fill="x")
    return b


def btn(parent, texto, img, cmd):
    CTkButton(parent, text=texto, image=img, anchor="w",
              fg_color=COLOR_MAIN, hover_color=COLOR_HOVER, text_color="white",
              font=BUTTON_FONT, command=cmd).pack(pady=8, padx=10, fill="x")


def aplicar_fuente_tabview(tabview):
    try:
        tabview._segmented_button.configure(font=("Arial", 16, "bold"))
    except Exception:
        pass


def informacion_general_grupo(frame, id_grupo):
    limpiar_frame(frame)

    id_grupo_sql = str(id_grupo).strip()
    contenedor = CTkScrollableFrame(frame, fg_color="white")
    contenedor.pack(fill="both", expand=True, padx=8, pady=8)

    frame_info = CTkFrame(contenedor, fg_color="#DFF4F7")
    frame_info.pack(fill="x", padx=5, pady=5)

    consulta = """
        SELECT
            G.clave_grupo,
            M.id_materia,
            M.nombre_materia,
            M.horas_semana,
            G.cupo_maximo,
            G.periodo,
            G.years,
            G.estado,
            COUNT(R.id_registro) AS alumnos_reales
        FROM grupo G
        JOIN materia M ON G.id_materia = M.id_materia
        LEFT JOIN registro R ON R.id_grupo = G.id_grupo
        WHERE G.id_grupo = %s
        GROUP BY G.clave_grupo, M.id_materia, M.nombre_materia,
                 M.horas_semana, G.cupo_maximo, G.periodo, G.years, G.estado
        LIMIT 1
    """
    resultado = ejecutar_select(consulta, (id_grupo_sql,))

    if resultado:
        clave_grupo, id_materia, nombre_materia, horas_semana, cupo, periodo, years, estado, alumnos_reales = resultado[0]
        CTkLabel(frame_info, text=f"Grupo: {clave_grupo}", text_color="black",
                 font=("Arial Rounded MT Bold", 20)).pack(anchor="w", padx=10, pady=(8, 2))
        CTkLabel(frame_info, text=f"Materia: {nombre_materia}", text_color="black",
                 font=("Arial Rounded MT Bold", 15)).pack(anchor="w", padx=10, pady=2)
        CTkLabel(frame_info,
                 text=f"Alumnos inscritos: {alumnos_reales}    Periodo: {periodo}",
                 text_color="black", font=("Arial Rounded MT Bold", 13)).pack(anchor="w", padx=10, pady=(2, 4))
        CTkLabel(frame_info,
                 text=f"Año: {years}    Estado del grupo: {estado}",
                 text_color="black", font=("Arial Rounded MT Bold", 13)).pack(anchor="w", padx=10, pady=(0, 8))
    else:
        CTkLabel(frame_info, text="No se encontró información general del grupo.",
                 text_color="#B00020", font=("Arial Rounded MT Bold", 14)).pack(anchor="w", padx=10, pady=10)

    CTkLabel(contenedor, text="Participantes inscritos", text_color="black",
             font=("Arial Rounded MT Bold", 18)).pack(anchor="w", padx=8, pady=(8, 4))
    frame_participantes = CTkFrame(contenedor, fg_color="white", height=280)
    frame_participantes.pack(fill="x", padx=5, pady=(0, 8))
    frame_participantes.pack_propagate(False)
    crear_tabla_participantes_con_calificaciones(
        frame_participantes, id_grupo_sql)


def ver_grupo(frame, id_grupo):
    limpiar_frame(frame)
    header = CTkFrame(frame, fg_color="white")
    header.pack(fill="x", padx=10, pady=(10, 4))

    # Obtener clave_grupo
    sql_clave = "SELECT clave_grupo FROM grupo WHERE id_grupo = %s LIMIT 1"
    resultado_clave = ejecutar_select(sql_clave, (id_grupo,))
    clave_grupo = resultado_clave[0][0] if resultado_clave else id_grupo

    CTkLabel(header, text=f"Grupo {clave_grupo}", text_color="black", anchor="w",
             font=("Arial Rounded MT Bold", 30)).pack(side="left")

    CTkButton(header, text="Actualizar", fg_color=COLOR_MAIN, hover_color=COLOR_HOVER,
              font=("Arial Rounded MT Bold", 14), width=150,
              command=lambda: ver_grupo(frame, id_grupo),
              ).pack(side="right", padx=(8, 0), pady=4)

    tabview = CTkTabview(
        frame,
        fg_color="#F2FBFD",
        segmented_button_fg_color="#BFEAF1",
        segmented_button_selected_color=COLOR_MAIN,
        segmented_button_selected_hover_color=COLOR_HOVER,
        segmented_button_unselected_color="#7CC9D6",
        segmented_button_unselected_hover_color="#5CB8C9",
        text_color="white",
    )
    aplicar_fuente_tabview(tabview)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)
    tabview.add("Informacion general")
    tabview.add("Asignar actividad")
    tabview.add("Eliminar actividad")
    tabview.add("Actividades")
    tabview.add("Bonus")

    # Frames de cada pestaña
    frame_info_general = CTkFrame(tabview.tab("Informacion general"), fg_color="#F2FBFD")
    frame_info_general.pack(fill="both", expand=True)

    frame_asignar = CTkFrame(tabview.tab("Asignar actividad"), fg_color="#F2FBFD")
    frame_asignar.pack(fill="both", expand=True)

    frame_eliminar = CTkFrame(tabview.tab("Eliminar actividad"), fg_color="#F2FBFD")
    frame_eliminar.pack(fill="both", expand=True)

    frame_pend = CTkFrame(tabview.tab("Actividades"), fg_color="#F2FBFD")
    frame_pend.pack(fill="both", expand=True)

    frame_bonus = CTkFrame(tabview.tab("Bonus"), fg_color="#F2FBFD")
    frame_bonus.pack(fill="both", expand=True)

    # Renderizar la primera pestaña inmediatamente
    informacion_general_grupo(frame_info_general, id_grupo)

    # Lazy loading: renderizar cada pestaña solo cuando se selecciona
    cargadas = {"Informacion general"}

    def on_tab_change():
        tab = tabview.get()
        print(f"DEBUG: on_tab_change tab={tab} id_grupo={id_grupo}")
        if tab in cargadas:
            return
        cargadas.add(tab)
        if tab == "Asignar actividad":
            asignar_actividad(frame_asignar, id_grupo)
        elif tab == "Eliminar actividad":
            eliminar_actividades(frame_eliminar, id_grupo)
        elif tab == "Actividades":
            pendientes(frame_pend, id_grupo)
        elif tab == "Bonus":
            from codigo_maestros.funciones_actividad import vista_bonus
            vista_bonus(frame_bonus, id_grupo)

    tabview.configure(command=on_tab_change)


def pendientes(frame, id_grupo):
    from codigo_maestros.funciones_actividad import vista_actividades

    sql = """
        SELECT m.nombre_materia
        FROM grupo g
        JOIN materia m ON g.id_materia = m.id_materia
        WHERE g.id_grupo = %s
        LIMIT 1
    """
    resultado = ejecutar_select(sql, (id_grupo,))
    nombre_materia = resultado[0][0] if resultado else ""

    vista_actividades(frame, id_grupo, nombre_materia)


def eliminar_actividades(frame, id_grupo):
    limpiar_frame(frame)
    CTkLabel(frame, text="Eliminar actividades", text_color="black", anchor="w",
             font=("Arial", 30, "bold")).pack(fill="x", padx=10, pady=10)
    CTkLabel(frame, text="Elimina actividades asignadas previamente en este grupo.",
             text_color="gray", font=("Arial", 14)).pack(anchor="w", padx=12, pady=(0, 8))

    estado = CTkLabel(frame, text="", text_color="gray", font=("Arial", 12))
    estado.pack(anchor="w", padx=12, pady=(0, 6))

    contenedor = CTkScrollableFrame(frame, fg_color="#F2FBFD")
    contenedor.pack(fill="both", expand=True, padx=10, pady=10)

    actividades = obtener_actividades_grupo(id_grupo)
    if not actividades:
        CTkLabel(contenedor, text="No hay actividades para eliminar en este grupo.",
                 text_color="gray", font=("Arial", 14)).pack(anchor="w", padx=10, pady=10)
        return

    for id_actividad, id_unidad, numero_unidad, id_tipo, tipo_actividad, detalles, ponderacion in actividades:
        card = CTkFrame(contenedor, fg_color="white",
                        border_width=1, border_color="#E0E0E0")
        card.pack(fill="x", padx=5, pady=6)

        etiqueta_tipo = tipo_actividad.strip() if tipo_actividad else f"Tipo {id_tipo}" if id_tipo is not None else "Tipo sin asignar"
        card.configure(height=165)
        card.pack_propagate(False)
        contenido = CTkFrame(card, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=16, pady=(8, 4))

        CTkLabel(contenido, text=f"{etiqueta_tipo}", text_color="black",
               font=("Arial", 16, "bold")).pack(anchor="w")
        badge_unidad = CTkFrame(contenido, fg_color=COLOR_AZUL, corner_radius=12)
        badge_unidad.pack(anchor="w", pady=(4, 4))
        CTkLabel(badge_unidad, text=f"Unidad {numero_unidad}", text_color="white",
               font=("Arial", 12, "bold"), padx=12, pady=4).pack()
        CTkLabel(contenido, text=f"ID actividad: {id_actividad}",
               text_color="#555555", font=("Arial", 11)).pack(anchor="w", pady=(0, 4))
        CTkLabel(contenido, text=f"Ponderación: {ponderacion}%",
               text_color="#444444", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        CTkLabel(contenido, text=f"Detalles: {detalles}", text_color="#666666",
               font=("Arial", 10), wraplength=720, justify="left").pack(anchor="w", pady=(0, 2))

        def eliminar_actual(ia=id_actividad):
            try:
                eliminar_actividad_por_id(id_grupo, ia)
                estado.configure(
                    text=f"Actividad eliminada: {ia}", text_color="#1B5E20")
                eliminar_actividades(frame, id_grupo)
            except Exception as ex:
                estado.configure(
                    text=f"No se pudo eliminar la actividad {ia}: {ex}", text_color="#B00020")

        CTkButton(contenido, text="Eliminar", fg_color="#B00020", hover_color="#8E0000",
              font=("Arial", 14, "bold"), width=160, height=38,
              corner_radius=10,
              command=eliminar_actual).place(relx=0.98, rely=0.78, anchor="e")


def mis_grupos(frame):
    limpiar_frame(frame)
    CTkLabel(frame, text="Mis Grupos", text_color="black", anchor="w",
             font=("Arial Rounded MT Bold", 34)).pack(fill="x", padx=10, pady=(14, 2))
    CTkLabel(frame, text="Gestiona tus grupos asignados", text_color="gray",
             font=("Arial", 15)).pack(anchor="w", padx=12, pady=(0, 10))

    grupos = obtener_grupos_maestro(matricula_maestro)

    cont = CTkScrollableFrame(frame, fg_color="white")
    cont.pack(padx=10, pady=5, fill="both", expand=True)

    if not grupos:
        CTkLabel(cont, text="No tienes grupos asignados.", text_color="black",
                 font=("Arial Rounded MT Bold", 18)).grid(
                     row=0, column=0, padx=10, pady=10, sticky="w")
        return

    # Intentar cargar ícono de grupo: preferir el recurso en carpeta 'general', luego caer a iconos_alumnos
    grupo_icon = None
    posibles = [
        "carpeta_iconos/general/grupo.png",
        "carpeta_iconos/general/grupo.jpeg",
        "carpeta_iconos/general/grupo.jpg",
        "carpeta_iconos/iconos_alumnos/grupo.png",
        "carpeta_iconos/iconos_alumnos/usuarios.png",
        "carpeta_iconos/iconos_alumnos/archivo-de-carpetas.png",
        "carpeta_iconos/iconos_alumnos/avatar.png",
    ]
    # DESPUÉS:
    for ruta in posibles:
        try:
            grupo_icon = crear_icono(ruta, (70, 70), color="#FFFFFF")
            if grupo_icon:
                break
        except Exception:
            continue

    COLS = 4  # tarjetas por fila
    for i, (clave_grupo, id_grupo, _, materia) in enumerate(grupos):
        r, c = i // COLS, i % COLS

        # ── Tarjeta exterior (fondo teal con esquinas redondeadas) ────────
        card = CTkFrame(
            cont,
            fg_color="#4b7b9c",
            corner_radius=14,
            width=260,
            height=210,
            cursor="hand2"
        )
        card.grid(row=r, column=c, padx=10, pady=10)
        card.pack_propagate(False)
        card.grid_propagate(False)

        # ── Ícono centrado en la parte teal ──────────────────────────────
        lbl_icon = CTkLabel(card, text="", image=grupo_icon,
                    fg_color="transparent")
        lbl_icon.pack(expand=True, fill="both", padx=20, pady=(14, 8))

        # ── Sección blanca inferior ───────────────────────────────────────
        bottom = CTkFrame(card, fg_color="white", corner_radius=10)
        bottom.pack(fill="x", side="bottom", padx=6, pady=(0, 6))

        lbl_clave = CTkLabel(bottom, text=clave_grupo, text_color=COLOR_MAIN,
                             font=("Arial Rounded MT Bold", 20))
        lbl_clave.pack(pady=(8, 2))

        lbl_materia = CTkLabel(bottom, text=materia, text_color="gray",
                               font=("Arial", 13))
        lbl_materia.pack(pady=(0, 8))

        # ── Hacer toda la tarjeta clicleable ─────────────────────────────
        for widget in (card, lbl_icon, bottom, lbl_clave, lbl_materia):
            widget.bind("<Button-1>",
                        lambda e, g=id_grupo: ver_grupo(frame, g))


def asignar_actividad(frame, id_grupo_seleccionado=None):
    limpiar_frame(frame)
    CTkLabel(frame, text="Asignar Actividad", text_color="black", anchor="w",
             font=("Arial Rounded MT Bold", 34)).pack(fill="x", padx=10, pady=10)

    form = CTkFrame(frame, fg_color="white")
    form.pack(padx=20, pady=14, fill="x")
    e_grupo = CTkEntry(form, placeholder_text="Id grupo",
                       font=("Arial", 15), height=42)

    unidades_grupo = obtener_unidades_grupo(
        id_grupo_seleccionado) if id_grupo_seleccionado else []
    unidad_ids = None
    if unidades_grupo:
        unidad_ids = [str(id_unidad).strip()
                      for id_unidad, numero_unidad, tema_unidad in unidades_grupo]
        opciones_unidad = [f"Unidad {numero_unidad}: {tema_unidad}"
                           for id_unidad, numero_unidad, tema_unidad in unidades_grupo]
        e_unidad = CTkComboBox(form, values=opciones_unidad,
                               state="readonly", font=("Arial", 15), height=42)
        e_unidad.set(opciones_unidad[0])
    else:
        e_unidad = CTkEntry(
            form, placeholder_text="Id unidad (obligatorio)", font=("Arial", 15), height=42)

    # Tipos de actividad (combo)
    try:
        tipos_filas = ejecutar_select(
            "SELECT nombre FROM tipos_actividades ORDER BY nombre")
        tipos_nombres = [t[0] for t in tipos_filas] if tipos_filas else []
    except Exception:
        tipos_nombres = []

    if tipos_nombres:
        e_tipo = CTkComboBox(form, values=tipos_nombres,
                             state="readonly", font=("Arial", 15), height=42)
        e_tipo.set(tipos_nombres[0])
    else:
        e_tipo = CTkEntry(
            form, placeholder_text="Tipo de actividad (obligatorio)", font=("Arial", 15), height=42)

    e_desc = CTkEntry(form, placeholder_text="Detalles de la actividad", font=(
        "Arial", 15), height=130)
    e_valor = CTkEntry(
        form, placeholder_text="Ponderación % (ej. 20)", font=("Arial", 15), height=42)

    for w in (e_grupo, e_unidad, e_tipo, e_desc, e_valor):
        w.pack(fill="x", padx=10, pady=7)

    if id_grupo_seleccionado is not None:
        sql_clave = "SELECT clave_grupo FROM grupo WHERE id_grupo = %s LIMIT 1"
        resultado_clave = ejecutar_select(sql_clave, (id_grupo_seleccionado,))
        clave_grupo = resultado_clave[0][0] if resultado_clave else id_grupo_seleccionado
        e_grupo.insert(0, str(clave_grupo))
        e_grupo.configure(state="disabled")

    CTkLabel(form, text="Selecciona la unidad a la que se asignará la actividad.",
             text_color="gray", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(2, 6))
    if id_grupo_seleccionado is not None and not unidades_grupo:
        CTkLabel(form, text="No hay unidades configuradas para este grupo.",
                 text_color="#B00020", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(0, 6))

    lbl_suma_actual = CTkLabel(form, text="Suma de ponderaciones actual: 0.00%",
                               text_color="#0E7490", font=("Arial Rounded MT Bold", 13))
    lbl_suma_actual.pack(anchor="w", padx=10, pady=(3, 2))
    lbl_suma_nueva = CTkLabel(form, text="Suma con nueva actividad: 0.00%",
                              text_color="#7A4B00", font=("Arial Rounded MT Bold", 13))
    lbl_suma_nueva.pack(anchor="w", padx=10, pady=(0, 8))

    estado = CTkLabel(form, text="", text_color="gray")
    estado.pack(anchor="w", padx=10, pady=8)

    def id_grupo_actual():
        return e_grupo.get().strip() if id_grupo_seleccionado is None else str(id_grupo_seleccionado).strip()

    def id_unidad_actual():
        valor = e_unidad.get().strip()
        if not valor:
            return None
        if isinstance(e_unidad, CTkComboBox) and unidad_ids is not None:
            try:
                idx = opciones_unidad.index(valor)
                return unidad_ids[idx]
            except Exception:
                pass
        return valor.split(" - ", 1)[0].strip()

    def id_tipo_actual():
        # devuelve el nombre seleccionado o el texto del entry
        try:
            nombre = e_tipo.get().strip()
        except Exception:
            return None
        return nombre if nombre else None

    def actualizar_ponderacion_ui(*_):
        id_grupo_val = id_grupo_actual()
        id_unidad_val = id_unidad_actual()
        if not id_grupo_val or not id_unidad_val:
            lbl_suma_actual.configure(text="Suma de ponderaciones actual: -")
            lbl_suma_nueva.configure(text="Suma con nueva actividad: -")
            return

        suma_actual = obtener_suma_ponderaciones(id_grupo_val, id_unidad_val)
        valor_nuevo = a_numero(e_valor.get()) or 0.0
        suma_nueva = suma_actual + valor_nuevo

        lbl_suma_actual.configure(
            text=f"Suma de ponderaciones actual: {suma_actual:.2f}%")
        if suma_nueva > 100:
            lbl_suma_nueva.configure(
                text=f"Suma con nueva actividad: {suma_nueva:.2f}% (excede 100%)",
                text_color="#B00020")
        elif suma_nueva == 100:
            lbl_suma_nueva.configure(
                text=f"Suma con nueva actividad: {suma_nueva:.2f}% (completa)",
                text_color="#1B5E20")
        else:
            lbl_suma_nueva.configure(
                text=f"Suma con nueva actividad: {suma_nueva:.2f}% (faltan {100 - suma_nueva:.2f}%)",
                text_color="#7A4B00")

    e_valor.bind("<KeyRelease>", actualizar_ponderacion_ui)
    if isinstance(e_unidad, CTkComboBox):
        e_unidad.bind("<<ComboboxSelected>>", actualizar_ponderacion_ui)
    else:
        e_unidad.bind("<KeyRelease>", actualizar_ponderacion_ui)
    if id_grupo_seleccionado is None:
        e_grupo.bind("<KeyRelease>", actualizar_ponderacion_ui)

    def guardar():
        unidad_val = id_unidad_actual()
        grupo_val = id_grupo_actual()
        valor_nuevo = a_numero(e_valor.get())
        detalles_val = e_desc.get().strip()
        tipo_nombre = id_tipo_actual()

        if not unidad_val:
            estado.configure(
                text="Debes seleccionar una unidad válida.", text_color="#B00020")
            return
        if not tipo_nombre:
            estado.configure(
                text="Debes seleccionar un tipo de actividad.", text_color="#B00020")
            return
        if valor_nuevo is None or valor_nuevo <= 0:
            estado.configure(
                text="Debes capturar una ponderación válida mayor a 0.", text_color="#B00020")
            return

        suma_actual = obtener_suma_ponderaciones(grupo_val, unidad_val)
        suma_nueva = suma_actual + valor_nuevo
        if suma_nueva > 100:
            estado.configure(
                text=f"No se puede guardar: la suma de ponderaciones sería {suma_nueva:.2f}%.",
                text_color="#B00020")
            return

        # Resolver id_tipo desde el nombre seleccionado
        try:
            tipo_result = ejecutar_select(
                "SELECT id_tipo FROM tipos_actividades WHERE nombre = %s", (
                    tipo_nombre,)
            ) if tipo_nombre else None
            if not tipo_result:
                estado.configure(
                    text="Tipo de actividad no válido.", text_color="#B00020")
                return
            id_tipo_val = tipo_result[0][0]

            sql = """
                INSERT INTO actividad (id_unidad, id_tipo, ponderacion, detalles)
                VALUES (%s, %s, %s, %s)
            """
            ejecutar_insert(sql, (unidad_val, id_tipo_val,
                            valor_nuevo, detalles_val))
            estado.configure(
                text=f"Actividad asignada correctamente. Total de unidad: {suma_nueva:.2f}%.",
                text_color="#1B5E20")
            actualizar_ponderacion_ui()
        except Exception as ex:
            estado.configure(
                text=f"Error al asignar actividad: {ex}", text_color="#B00020")

    actualizar_ponderacion_ui()

    CTkButton(form, text="Guardar actividad", fg_color=COLOR_MAIN, hover_color=COLOR_HOVER,
              font=BUTTON_FONT, command=guardar).pack(anchor="e", padx=10, pady=(4, 10))


def iniciar_maestro(matricula):
    global ventana, frame_contenido, matricula_maestro, nombre_maestro
    matricula_maestro = matricula

    try:
        datos = obtener_datos_maestro(matricula_maestro)
        if datos:
            n, ap, am, *_ = datos
            nombre_maestro = f"{n} {ap} {am}"
        else:
            nombre_maestro = None
    except Exception:
        nombre_maestro = None

    ventana = CTk(fg_color="white")
    ventana.title("Inicio Maestros")
    ventana.withdraw()
    ventana.after(0, mostrar_maximizada)

    frame_menu = CTkFrame(ventana, width=270,
                          corner_radius=0, fg_color=COLOR_SIDE)
    frame_menu.pack(side="left", fill="y")
    frame_menu.pack_propagate(False)

    frame_contenido = CTkFrame(ventana, fg_color="white")
    frame_contenido.pack(side="left", fill="both",
                         expand=True, padx=20, pady=(40, 10))

    menu_opciones(frame_menu)
    mis_grupos(frame_contenido)
    ventana.mainloop()


if __name__ == "__main__":
    iniciar_maestro("M001")