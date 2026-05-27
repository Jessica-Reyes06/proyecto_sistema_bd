from db_conexion import *
from codigo_alumnos import funciones_Alumnos as funciones
import datetime
from PIL import Image
from customtkinter import *
import os
import sys

# Nota: archivo tocado para normalizar indentación/fin de línea (no funcional)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


global id_grupo, nc_alumno, id_materia
id_grupo = None
nc_alumno = None
id_materia = None


def ruta_recurso(ruta_relativa):
    base_path = getattr(sys, "_MEIPASS", ROOT_DIR)
    return os.path.join(base_path, ruta_relativa)


# ------------------FUNCIONES----------------
def limpiar_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def normalizar_id_grupo(valor_grupo):
    if valor_grupo is None:
        return None
    texto = str(valor_grupo).strip()
    if texto.lower().startswith("grupo "):
        return texto[6:].strip()
    return texto


def formatear_nombre_unidad(unidad):
    texto = str(unidad).strip()
    if texto.isdigit() and len(texto) > 1 and len(set(texto)) == 1:
        texto = texto[0]
    return f"Unidad {texto}"


def mostrar_placeholder_actividad(frame_detalle):
    limpiar_frame(frame_detalle)
    CTkLabel(
        frame_detalle,
        text="Selecciona una actividad para ver su informacion.",
        text_color="gray",
        anchor="w",
        justify="left",
        font=("Arial Rounded MT Bold", 14)
    ).pack(fill="x", padx=10, pady=10)


def componentes_Info_General(frame_tab):
    global id_grupo

    id_grupo_sql = normalizar_id_grupo(id_grupo)

    contenedor = CTkScrollableFrame(
        frame_tab,
        fg_color="white",
        border_width=0,
        corner_radius=0,
        scrollbar_fg_color="white",
        scrollbar_button_color="#d7d7d7",
        scrollbar_button_hover_color="#c4c4c4",
    )
    contenedor.pack(fill="both", expand=True, padx=5, pady=5)

    frame_info = CTkFrame(contenedor, fg_color="#cabece", border_width=0)
    frame_info.pack(pady=5, padx=5, fill="x")

    consulta = """
        SELECT
            G.id_grupo,
            M.id_materia,
            M.nombre_materia,
            M.horas_semana,
            M.creditos,
            M.tipo,
            G.cupo_maximo
        FROM grupo G
        JOIN materia M ON G.id_materia = M.id_materia
        WHERE G.id_grupo = %s
        LIMIT 1
    """

    resultado = ejecutar_select(
        consulta, (id_grupo_sql,)) if id_grupo_sql else []

    if resultado:
        (
            grupo,
            materia_id,
            materia_nombre,
            horas_semana,
            creditos,
            tipo_materia,
            cupo_maximo,
        ) = resultado[0]

        CTkLabel(
            frame_info,
            text=f"Grupo: {grupo}",
            text_color="black",
            justify="left",
            font=("Arial Rounded MT Bold", 20),
        ).pack(pady=(8, 2), padx=10, anchor="w")

        CTkLabel(
            frame_info,
            text=f"Materia: {materia_id} - {materia_nombre}",
            text_color="black",
            justify="left",
            font=("Arial Rounded MT Bold", 15),
        ).pack(pady=2, padx=10, anchor="w")

        CTkLabel(
            frame_info,
            text=f"Horas/semana: {horas_semana}    Creditos: {creditos}    Tipo: {tipo_materia}    Cupo: {cupo_maximo}",
            text_color="black",
            justify="left",
            font=("Arial Rounded MT Bold", 14),
        ).pack(pady=(2, 8), padx=10, anchor="w")
    else:
        CTkLabel(
            frame_info,
            text="No se encontro informacion del grupo en la base de datos.",
            text_color="black",
            justify="left",
            font=("Arial Rounded MT Bold", 14),
        ).pack(pady=8, padx=10, anchor="w")

    CTkLabel(
        contenedor,
        text="Horario del grupo",
        text_color="black",
        font=("Arial Rounded MT Bold", 18),
    ).pack(pady=(8, 4), padx=8, anchor="w")

    frame_horario = CTkFrame(
        contenedor, fg_color="white", height=240, border_width=0)
    frame_horario.pack(fill="x", expand=False, padx=5, pady=(0, 8))
    frame_horario.pack_propagate(False)
    funciones.tabla_horario_materia(frame_horario, id_grupo_sql)

    CTkLabel(
        contenedor,
        text="Participantes inscritos",
        text_color="black",
        font=("Arial Rounded MT Bold", 18),
    ).pack(pady=(8, 4), padx=8, anchor="w")

    frame_participantes = CTkFrame(
        contenedor, fg_color="white", height=280, border_width=0)
    frame_participantes.pack(fill="x", expand=False, padx=5, pady=(0, 8))
    frame_participantes.pack_propagate(False)
    funciones.crear_tabla_participantes(frame_participantes, id_grupo_sql)


def componentes_actividades(frame_tab, titulo):
    limpiar_frame(frame_tab)

    actividad = titulo if isinstance(titulo, dict) else {
        "id_actividad": None,
        "nombre": str(titulo),
        "descripcion": "Descripción de la actividad",
        "fecha_entrega": None,
        "fecha_entrega_alumno": None,
        "valor_porcentaje": None,
        "observaciones": None,
        "calificacion_unidad": None,
    }

    def normalizar_fecha(valor):
        if valor is None:
            return None
        if isinstance(valor, datetime.datetime):
            return valor.date()
        if isinstance(valor, datetime.date):
            return valor
        if isinstance(valor, str):
            texto = valor.strip()
            if not texto:
                return None
            for formato in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.datetime.strptime(texto, formato).date()
                except ValueError:
                    continue
        return None

    frame_actividad = CTkFrame(frame_tab, fg_color="#cabece")
    frame_actividad.pack(pady=5, padx=5, fill="x")
    CTkLabel(
        frame_actividad,
        text=actividad["nombre"],
        text_color="black",
        justify="left",
        font=("Arial Rounded MT Bold", 20)
    ).pack(pady=5, padx=10, anchor="w")
    CTkLabel(
        frame_actividad,
        text=actividad["descripcion"] or "Sin descripcion",
        text_color="black",
        justify="left",
        font=("Arial Rounded MT Bold", 14)
    ).pack(pady=5, padx=10, anchor="w")

    meta = []
    if actividad.get("fecha_entrega"):
        meta.append(f"Entrega: {actividad['fecha_entrega']}")
    if actividad.get("valor_porcentaje") is not None:
        meta.append(f"Valor: {actividad['valor_porcentaje']}%")

    if meta:
        CTkLabel(
            frame_actividad,
            text="    ".join(meta),
            text_color="black",
            justify="left",
            font=("Arial Rounded MT Bold", 13)
        ).pack(pady=(0, 5), padx=10, anchor="w")

    fecha_limite = normalizar_fecha(actividad.get("fecha_entrega"))
    fecha_envio = normalizar_fecha(actividad.get("fecha_entrega_alumno"))
    hoy = datetime.date.today()

    estado_entrega = "ACTIVIDAD NO ENTREGA"
    color_estado = "#B00020"
    if fecha_envio is not None:
        if fecha_limite is None or fecha_envio <= fecha_limite:
            estado_entrega = "ACTIVIDAD ENTREGADA"
            color_estado = "#1B5E20"
        else:
            estado_entrega = "ENTREGA CON RETRASO"
            color_estado = "#B26A00"
    elif fecha_limite is not None:
        dias_restantes = (fecha_limite - hoy).days
        if dias_restantes >= 0:
            estado_entrega = f"Te quedan {dias_restantes} dias para entregar"
            color_estado = "#0D47A1"

    label_estado_actividad = CTkLabel(
        frame_actividad,
        text=f"Estado: {estado_entrega}",
        text_color=color_estado,
        justify="left",
        font=("Arial Rounded MT Bold", 14)
    )
    label_estado_actividad.pack(pady=(0, 4), padx=10, anchor="w")

    texto_fecha_entrega = "Pendiente"
    if fecha_envio is not None:
        texto_fecha_entrega = str(fecha_envio)

    label_fecha_entrega = CTkLabel(
        frame_actividad,
        text=f"Fecha de entrega: {texto_fecha_entrega}",
        text_color="black",
        justify="left",
        font=("Arial Rounded MT Bold", 13)
    )
    label_fecha_entrega.pack(pady=(0, 4), padx=10, anchor="w")

    observaciones = actividad.get("observaciones")
    if not observaciones:
        observaciones = "Por el momento no hay observaciones del maestro."

    calificacion = actividad.get("calificacion_unidad")
    if calificacion in (None, ""):
        texto_calificacion = "Pendiente"
    else:
        texto_calificacion = str(calificacion)

    label_observaciones = CTkLabel(
        frame_actividad,
        text=f"Observaciones: {observaciones}",
        text_color="black",
        justify="left",
        font=("Arial Rounded MT Bold", 13),
        wraplength=1100
    )
    label_observaciones.pack(pady=(0, 4), padx=10, anchor="w")

    label_calificacion = CTkLabel(
        frame_actividad,
        text=f"Calificación: {texto_calificacion}",
        text_color="black",
        justify="left",
        font=("Arial Rounded MT Bold", 13)
    )
    label_calificacion.pack(pady=(0, 6), padx=10, anchor="w")

    label_archivo = CTkLabel(
        frame_actividad,
        text="Archivo: ninguno",
        text_color="black",
        justify="left",
        font=("Arial Rounded MT Bold", 14)
    )
    label_archivo.pack(pady=(5, 8), padx=10, anchor="w")

    frame_botones = CTkFrame(frame_actividad, fg_color="#cabece")
    frame_botones.pack(fill="x", padx=10, pady=(0, 5))

    boton_seleccionar = CTkButton(
        frame_botones,
        text="Seleccionar archivo",
        fg_color="#715a72",
        text_color="white",
        hover_color="#5e485f",
        font=("Arial Rounded MT Bold", 14),
        command=lambda: funciones.seleccionar_archivo(label_archivo)
    )
    boton_seleccionar.pack(side="left")

    boton_enviar = CTkButton(
        frame_botones,
        text="Enviar actividad",
        fg_color="#715a72",
        text_color="white",
        hover_color="#5e485f",
        font=("Arial Rounded MT Bold", 14),
        command=lambda: enviar_actividad()
    )
    boton_enviar.pack(side="right")

    label_estado_envio = CTkLabel(
        frame_actividad,
        text="",
        text_color="#444444",
        justify="left",
        font=("Arial Rounded MT Bold", 13)
    )
    label_estado_envio.pack(pady=(4, 8), padx=10, anchor="w")

    def enviar_actividad():
        global nc_alumno

        id_act = actividad.get("id_actividad")
        if not id_act:
            label_estado_envio.configure(
                text="No se pudo identificar la actividad para entregar.",
                text_color="#B00020"
            )
            return

        texto_archivo = label_archivo.cget("text")
        if not texto_archivo or texto_archivo.strip().lower() == "archivo: ninguno":
            label_estado_envio.configure(
                text="Selecciona un archivo antes de enviar la actividad.",
                text_color="#B26A00"
            )
            return

        ruta_archivo = texto_archivo.replace("Archivo: ", "", 1).strip()
        ok, mensaje = funciones.entregar_actividad(
            nc_alumno, id_act, ruta_archivo)
        label_estado_envio.configure(
            text=mensaje,
            text_color="#1B5E20" if ok else "#B00020"
        )

        if ok:
            fecha_reporte = datetime.date.today()
            if fecha_limite is None or fecha_reporte <= fecha_limite:
                label_estado_actividad.configure(
                    text="Estado: ACTIVIDAD ENTREGADA", text_color="#1B5E20")
            else:
                label_estado_actividad.configure(
                    text="Estado: ENTREGA CON RETRASO", text_color="#B26A00")

            label_fecha_entrega.configure(
                text=f"Fecha de entrega: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            label_observaciones.configure(text="Observaciones: Pendientes")
            label_calificacion.configure(text="Calificación: Pendiente")
            label_archivo.configure(text="Archivo: entregada")
            boton_seleccionar.configure(state="disabled")
            boton_enviar.configure(state="disabled")


def boton_unidad_grupo(frame_tab, frame_detalle, titulo_unidad, actividades):
    frame_grupo = CTkFrame(frame_tab, fg_color="white")
    frame_grupo.pack(pady=0, padx=5, fill="x")

    img_unidad = CTkImage(
        Image.open(ruta_recurso(
            "carpeta_iconos/iconos_alumnos/resaltador.png")),
        size=(30, 30)
    )

    frame_opciones = CTkFrame(frame_grupo, fg_color="white")
    desplegado = {"activo": False}

    def toggle_menu():
        if desplegado["activo"]:
            frame_opciones.pack_forget()
            desplegado["activo"] = False
        else:
            frame_opciones.pack(fill="x", padx=0, pady=0, anchor="w")
            desplegado["activo"] = True

    boton_unidad = CTkButton(
        frame_grupo,
        text=f"     {titulo_unidad}",
        image=img_unidad,
        compound="left",
        anchor="w",
        width=1190,
        fg_color="#5e485f",
        hover_color="#4c304e",
        text_color="white",
        font=("Arial Rounded MT Bold", 25),
        command=toggle_menu
    )
    boton_unidad.pack(pady=0, padx=0, fill="x", anchor="w")

    if not actividades:
        CTkLabel(
            frame_opciones,
            text="No hay actividades en esta unidad.",
            text_color="gray",
            anchor="w",
            justify="left",
            font=("Arial Rounded MT Bold", 13)
        ).pack(fill="x", padx=10, pady=8)
    else:
        for actividad in actividades:
            texto_actividad = actividad["nombre"] if isinstance(
                actividad, dict) else str(actividad)
            CTkButton(
                frame_opciones,
                text=texto_actividad,
                anchor="w",
                width=1190,
                fg_color="#715a72",
                hover_color="#5e485f",
                text_color="white",
                corner_radius=0,
                font=("Arial Rounded MT Bold", 14),
                command=lambda item=actividad: componentes_actividades(
                    frame_detalle, item)
            ).pack(fill="x", padx=0, pady=0)


def obtener_id_registro_alumno(numero_control, id_grupo_valor):
    consulta = """
        SELECT R.id_registro
        FROM registro R
        JOIN alumno A ON R.id_alumno = A.id_alumno
        WHERE TRIM(A.numero_control) = TRIM(%s)
          AND TRIM(R.id_grupo) = TRIM(%s)
        LIMIT 1
    """

    try:
        filas = ejecutar_select(consulta, (numero_control, id_grupo_valor))
    except Exception:
        return None

    return filas[0][0] if filas else None


def obtener_columnas_tabla(nombre_tabla):
    try:
        filas = ejecutar_select(f"SHOW COLUMNS FROM {nombre_tabla}")
    except Exception:
        return set()
    return {fila[0].lower() for fila in filas or []}


def obtener_actividades_por_unidad(id_grupo_valor, numero_control):
    id_registro = obtener_id_registro_alumno(numero_control, id_grupo_valor)

    if id_registro is None:
        return {}

    try:
        fila_materia = ejecutar_select(
            """
            SELECT id_materia
            FROM grupo
            WHERE TRIM(id_grupo) = TRIM(%s)
            LIMIT 1
            """,
            (id_grupo_valor,),
        )
    except Exception:
        fila_materia = []

    if not fila_materia:
        return {}

    id_materia_grupo = fila_materia[0][0]

    tabla_unidad = None
    columnas_unidad = set()
    for candidata in ("Unidad", "unidad"):
        cols = obtener_columnas_tabla(candidata)
        if cols:
            tabla_unidad = candidata
            columnas_unidad = cols
            break

    enlace_materia_unidad_disponible = bool(
        tabla_unidad
        and "id_unidad" in columnas_unidad
        and "id_materia" in columnas_unidad
    )

    col_unidad = "numero_unidad" if "numero_unidad" in columnas_unidad else "id_unidad"

    columnas_resultado = obtener_columnas_tabla("resultado")
    tiene_resultado = bool(columnas_resultado)

    col_obs = "RES.observaciones" if "observaciones" in columnas_resultado else "NULL"
    if "calificacion_actividad" in columnas_resultado:
        col_cal = "RES.calificacion_actividad"
    elif "calificacion_unidad" in columnas_resultado:
        col_cal = "RES.calificacion_unidad"
    elif "calificacion" in columnas_resultado:
        col_cal = "RES.calificacion"
    else:
        col_cal = "NULL"

    filas = None
    actividades_por_unidad = {}

    if enlace_materia_unidad_disponible:
        try:
            filas_unidades = ejecutar_select(
                f"""
                SELECT
                    TRIM(id_unidad) AS id_unidad,
                    COALESCE(NULLIF(TRIM({col_unidad}), ''), TRIM(id_unidad)) AS unidad_mostrar
                FROM {tabla_unidad}
                WHERE TRIM(id_materia) = TRIM(%s)
                ORDER BY unidad_mostrar
                """,
                (id_materia_grupo,),
            )
        except Exception:
            filas_unidades = []

        for _id_unidad, unidad_mostrar in filas_unidades or []:
            clave_unidad = str(unidad_mostrar).strip(
            ) if unidad_mostrar not in (None, "") else "Sin unidad"
            if clave_unidad not in actividades_por_unidad:
                actividades_por_unidad[clave_unidad] = []

        consulta_base = f"""
            SELECT
                A.id_actividad,
                COALESCE(NULLIF(TRIM(U.{col_unidad}), ''), TRIM(U.id_unidad), 'Sin unidad') AS unidad,
                COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre') AS nombre_actividad,
                COALESCE(NULLIF(TRIM(A.descripcion), ''), 'Sin descripcion') AS descripcion,
                A.fecha_entrega,
                A.valor_porcentaje,
                NULL AS fecha_entrega_alumno,
                NULL AS observaciones,
                NULL AS calificacion_unidad
            FROM {{tabla_actividad}} A
            JOIN {tabla_unidad} U
                ON TRIM(A.id_unidad) = TRIM(U.id_unidad)
            WHERE TRIM(A.id_grupo) = TRIM(%s)
              AND TRIM(U.id_materia) = TRIM(%s)
            ORDER BY unidad, A.fecha_entrega, nombre_actividad
        """

        consulta_con_resultado = f"""
            SELECT
                A.id_actividad,
                COALESCE(NULLIF(TRIM(U.{col_unidad}), ''), TRIM(U.id_unidad), 'Sin unidad') AS unidad,
                COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre') AS nombre_actividad,
                COALESCE(NULLIF(TRIM(A.descripcion), ''), 'Sin descripcion') AS descripcion,
                A.fecha_entrega,
                A.valor_porcentaje,
                MAX(RES.fecha_registro) AS fecha_entrega_alumno,
                MAX({col_obs}) AS observaciones,
                MAX({col_cal}) AS calificacion_unidad
            FROM {{tabla_actividad}} A
            JOIN {tabla_unidad} U
                ON TRIM(A.id_unidad) = TRIM(U.id_unidad)
            LEFT JOIN resultado RES
                ON RES.id_registro = %s
                AND RES.id_actividad = A.id_actividad
            WHERE TRIM(A.id_grupo) = TRIM(%s)
              AND TRIM(U.id_materia) = TRIM(%s)
            GROUP BY
                A.id_actividad,
                COALESCE(NULLIF(TRIM(U.{col_unidad}), ''), TRIM(U.id_unidad), 'Sin unidad'),
                COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre'),
                COALESCE(NULLIF(TRIM(A.descripcion), ''), 'Sin descripcion'),
                A.fecha_entrega,
                A.valor_porcentaje
            ORDER BY unidad, A.fecha_entrega, nombre_actividad
        """

        for tabla_actividad in ("Actividad", "actividad"):
            if tiene_resultado:
                try:
                    filas = ejecutar_select(
                        consulta_con_resultado.format(
                            tabla_actividad=tabla_actividad),
                        (id_registro, id_grupo_valor, id_materia_grupo),
                    )
                    break
                except Exception:
                    pass
            try:
                filas = ejecutar_select(
                    consulta_base.format(tabla_actividad=tabla_actividad),
                    (id_grupo_valor, id_materia_grupo),
                )
                break
            except Exception:
                pass

    # Fallback: si no existe/encaja el enlace Unidad-Materia, mostrar actividades por grupo.
    if filas is None:
        consulta_base_fallback = """
            SELECT
                A.id_actividad,
                COALESCE(NULLIF(TRIM(A.id_unidad), ''), 'Sin unidad') AS unidad,
                COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre') AS nombre_actividad,
                COALESCE(NULLIF(TRIM(A.descripcion), ''), 'Sin descripcion') AS descripcion,
                A.fecha_entrega,
                A.valor_porcentaje,
                NULL AS fecha_entrega_alumno,
                NULL AS observaciones,
                NULL AS calificacion_unidad
            FROM {tabla_actividad} A
            WHERE TRIM(A.id_grupo) = TRIM(%s)
            ORDER BY unidad, A.fecha_entrega, nombre_actividad
        """

        consulta_resultado_fallback = f"""
            SELECT
                A.id_actividad,
                COALESCE(NULLIF(TRIM(A.id_unidad), ''), 'Sin unidad') AS unidad,
                COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre') AS nombre_actividad,
                COALESCE(NULLIF(TRIM(A.descripcion), ''), 'Sin descripcion') AS descripcion,
                A.fecha_entrega,
                A.valor_porcentaje,
                MAX(RES.fecha_registro) AS fecha_entrega_alumno,
                MAX({col_obs}) AS observaciones,
                MAX({col_cal}) AS calificacion_unidad
            FROM {{tabla_actividad}} A
            LEFT JOIN resultado RES
                ON RES.id_registro = %s
                AND RES.id_actividad = A.id_actividad
            WHERE TRIM(A.id_grupo) = TRIM(%s)
            GROUP BY
                A.id_actividad,
                COALESCE(NULLIF(TRIM(A.id_unidad), ''), 'Sin unidad'),
                COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre'),
                COALESCE(NULLIF(TRIM(A.descripcion), ''), 'Sin descripcion'),
                A.fecha_entrega,
                A.valor_porcentaje
            ORDER BY unidad, A.fecha_entrega, nombre_actividad
        """

        filas = None
        for tabla_actividad in ("Actividad", "actividad"):
            if tiene_resultado:
                try:
                    filas = ejecutar_select(
                        consulta_resultado_fallback.format(
                            tabla_actividad=tabla_actividad),
                        (id_registro, id_grupo_valor),
                    )
                    break
                except Exception:
                    pass
            try:
                filas = ejecutar_select(
                    consulta_base_fallback.format(
                        tabla_actividad=tabla_actividad),
                    (id_grupo_valor,),
                )
                break
            except Exception:
                pass

    if filas is None:
        return {}

    for id_actividad, unidad, nombre, descripcion, fecha_entrega, valor_porcentaje, fecha_entrega_alumno, observaciones, calificacion_unidad in filas or []:
        actividades_por_unidad.setdefault(unidad, []).append(
            {
                "id_actividad": id_actividad,
                "nombre": nombre,
                "descripcion": descripcion,
                "fecha_entrega": fecha_entrega,
                "valor_porcentaje": valor_porcentaje,
                "fecha_entrega_alumno": fecha_entrega_alumno,
                "observaciones": observaciones,
                "calificacion_unidad": calificacion_unidad,
            }
        )

    return actividades_por_unidad


def Informacion_General(tab):
    limpiar_frame(tab)
    CTkLabel(
        tab,
        text="Informacion general del grupo",
        font=("Arial Rounded MT Bold", 20),
        text_color="black"
    ).pack(pady=10)

    componentes_Info_General(tab)


def Actividades(tab):
    global id_grupo
    global nc_alumno
    limpiar_frame(tab)

    frame_scroll_actividades = CTkScrollableFrame(
        tab,
        fg_color="white",
        scrollbar_fg_color="white",
        scrollbar_button_color="#d9d9d9",
        scrollbar_button_hover_color="#c8c8c8"
    )
    frame_scroll_actividades.pack(fill="both", expand=True, padx=5, pady=5)

    CTkLabel(
        frame_scroll_actividades,
        text="Actividades del grupo",
        font=("Arial Rounded MT Bold", 20),
        text_color="black"
    ).pack(pady=10)

    frame_menu_unidades = CTkFrame(frame_scroll_actividades, fg_color="white")
    frame_menu_unidades.pack(fill="x", padx=5, pady=0)

    frame_detalle = CTkFrame(frame_scroll_actividades, fg_color="white")
    frame_detalle.pack(fill="x", padx=5, pady=(5, 0))

    id_grupo_sql = normalizar_id_grupo(id_grupo)
    data_unidades = obtener_actividades_por_unidad(
        id_grupo_sql, nc_alumno) if id_grupo_sql and nc_alumno else {}

    if not data_unidades:
        CTkLabel(
            frame_menu_unidades,
            text="No hay actividades registradas para este grupo.",
            text_color="gray",
            anchor="w",
            justify="left",
            font=("Arial Rounded MT Bold", 14)
        ).pack(fill="x", padx=10, pady=10)
        mostrar_placeholder_actividad(frame_detalle)
        return

    mostrar_placeholder_actividad(frame_detalle)

    for unidad, actividades in data_unidades.items():
        nombre_unidad = formatear_nombre_unidad(unidad)
        boton_unidad_grupo(frame_menu_unidades, frame_detalle,
                           nombre_unidad, actividades)


def _a_numero(valor):
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


def _obtener_info_unidades(id_materia_valor, id_registro_valor):
    info = {}
    columnas_unidad = obtener_columnas_tabla("Unidad")
    if not columnas_unidad:
        return info

    col_tema = "tema_unidad" if "tema_unidad" in columnas_unidad else None
    col_numero = "numero_unidad" if "numero_unidad" in columnas_unidad else None

    campos = ["id_unidad"]
    if col_numero:
        campos.append(col_numero)
    if col_tema:
        campos.append(col_tema)

    where_sql = ""
    params = ()
    if "id_materia" in columnas_unidad and id_materia_valor:
        where_sql = " WHERE id_materia = %s"
        params = (id_materia_valor,)

    consulta_unidad = f"SELECT {', '.join(campos)} FROM Unidad{where_sql}"
    try:
        filas = ejecutar_select(
            consulta_unidad, params) if params else ejecutar_select(consulta_unidad)
    except Exception:
        filas = []

    for fila in filas or []:
        idx = 0
        id_unidad_fila = str(fila[idx]).strip()
        idx += 1
        numero_unidad = str(fila[idx]).strip(
        ) if col_numero else id_unidad_fila
        if col_numero:
            idx += 1
        tema_unidad = str(fila[idx]).strip() if col_tema and fila[idx] not in (
            None, "") else "Sin tema"
        info[id_unidad_fila] = {"numero": numero_unidad,
                                "tema": tema_unidad, "bonus_unidad": 0.0}

    columnas_bonus = obtener_columnas_tabla("BonusUnidad")
    if columnas_bonus and id_registro_valor is not None:
        col_valor = "valor" if "valor" in columnas_bonus else None
        if col_valor and "id_unidad" in columnas_bonus and "id_registro" in columnas_bonus:
            try:
                bonus_rows = ejecutar_select(
                    "SELECT id_unidad, valor FROM BonusUnidad WHERE id_registro = %s",
                    (id_registro_valor,),
                )
            except Exception:
                bonus_rows = []

            for id_unidad_bonus, bonus_val in bonus_rows or []:
                clave = str(id_unidad_bonus).strip()
                if clave not in info:
                    info[clave] = {"numero": clave,
                                   "tema": "Sin tema", "bonus_unidad": 0.0}
                bonus_num = _a_numero(bonus_val) or 0.0
                info[clave]["bonus_unidad"] = bonus_num

    return info


def _obtener_bonus_final(id_materia_valor, id_registro_valor):
    columnas_bonus = obtener_columnas_tabla("BonusMateria")
    if not columnas_bonus or id_registro_valor is None:
        return 0.0
    if "valor" not in columnas_bonus or "id_registro" not in columnas_bonus:
        return 0.0

    consulta = "SELECT MAX(valor) FROM BonusMateria WHERE id_registro = %s"
    params = [id_registro_valor]
    if "id_materia" in columnas_bonus and id_materia_valor:
        consulta += " AND id_materia = %s"
        params.append(id_materia_valor)

    try:
        fila = ejecutar_select(consulta, tuple(params))
    except Exception:
        return 0.0

    if not fila or not fila[0]:
        return 0.0
    return _a_numero(fila[0][0]) or 0.0


def componentes_calificaciones(frame_tab, titulo, porcentaje, calificacion):
    frame_item = CTkFrame(frame_tab, fg_color="#cabece")
    frame_item.pack(fill="x", padx=0, pady=0)

    CTkLabel(
        frame_item,
        text=titulo,
        anchor="w",
        justify="left",
        text_color="black",
        font=("Arial Rounded MT Bold", 14)
    ).pack(side="left", padx=10, pady=6)

    texto_porcentaje = f"{porcentaje:.2f}%" if isinstance(
        porcentaje, (int, float)) else str(porcentaje)
    CTkLabel(
        frame_item,
        text=texto_porcentaje,
        anchor="e",
        justify="right",
        text_color="#4a4a4a",
        font=("Arial Rounded MT Bold", 13)
    ).pack(side="right", padx=(4, 10), pady=6)

    CTkLabel(
        frame_item,
        text=calificacion,
        anchor="e",
        justify="right",
        text_color="black",
        font=("Arial Rounded MT Bold", 14)
    ).pack(side="right", padx=(4, 10), pady=6)


def bloque_calificaciones_unidad(frame_tab, titulo_unidad, tema_unidad, items, bonus_unidad=0.0):
    frame_bloque = CTkFrame(frame_tab, fg_color="white")
    frame_bloque.pack(fill="x", padx=5, pady=0)

    CTkLabel(
        frame_bloque,
        text=f"     {titulo_unidad} - Tema: {tema_unidad}",
        anchor="w",
        justify="left",
        text_color="white",
        fg_color="#715a72",
        font=("Arial Rounded MT Bold", 22)
    ).pack(fill="x", padx=0, pady=0)

    frame_lista = CTkFrame(frame_bloque, fg_color="white")
    frame_lista.pack(fill="x", padx=0, pady=0)

    if not items:
        CTkLabel(
            frame_lista,
            text="SIN ACTIVIDADES ASIGANDAS EN LA UNIDAD",
            anchor="w",
            justify="left",
            text_color="gray",
            font=("Arial Rounded MT Bold", 13)
        ).pack(fill="x", padx=10, pady=8)

    ponderada = 0.0
    for titulo, porcentaje, calificacion_actividad in items:
        cal_num = funciones.a_numero(calificacion_actividad)
        por_num = funciones.a_numero(porcentaje) or 0.0
        if cal_num is not None:
            ponderada += cal_num * (por_num / 100.0)

        texto_cal = str(calificacion_actividad) if calificacion_actividad not in (
            None, "") else "Por calificar"
        componentes_calificaciones(frame_lista, titulo, por_num, texto_cal)

    base_unidad = round(ponderada, 2)
    aplica_bonus_unidad = base_unidad < 100
    bonus_aplicado = (bonus_unidad or 0.0) if aplica_bonus_unidad else 0.0
    final_unidad = min(100.0, base_unidad + bonus_aplicado)

    resumen = CTkFrame(frame_bloque, fg_color="#f4f4f4")
    resumen.pack(fill="x", padx=0, pady=(4, 8))

    CTkLabel(
        resumen,
        text=f"Ponderada: {base_unidad:.2f}",
        anchor="w",
        text_color="black",
        font=("Arial Rounded MT Bold", 13)
    ).pack(side="left", padx=10, pady=6)

    CTkLabel(
        resumen,
        text=f"Bonus unidad: {bonus_aplicado:.2f}",
        anchor="w",
        text_color="black",
        font=("Arial Rounded MT Bold", 13)
    ).pack(side="left", padx=10, pady=6)

    CTkLabel(
        resumen,
        text=f"Final unidad: {final_unidad:.2f}",
        anchor="e",
        text_color="#5e485f",
        font=("Arial Rounded MT Bold", 13)
    ).pack(side="right", padx=10, pady=6)

    return final_unidad


def Calificaciones(tab):
    global id_grupo
    global nc_alumno
    global id_materia

    limpiar_frame(tab)
    CTkLabel(
        tab,
        text="Calificaciones",
        font=("Arial Rounded MT Bold", 20),
        text_color="black"
    ).pack(pady=10)

    frame_calificaciones = CTkScrollableFrame(
        tab, fg_color="white", border_width=0)
    frame_calificaciones.pack(fill="both", expand=True, padx=5, pady=0)

    id_grupo_sql = normalizar_id_grupo(id_grupo)
    data_unidades = obtener_actividades_por_unidad(
        id_grupo_sql, nc_alumno) if id_grupo_sql and nc_alumno else {}
    if not data_unidades:
        CTkLabel(
            frame_calificaciones,
            text="No hay calificaciones registradas para este grupo.",
            text_color="gray",
            anchor="w",
            justify="left",
            font=("Arial Rounded MT Bold", 14)
        ).pack(fill="x", padx=10, pady=10)
        return

    id_registro = obtener_id_registro_alumno(nc_alumno, id_grupo_sql)
    info_unidades = funciones.obtener_info_unidades(id_materia, id_registro)
    bonus_final = funciones.obtener_bonus_final(id_materia, id_registro)

    finales_unidad = []
    for unidad, actividades in data_unidades.items():
        clave_unidad = str(unidad).strip()
        info_u = info_unidades.get(clave_unidad, {})
        numero_unidad = info_u.get("numero", clave_unidad)
        tema_unidad = info_u.get("tema", "Sin tema")
        bonus_unidad = funciones.a_numero(info_u.get("bonus_unidad")) or 0.0

        items = []
        for actividad in actividades:
            nombre = actividad.get("nombre") or "Actividad sin nombre"
            porcentaje = funciones.a_numero(
                actividad.get("valor_porcentaje")) or 0.0
            calificacion = actividad.get("calificacion_unidad")
            items.append((nombre, porcentaje, calificacion))

        final_u = bloque_calificaciones_unidad(
            frame_calificaciones,
            formatear_nombre_unidad(numero_unidad),
            tema_unidad,
            items,
            bonus_unidad=bonus_unidad,
        )
        finales_unidad.append(final_u)

    promedio_base = (sum(finales_unidad) / len(finales_unidad)
                     ) if finales_unidad else 0.0
    promedio_base = round(promedio_base, 2)

    aplica_bonus_final = promedio_base < 100
    bonus_final_aplicado = bonus_final if aplica_bonus_final else 0.0
    calificacion_final = min(100.0, promedio_base + bonus_final_aplicado)

    frame_final = CTkFrame(frame_calificaciones, fg_color="#efe8f0")
    frame_final.pack(fill="x", padx=5, pady=(8, 12))

    CTkLabel(
        frame_final,
        text=f"Promedio final (sin bonus): {promedio_base:.2f}",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 14)
    ).pack(fill="x", padx=10, pady=(8, 2))

    CTkLabel(
        frame_final,
        text=f"Bonus final aplicado: {bonus_final_aplicado:.2f}",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 14)
    ).pack(fill="x", padx=10, pady=2)

    CTkLabel(
        frame_final,
        text=f"Calificación final: {calificacion_final:.2f}",
        text_color="#5e485f",
        anchor="w",
        font=("Arial Rounded MT Bold", 16)
    ).pack(fill="x", padx=10, pady=(2, 8))

# Formula para calificacion final por ponderacion: sumatoria de (calificacion_actividad * valor_porcentaje)
# Bonus de unidad: formula de calificacion final por ponderacion + bonus_unidad (si existe) y no exceda el 100
# Calificacion Final: Sumatoria de resultado de unidades/numero de unidades
# Bonus de calificacion final: formula de calificacion final + bonus_calificacion_final (si existe) y no exceda el 100


def opciones_menu(tabview):
    opcion_activa = tabview.get()

    if opcion_activa == "Informacion general" or opcion_activa == "Información general":
        Informacion_General(tabview.tab("Informacion general"))
    elif opcion_activa == "Actividades":
        Actividades(tabview.tab("Actividades"))
    elif opcion_activa == "Calificaciones":
        Calificaciones(tabview.tab("Calificaciones"))


def Info_Grupo(frame_contenido, materia, profesor, id_grupo, nc_alumno):
    global id_materia
    globals()["id_grupo"] = normalizar_id_grupo(id_grupo)
    globals()["nc_alumno"] = nc_alumno

    limpiar_frame(frame_contenido)
    id_materia = funciones.obtener_id_materia(materia)

    frame_info_general = CTkFrame(frame_contenido, fg_color="#cabece")
    frame_info_general.pack(fill="x", padx=5, pady=(5, 2))

    CTkLabel(frame_info_general, text=materia,
             font=("Arial Rounded MT Bold", 30),
             text_color="black").pack(fill="x", padx=10)

    CTkLabel(frame_info_general, text=profesor,
             font=("Arial Rounded MT Bold", 20),
             text_color="black").pack(fill="x", padx=10)

    CTkLabel(frame_info_general, text=id_grupo,
             font=("Arial Rounded MT Bold", 20),
             text_color="black").pack(fill="x", padx=10)
    opciones_grupo = CTkTabview(
        frame_contenido,
        width=1200,
        height=700,
        fg_color="white",
        command=lambda: opciones_menu(opciones_grupo)
    )
    opciones_grupo.pack(pady=0, padx=0)
    opciones_grupo.add("Informacion general")
    opciones_grupo.add("Actividades")
    opciones_grupo.add("Calificaciones")

    opciones_grupo._segmented_button.configure(
        width=150,
        font=("Arial Rounded MT Bold", 16),
        fg_color="#715a72",
        selected_color="#5e485f",
        selected_hover_color="#5e485f",
        unselected_hover_color="#715a72",
    )
    opciones_menu(opciones_grupo)
