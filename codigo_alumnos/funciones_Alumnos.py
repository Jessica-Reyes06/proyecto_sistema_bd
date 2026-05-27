import datetime
from tkinter import filedialog
import importlib
from db_conexion import ejecutar_select, ejecutar_insert
from customtkinter import CTkFrame, CTkLabel, CTkScrollableFrame
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def obtener_id_materia(nombre_materia):
    """Obtiene el id_materia a partir del nombre de la materia."""
    consulta = """
        SELECT id_materia
        FROM materia
        WHERE nombre_materia = %s
        LIMIT 1
    """
    resultado = ejecutar_select(consulta, (nombre_materia,))
    return resultado[0][0] if resultado else None


def crear_tabla_participantes(parent, id_grupo):
    """Crea una tabla visual con los alumnos inscritos en un grupo."""
    consulta = """
        SELECT
            A.nombre_alumno,
            A.apellido_paterno,
            A.apellido_materno
        FROM registro R
        JOIN alumno A ON R.id_alumno = A.id_alumno
        WHERE R.id_grupo = %s
        ORDER BY A.apellido_paterno, A.apellido_materno, A.nombre_alumno
    """

    alumnos = ejecutar_select(consulta, (id_grupo,))

    tabla = CTkFrame(parent)
    tabla.pack(fill="both", expand=True)

    encabezados = ["Nombre", "A. Paterno", "A. Materno"]

    header = CTkFrame(tabla, fg_color="#715a72")
    header.pack(fill="x")

    for i, texto in enumerate(encabezados):
        header.grid_columnconfigure(i, weight=1)
        CTkLabel(
            header,
            text=texto,
            text_color="white",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).grid(row=0, column=i, padx=10, pady=10, sticky="w")

    cuerpo = CTkScrollableFrame(
        tabla,
        fg_color="#f4eef6",
        scrollbar_fg_color="#f4eef6",
        scrollbar_button_color="#715a72",
        scrollbar_button_hover_color="#5e485f"
    )
    cuerpo.pack(fill="both", expand=True)

    if not alumnos:
        CTkLabel(
            cuerpo,
            text=f"No hay alumnos inscritos en el grupo {id_grupo}.",
            text_color="#444444",
            font=("Arial", 13)
        ).pack(pady=20)
        return tabla

    for fila_idx, fila in enumerate(alumnos):
        for col_idx, valor in enumerate(fila):
            cuerpo.grid_columnconfigure(col_idx, weight=1)
            CTkLabel(
                cuerpo,
                text=str(valor),
                text_color="#111111",
                font=("Arial", 13),
                anchor="w",
                justify="left"
            ).grid(row=fila_idx, column=col_idx, padx=10, pady=6, sticky="ew")

    return tabla


def tabla_horario_materia(parent, id_grupo):
    def _crear_filas_desde_texto(texto_horario):
        texto = str(texto_horario).strip()
        if not texto:
            return []

        horario_mostrar = texto
        hora_inicio = texto
        hora_fin = ""
        salon = ""

        # Formatos soportados: "8:00-10:00", "8:00 - 10:00", "Lun 8:00-10:00 A-203".
        if "-" in texto:
            partes = [parte.strip() for parte in texto.split("-", 1)]
            if partes[0]:
                hora_inicio = partes[0]
            if len(partes) > 1 and partes[1]:
                resto = partes[1].strip()
                if " " in resto:
                    posible_hora_fin, posible_salon = resto.split(" ", 1)
                    hora_fin = posible_hora_fin.strip()
                    salon = posible_salon.strip()
                else:
                    hora_fin = resto
        elif " " in texto:
            partes = texto.split()
            if len(partes) >= 2:
                hora_inicio = partes[0]
                hora_fin = partes[1]
                if len(partes) > 2:
                    salon = " ".join(partes[2:])

        return [("N/A", hora_inicio, hora_fin, salon or horario_mostrar)]

    filas_horario = []
    error_consulta = None

    try:
        grupo_h = ejecutar_select(
            "SELECT horario FROM grupo WHERE id_grupo = %s", (id_grupo,))
        if grupo_h and grupo_h[0] and grupo_h[0][0]:
            filas_horario = _crear_filas_desde_texto(grupo_h[0][0])
    except Exception as error:
        error_consulta = str(error)

    tabla = CTkFrame(parent)
    tabla.pack(fill="both", expand=True)

    encabezados = ["Dia", "Hora inicio", "Hora fin", "Salon"]

    header = CTkFrame(tabla, fg_color="#715a72")
    header.pack(fill="x")

    for i, texto in enumerate(encabezados):
        header.grid_columnconfigure(i, weight=1)
        CTkLabel(
            header,
            text=texto,
            text_color="white",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).grid(row=0, column=i, padx=10, pady=10, sticky="w")

    cuerpo = CTkScrollableFrame(
        tabla,
        fg_color="#f4eef6",
        scrollbar_fg_color="#f4eef6",
        scrollbar_button_color="#715a72",
        scrollbar_button_hover_color="#5e485f"
    )
    cuerpo.pack(fill="both", expand=True)

    if error_consulta is not None:
        CTkLabel(
            cuerpo,
            text="No se pudo leer el horario del grupo.",
            text_color="#b00020",
            font=("Arial", 13)
        ).pack(pady=(20, 6))
        CTkLabel(
            cuerpo,
            text=str(error_consulta),
            text_color="#444444",
            font=("Arial", 11),
            wraplength=700,
            justify="left"
        ).pack(pady=(0, 20), padx=10)
        return tabla

    if not filas_horario:
        CTkLabel(
            cuerpo,
            text=f"No hay horario registrado para el grupo {id_grupo}.",
            text_color="#444444",
            font=("Arial", 13)
        ).pack(pady=20)
        return tabla

    for fila_idx, fila in enumerate(filas_horario):
        for col_idx, valor in enumerate(fila):
            cuerpo.grid_columnconfigure(col_idx, weight=1)
            CTkLabel(
                cuerpo,
                text=str(valor),
                text_color="#111111",
                font=("Arial", 13),
                anchor="w",
                justify="left"
            ).grid(row=fila_idx, column=col_idx, padx=10, pady=6, sticky="ew")

    return tabla

# funcion para seleccionar archivo y mostrar su nombre en una etiqueta


def seleccionar_archivo(label_archivo):
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=[("Todos los archivos", "*.*"),
                   ("PDF", "*.pdf"), ("Word", "*.docx")]
    )
    if ruta:
        label_archivo.configure(text=f"Archivo: {os.path.basename(ruta)}")


def entregar_actividad(numero_control, id_actividad, ruta_archivo):
    if not numero_control or not id_actividad:
        return False, "Faltan datos para registrar la entrega."

    if not ruta_archivo:
        return False, "Selecciona un archivo antes de entregar."

    # Buscar el grupo de la actividad para ubicar el id_registro del alumno.
    fila_actividad = None
    for tabla_actividad in ("Actividad", "actividad"):
        try:
            filas = ejecutar_select(
                f"SELECT id_grupo, fecha_entrega FROM {tabla_actividad} WHERE id_actividad = %s LIMIT 1",
                (id_actividad,),
            )
        except Exception:
            continue
        if filas:
            fila_actividad = filas[0]
            break

    if not fila_actividad:
        return False, "No se encontro la actividad en la base de datos."

    id_grupo_actividad = str(fila_actividad[0]).strip()

    try:
        fila_registro = ejecutar_select(
            """
            SELECT R.id_registro
            FROM registro R
            JOIN alumno A ON R.id_alumno = A.id_alumno
            WHERE TRIM(A.numero_control) = TRIM(%s) AND TRIM(R.id_grupo) = TRIM(%s)
            LIMIT 1
            """,
            (numero_control, id_grupo_actividad),
        )
    except Exception:
        fila_registro = []

    if not fila_registro:
        return False, "No se encontro el registro del alumno en el grupo de la actividad."

    id_registro = fila_registro[0][0]

    # Guardar especificamente en la tabla resultado.
    tabla_resultado = "resultado"
    columnas_resultado = obtener_columnas_tabla(tabla_resultado)
    if not columnas_resultado:
        return False, "No se encontro la tabla resultado."

    if "id_registro" not in columnas_resultado or "id_actividad" not in columnas_resultado:
        return False, "La tabla resultado no tiene las columnas requeridas para guardar la entrega."

    if "fecha_registro" not in columnas_resultado:
        return False, "La tabla resultado no tiene fecha_registro para guardar la entrega."

    col_calificacion = None
    for candidata in ("calificacion_actividad", "calificacion_unidad", "calificacion"):
        if candidata in columnas_resultado:
            col_calificacion = candidata
            break

    fecha_entrega = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        existe = ejecutar_select(
            f"SELECT 1 FROM {tabla_resultado} WHERE id_registro = %s AND id_actividad = %s LIMIT 1",
            (id_registro, id_actividad),
        )
    except Exception as error:
        return False, f"No se pudo validar la entrega actual: {error}"

    try:
        if existe:
            if col_calificacion:
                sql_update = (
                    f"UPDATE {tabla_resultado} SET fecha_registro = %s, {col_calificacion} = %s "
                    "WHERE id_registro = %s AND id_actividad = %s"
                )
                ejecutar_insert(sql_update, (fecha_entrega,
                                0, id_registro, id_actividad))
            else:
                sql_update = (
                    f"UPDATE {tabla_resultado} SET fecha_registro = %s "
                    "WHERE id_registro = %s AND id_actividad = %s"
                )
                ejecutar_insert(sql_update, (fecha_entrega,
                                id_registro, id_actividad))
        else:
            if col_calificacion:
                sql_insert = (
                    f"INSERT INTO {tabla_resultado} (id_registro, id_actividad, fecha_registro, {col_calificacion}) "
                    "VALUES (%s, %s, %s, %s)"
                )
                ejecutar_insert(
                    sql_insert, (id_registro, id_actividad, fecha_entrega, 0))
            else:
                sql_insert = (
                    f"INSERT INTO {tabla_resultado} (id_registro, id_actividad, fecha_registro) "
                    "VALUES (%s, %s, %s)"
                )
                ejecutar_insert(
                    sql_insert, (id_registro, id_actividad, fecha_entrega))
    except Exception as error:
        return False, f"No se pudo guardar la entrega: {error}"

    return True, f"Entrega registrada: {fecha_entrega}."


def obtener_columnas_tabla(nombre_tabla):
    try:
        filas = ejecutar_select(f"SHOW COLUMNS FROM {nombre_tabla}")
    except Exception:
        return set()
    return {fila[0].lower() for fila in filas or []}


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


def obtener_info_unidades(id_materia_valor, id_registro_valor):
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
        registro_unidad = {"numero": numero_unidad,
                           "tema": tema_unidad, "bonus_unidad": 0.0}
        info[id_unidad_fila] = registro_unidad
        if numero_unidad and numero_unidad != id_unidad_fila:
            info[numero_unidad] = registro_unidad

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
                bonus_num = a_numero(bonus_val) or 0.0
                info[clave]["bonus_unidad"] = bonus_num

    return info


def obtener_bonus_final(id_materia_valor, id_registro_valor):
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
    return a_numero(fila[0][0]) or 0.0
