import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from customtkinter import *
from db_conexion import ejecutar_select, ejecutar_insert


# ── CONSULTAS ─────────────────────────────────────────────────────────────────

def obtener_unidades_con_actividades(id_grupo):
    sql = """
        SELECT DISTINCT u.id_unidad, u.numero_unidad, u.tema_unidad, u.estado
        FROM unidad u
        LEFT JOIN actividad a ON a.id_unidad = u.id_unidad
        WHERE u.id_grupo = %s
        ORDER BY u.numero_unidad
    """
    return ejecutar_select(sql, (id_grupo,))


def cambiar_estado_unidad(id_unidad, nuevo_estado):
    from db_conexion import conexion
    cur = conexion.cursor()
    cur.execute("UPDATE unidad SET estado = %s WHERE id_unidad = %s", (nuevo_estado, id_unidad))
    conexion.commit()
    cur.close()


def obtener_actividades_por_unidad(id_unidad):
    sql = """
        SELECT a.id_actividad, ta.nombre AS tipo_actividad, a.detalles, a.ponderacion
        FROM actividad a
        LEFT JOIN tipos_actividades ta ON a.id_tipo = ta.id_tipo
        WHERE a.id_unidad = %s
        ORDER BY a.id_actividad
    """
    return ejecutar_select(sql, (id_unidad,))


def obtener_alumnos_con_calificacion(id_grupo, id_actividad):
    sql = """
        SELECT
            r.id_registro,
            a.nombre_alumno,
            a.apellido_paterno,
            a.apellido_materno,
            res.id_resultado,
            res.calificacion,
            res.observaciones
        FROM registro r
        JOIN alumno a ON r.id_alumno = a.id_alumno
        LEFT JOIN resultado res
            ON res.id_registro = r.id_registro
            AND res.id_actividad = %s
        WHERE r.id_grupo = %s
        ORDER BY a.apellido_paterno, a.apellido_materno, a.nombre_alumno
    """
    return ejecutar_select(sql, (id_actividad, id_grupo))


def guardar_calificacion(id_registro, id_actividad, calificacion, observaciones=""):
    """Inserta o actualiza la calificación de un alumno en una actividad."""
    existente = ejecutar_select(
        "SELECT id_resultado FROM resultado WHERE id_registro=%s AND id_actividad=%s",
        (id_registro, id_actividad)
    )
    if existente:
        ejecutar_insert(
            """UPDATE resultado
               SET calificacion=%s, observaciones=%s, fecha_modificacion=NOW()
               WHERE id_registro=%s AND id_actividad=%s""",
            (calificacion, observaciones, id_registro, id_actividad)
        )
    else:
        ejecutar_insert(
            """INSERT INTO resultado (id_registro, id_actividad, calificacion, fecha_registro, fecha_modificacion, observaciones)
               VALUES (%s, %s, %s, NOW(), NOW(), %s)""",
            (id_registro, id_actividad, calificacion, observaciones)
        )


# ── VISTAS ────────────────────────────────────────────────────────────────────

COLOR_MAIN  = "#0E7490"
COLOR_HOVER = "#155E75"
COLOR_SIDE  = "#DFF4F7"
COLOR_AZUL  = "#2563EB"
COLOR_AZUL_CLARO = "#EFF6FF"
COLOR_HEADER_AZUL = "#1D4ED8"
BUTTON_FONT = ("Arial Rounded MT Bold", 14)


def vista_actividades(frame, id_grupo, nombre_materia=""):
    """
    Vista principal de actividades: muestra unidades con sus tarjetas de actividad.
    Al hacer clic en una tarjeta navega a la vista de calificación.
    """
    for w in frame.winfo_children():
        w.destroy()

    # ── HEADER ───────────────────────────────────────────────
    header = CTkFrame(frame, fg_color="white", corner_radius=12)
    header.pack(fill="x", padx=16, pady=(16, 8))

    CTkLabel(header, text=nombre_materia or "Actividades",
             font=("Arial Rounded MT Bold", 26), text_color="#1E3A5F").pack(anchor="w", padx=20, pady=(16, 2))
    CTkLabel(header, text="Selecciona una actividad para calificar",
             font=("Arial", 14), text_color=COLOR_AZUL).pack(anchor="w", padx=20, pady=(0, 16))

    # ── CONTENIDO SCROLLABLE ─────────────────────────────────
    scroll = CTkScrollableFrame(frame, fg_color="#EAF2FB", corner_radius=0)
    scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    unidades = obtener_unidades_con_actividades(id_grupo)

    if not unidades:
        CTkLabel(scroll, text="No hay actividades registradas para este grupo.",
                 font=("Arial", 14), text_color="gray").pack(pady=40)
        return

    for id_unidad, numero_unidad, tema_unidad, estado_unidad in unidades:
        # ── BLOQUE DE UNIDAD ─────────────────────────────────
        bloque = CTkFrame(scroll, fg_color="white", corner_radius=12)
        bloque.pack(fill="x", pady=(0, 16))

        header_unidad = CTkFrame(bloque, fg_color=COLOR_AZUL, corner_radius=10, height=52)
        header_unidad.pack(fill="x")
        header_unidad.pack_propagate(False)

        # Nombre de la unidad a la izquierda
        CTkLabel(header_unidad,
                 text=f"Unidad {numero_unidad}: {tema_unidad}",
                 font=("Arial Rounded MT Bold", 16), text_color="white").pack(
                 side="left", padx=16, pady=14)

        # Badge y botón a la derecha
        lado_der = CTkFrame(header_unidad, fg_color="transparent")
        lado_der.pack(side="right", padx=12, pady=8)

        es_activa = (estado_unidad or "activa") == "activa"
        color_badge = "#16A34A" if es_activa else "#DC2626"
        texto_badge = "● Activa" if es_activa else "● Cerrada"
        texto_btn   = "Cerrar unidad" if es_activa else "Reabrir unidad"
        nuevo_estado = "cerrada" if es_activa else "activa"

        badge_estado = CTkLabel(lado_der, text=texto_badge,
                                font=("Arial Rounded MT Bold", 13),
                                text_color=color_badge, fg_color="white",
                                corner_radius=20)
        badge_estado.pack(side="left", padx=(0, 8), ipadx=8, ipady=3)

        # Label de error para validaciones, debajo del header
        lbl_error = CTkLabel(bloque, text="", font=("Arial", 12),
                             text_color="#DC2626", fg_color="transparent")
        lbl_error.pack(anchor="w", padx=16, pady=(4, 0))

        def toggle_estado(iu=id_unidad, frame_ref=frame,
                          ig=id_grupo, nm=nombre_materia, lbl=lbl_error):
            from db_conexion import conexion
            cur = conexion.cursor()

            # Verificar estado actual
            cur.execute("SELECT estado FROM unidad WHERE id_unidad = %s", (iu,))
            actual = cur.fetchone()[0]

            # Si está cerrando, validar antes
            if actual == "activa":
                # Validar suma de ponderaciones = 100
                cur.execute(
                    "SELECT COALESCE(SUM(ponderacion), 0) FROM actividad WHERE id_unidad = %s",
                    (iu,)
                )
                suma = float(cur.fetchone()[0])
                if suma != 100:
                    lbl.configure(text=f"⚠ Las ponderaciones suman {suma:.1f}%, deben sumar 100%.")
                    cur.close()
                    return

                # Validar que todos los alumnos tengan calificación en todas las actividades
                cur.execute("""
                    SELECT COUNT(*) FROM registro r
                    JOIN actividad a ON a.id_unidad = %s
                    LEFT JOIN resultado res
                        ON res.id_registro = r.id_registro
                        AND res.id_actividad = a.id_actividad
                    WHERE r.id_grupo = (
                        SELECT id_grupo FROM unidad WHERE id_unidad = %s LIMIT 1
                    )
                    AND (res.calificacion IS NULL OR res.id_resultado IS NULL)
                """, (iu, iu))
                sin_calificacion = cur.fetchone()[0]
                if sin_calificacion > 0:
                    lbl.configure(text=f"⚠ Hay {sin_calificacion} calificación(es) pendiente(s) de capturar.")
                    cur.close()
                    return

            # Todo válido, cambiar estado
            nuevo = "cerrada" if actual == "activa" else "activa"
            cur.execute("UPDATE unidad SET estado = %s WHERE id_unidad = %s", (nuevo, iu))
            conexion.commit()
            cur.close()
            vista_actividades(frame_ref, ig, nm)

        CTkButton(lado_der, text=texto_btn,
                  fg_color="white", text_color=COLOR_AZUL,
                  hover_color="#DBEAFE", font=("Arial Rounded MT Bold", 13),
                  height=30, corner_radius=8,
                  command=toggle_estado).pack(side="left")

        # ── TARJETAS DE ACTIVIDADES ──────────────────────────
        actividades = obtener_actividades_por_unidad(id_unidad)

        tarjetas_frame = CTkFrame(bloque, fg_color="white", corner_radius=0)
        tarjetas_frame.pack(fill="x", padx=12, pady=12)

        if not actividades:
            CTkLabel(tarjetas_frame, text="Sin actividades en esta unidad.",
                     font=("Arial", 13), text_color="gray").pack(anchor="w", padx=8, pady=8)
            continue

        col = 0
        for id_actividad, tipo_actividad, detalles, ponderacion in actividades:
            tarjetas_frame.grid_columnconfigure(col, weight=1)

            card = CTkFrame(tarjetas_frame, fg_color=COLOR_AZUL_CLARO,
                            corner_radius=10, border_width=1, border_color="#BFDBFE",
                            cursor="hand2")
            card.grid(row=0, column=col, padx=6, pady=6, sticky="ew")

            # Contenido de la tarjeta
            top = CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(12, 4))

            CTkLabel(top, text=tipo_actividad or f"Actividad {id_actividad}",
                     font=("Arial Rounded MT Bold", 14), text_color="#1E3A5F",
                     wraplength=180, justify="left").pack(side="left", anchor="w")
            CTkLabel(top, text="›", font=("Arial", 20), text_color=COLOR_AZUL).pack(side="right")

            if detalles:
                CTkLabel(card, text=detalles,
                         font=("Arial", 11), text_color="#475569",
                         wraplength=180, justify="left").pack(anchor="w", padx=12, pady=(0, 6))

            badge_frame = CTkFrame(card, fg_color="transparent")
            badge_frame.pack(anchor="w", padx=12, pady=(0, 12))

            badge = CTkFrame(badge_frame, fg_color=COLOR_AZUL, corner_radius=20)
            badge.pack(side="left")
            CTkLabel(badge, text=f"{int(ponderacion)}%",
                     font=("Arial Rounded MT Bold", 13), text_color="white").pack(padx=10, pady=3)
            CTkLabel(badge_frame, text=" del total",
                     font=("Arial", 13), text_color="#374151").pack(side="left")

            # Click en toda la tarjeta
            def abrir(ia=id_actividad, tipo=tipo_actividad, det=detalles, pond=ponderacion,
                      nu=numero_unidad, tu=tema_unidad):
                vista_calificacion(frame, id_grupo, ia, tipo, det, pond, nu, tu, nombre_materia)

            card.bind("<Button-1>", lambda e, fn=abrir: fn())
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, fn=abrir: fn())
                for grandchild in child.winfo_children():
                    grandchild.bind("<Button-1>", lambda e, fn=abrir: fn())

            col += 1


def vista_calificacion(frame, id_grupo, id_actividad, tipo_actividad, detalles, ponderacion,
                       numero_unidad, tema_unidad, nombre_materia=""):
    """
    Vista de calificación: muestra la lista de alumnos con campos para ingresar calificaciones.
    """
    for w in frame.winfo_children():
        w.destroy()

    # ── HEADER CON BOTÓN REGRESAR ────────────────────────────
    header = CTkFrame(frame, fg_color="white", corner_radius=12)
    header.pack(fill="x", padx=16, pady=(16, 8))

    btn_back = CTkButton(header, text="← Volver a unidades",
                         fg_color="transparent", text_color=COLOR_AZUL,
                         hover_color=COLOR_AZUL_CLARO, font=("Arial", 14),
                         command=lambda: vista_actividades(frame, id_grupo, nombre_materia))
    btn_back.pack(anchor="w", padx=12, pady=(12, 4))

    CTkLabel(header, text=nombre_materia or "Actividad",
             font=("Arial Rounded MT Bold", 26), text_color="#1E3A5F").pack(anchor="w", padx=20, pady=(0, 2))

    breadcrumb = CTkFrame(header, fg_color="transparent")
    breadcrumb.pack(anchor="w", padx=20, pady=(0, 16))
    CTkLabel(breadcrumb, text=f"Unidad {numero_unidad}: {tema_unidad}",
             font=("Arial", 14), text_color=COLOR_AZUL).pack(side="left")
    CTkLabel(breadcrumb, text="  ›  ", font=("Arial", 14), text_color="#9CA3AF").pack(side="left")
    detalle_frame = CTkFrame(breadcrumb, fg_color="transparent")
    detalle_frame.pack(side="left")
    CTkLabel(detalle_frame, text=tipo_actividad or f"Actividad {id_actividad}",
             font=("Arial", 15, "bold"), text_color=COLOR_AZUL).pack(anchor="w")
    if detalles:
        CTkLabel(detalle_frame, text=detalles,
                 font=("Arial", 11), text_color="#6B7280",
                 wraplength=520, justify="left").pack(anchor="w")

    # Badge ponderación
    badge_frame = CTkFrame(header, fg_color=COLOR_AZUL_CLARO, corner_radius=10)
    badge_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=16)
    CTkLabel(badge_frame, text="Valor de la actividad",
             font=("Arial", 12), text_color="#374151").pack(padx=16, pady=(10, 0))
    CTkLabel(badge_frame, text=f"{int(ponderacion)}%",
             font=("Arial Rounded MT Bold", 28), text_color=COLOR_AZUL).pack(padx=16, pady=(0, 10))

    # ── TABLA DE ALUMNOS ─────────────────────────────────────
    tabla_frame = CTkFrame(frame, fg_color="white", corner_radius=12)
    tabla_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    # Título y botón guardar
    top_tabla = CTkFrame(tabla_frame, fg_color="transparent")
    top_tabla.pack(fill="x", padx=20, pady=(16, 8))

    CTkLabel(top_tabla, text="Lista de Alumnos",
             font=("Arial Rounded MT Bold", 20), text_color="#1E3A5F").pack(side="left")

    estado_lbl = CTkLabel(top_tabla, text="", font=("Arial", 13), text_color="gray")
    estado_lbl.pack(side="left", padx=16)

    entries = {}  # id_registro -> CTkEntry

    def guardar_todas():
        errores = 0
        guardadas = 0
        for id_reg, entry in entries.items():
            valor = entry.get().strip()
            if valor == "":
                continue
            try:
                cal = float(valor)
                if cal < 0 or cal > 100:
                    raise ValueError
                guardar_calificacion(id_reg, id_actividad, cal)
                guardadas += 1
            except ValueError:
                errores += 1
        if errores:
            estado_lbl.configure(text=f"⚠ {errores} valor(es) inválido(s)", text_color="#B00020")
        else:
            estado_lbl.configure(text=f"✓ {guardadas} calificación(es) guardada(s)", text_color="#1B5E20")

    CTkButton(top_tabla, text="  Guardar Calificaciones",
              fg_color=COLOR_AZUL, hover_color=COLOR_HEADER_AZUL,
              font=("Arial Rounded MT Bold", 14), corner_radius=8,
              command=guardar_todas).pack(side="right")

    # Encabezado tabla
    enc = CTkFrame(tabla_frame, fg_color="#DBEAFE", corner_radius=6)
    enc.pack(fill="x", padx=20, pady=(0, 4))
    enc.grid_columnconfigure(0, minsize=60)
    enc.grid_columnconfigure(1, weight=1)
    enc.grid_columnconfigure(2, minsize=200)

    CTkLabel(enc, text="#", font=("Arial", 13, "bold"), text_color="#1E3A5F",
             width=60, anchor="center").grid(row=0, column=0, padx=10, pady=10)
    CTkLabel(enc, text="Nombre del Alumno", font=("Arial", 13, "bold"),
             text_color="#1E3A5F", anchor="w").grid(row=0, column=1, padx=10, pady=10, sticky="w")
    CTkLabel(enc, text="Calificación (0-100)", font=("Arial", 13, "bold"),
             text_color="#1E3A5F", width=200, anchor="center").grid(row=0, column=2, padx=10, pady=10)

    # Filas scrollables
    scroll_alumnos = CTkScrollableFrame(tabla_frame, fg_color="transparent")
    scroll_alumnos.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    alumnos = obtener_alumnos_con_calificacion(id_grupo, id_actividad)

    if not alumnos:
        CTkLabel(scroll_alumnos, text="No hay alumnos inscritos en este grupo.",
                 font=("Arial", 14), text_color="gray").pack(pady=30)
        return

    for idx, (id_registro, nombre, ap_pat, ap_mat, id_resultado, calificacion, observaciones) in enumerate(alumnos, 1):
        color_fila = "#F8FAFF" if idx % 2 == 0 else "white"
        fila = CTkFrame(scroll_alumnos, fg_color=color_fila, corner_radius=8)
        fila.pack(fill="x", pady=3)
        fila.grid_columnconfigure(0, minsize=60)
        fila.grid_columnconfigure(1, weight=1)
        fila.grid_columnconfigure(2, minsize=200)

        CTkLabel(fila, text=str(idx), font=("Arial", 13), text_color=COLOR_AZUL,
                 width=60, anchor="center").grid(row=0, column=0, padx=10, pady=12)

        nombre_completo = f"{nombre} {ap_pat} {ap_mat or ''}".strip()
        CTkLabel(fila, text=nombre_completo, font=("Arial", 13),
                 text_color="#111827", anchor="w").grid(row=0, column=1, padx=10, pady=12, sticky="w")

        entry = CTkEntry(fila, width=180, height=36, justify="center",
                         fg_color="#F1F5F9", border_color="#CBD5E1",
                         text_color="#111827", font=("Arial", 13))
        if calificacion is not None:
            entry.insert(0, str(int(calificacion) if float(calificacion) == int(calificacion) else calificacion))
        else:
            entry.insert(0, "0")
        entry.grid(row=0, column=2, padx=16, pady=8)
        entries[id_registro] = entry

# ── BONUS ─────────────────────────────────────────────────────────────────────

def obtener_alumnos_grupo_bonus(id_grupo):
    sql = """
        SELECT R.id_registro, A.numero_control, A.nombre_alumno,
               A.apellido_paterno, A.apellido_materno
        FROM registro R
        JOIN alumno A ON R.id_alumno = A.id_alumno
        WHERE R.id_grupo = %s
        ORDER BY A.apellido_paterno, A.apellido_materno, A.nombre_alumno
    """
    return ejecutar_select(sql, (id_grupo,))


def obtener_bonus_unidad_alumno(id_registro, id_unidad):
    filas = ejecutar_select(
        'SELECT valor FROM bonusunidad WHERE id_registro=%s AND id_unidad=%s ORDER BY "id_bonusUnidad" DESC LIMIT 1',
        (id_registro, id_unidad)
    )
    try:
        return float(filas[0][0]) if filas else 0.0
    except Exception:
        return 0.0


def obtener_bonus_semestre_alumno(id_registro, id_grupo):
    filas = ejecutar_select(
        'SELECT valor FROM bonusmateria BM JOIN registro R ON BM.id_registro=R.id_registro WHERE BM.id_registro=%s AND R.id_grupo=%s ORDER BY "id_bonusMateria" DESC LIMIT 1',
        (id_registro, id_grupo)
    )
    try:
        return float(filas[0][0]) if filas else 0.0
    except Exception:
        return 0.0


def obtener_promedio_final_alumno(id_registro, id_grupo):
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
        return 0.0

    unidades = {}
    for id_unidad, ponderacion, calificacion in filas:
        clave = str(id_unidad).strip()
        if clave not in unidades:
            unidades[clave] = 0.0
        try:
            por = float(ponderacion) if ponderacion else 0.0
            cal = float(calificacion) if calificacion is not None else None
        except Exception:
            continue
        if cal is not None:
            unidades[clave] += cal * (por / 100.0)

    if not unidades:
        return 0.0

    suma = 0.0
    for clave, base in unidades.items():
        bonus = obtener_bonus_unidad_alumno(id_registro, clave)
        suma += min(100.0, base + bonus)

    promedio = suma / len(unidades)
    bonus_sem = obtener_bonus_semestre_alumno(id_registro, id_grupo)
    return round(min(100.0, promedio + bonus_sem), 2)


def abrir_modal_bonus(parent, id_registro, numero_control, nombre_completo, id_grupo, on_guardado=None):
    modal = CTkToplevel(parent)
    modal.title("Asignar Bonus")
    modal.resizable(True, True)
    modal.grab_set()
    modal.configure(fg_color="white")

    # Centrar y dimensionar según pantalla
    modal.update_idletasks()
    sw = modal.winfo_screenwidth()
    sh = modal.winfo_screenheight()
    w, h = min(580, sw - 40), min(sh - 60, sh - 40)
    x, y = (sw - w) // 2, (sh - h) // 2
    modal.geometry(f"{w}x{h}+{x}+{y}")

    # ── CONTENIDO SCROLLABLE ──────────────────────────────────
    scroll_modal = CTkScrollableFrame(modal, fg_color="white")
    scroll_modal.pack(fill="both", expand=True)

    # Header
    header = CTkFrame(scroll_modal, fg_color="white")
    header.pack(fill="x", padx=24, pady=(20, 0))

    avatar = CTkFrame(header, fg_color=COLOR_AZUL, width=48, height=48, corner_radius=24)
    avatar.pack(side="left")
    avatar.pack_propagate(False)
    CTkLabel(avatar, text="🎓", font=("Arial", 22), fg_color="transparent").pack(expand=True)

    info = CTkFrame(header, fg_color="transparent")
    info.pack(side="left", padx=12)
    CTkLabel(info, text="Asignar Bonus", font=("Arial Rounded MT Bold", 20),
             text_color="#0F172A").pack(anchor="w")
    CTkLabel(info, text=f"{numero_control} - {nombre_completo}",
             font=("Arial", 13), text_color="#6B7280").pack(anchor="w")

    CTkButton(header, text="✕", width=32, height=32, corner_radius=16,
              fg_color="#F1F5F9", text_color="#374151", hover_color="#E2E8F0",
              font=("Arial", 14), command=modal.destroy).pack(side="right")

    CTkFrame(scroll_modal, height=1, fg_color="#E2E8F0").pack(fill="x", pady=12)

    # Tipo de Bonus
    CTkLabel(scroll_modal, text="Tipo de Bonus", font=("Arial Rounded MT Bold", 14),
             text_color="#374151", fg_color="white").pack(anchor="w", padx=24)

    tipo_var = StringVar(value="unidad")
    selector = CTkFrame(scroll_modal, fg_color="white")
    selector.pack(fill="x", padx=24, pady=(8, 16))
    selector.grid_columnconfigure(0, weight=1)
    selector.grid_columnconfigure(1, weight=1)

    btn_unidad = CTkButton(selector,
                           text="Bonus por Unidad Aplicar bonus a una unidad específica",
                           font=("Arial Rounded MT Bold", 13), corner_radius=10,
                           fg_color=COLOR_AZUL_CLARO, text_color=COLOR_AZUL,
                           border_width=2, border_color=COLOR_AZUL,
                           hover_color="#DBEAFE", height=70)
    btn_semestre = CTkButton(selector,
                             text="Bonus por Semestre Aplicar bonus a toda la materia",
                             font=("Arial Rounded MT Bold", 13), corner_radius=10,
                             fg_color="white", text_color="#374151",
                             border_width=1, border_color="#E2E8F0",
                             hover_color="#F8FAFC", height=70)
    btn_unidad.grid(row=0, column=0, padx=(0, 6), sticky="ew")
    btn_semestre.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    # Dropdown de unidades
    unidades_raw = ejecutar_select(
        "SELECT id_unidad, numero_unidad, tema_unidad FROM unidad WHERE id_grupo=%s ORDER BY numero_unidad",
        (id_grupo,)
    )
    opciones_unidad = [f"U{num}. {tema}" for _, num, tema in unidades_raw]
    ids_unidad = [str(iu) for iu, _, _ in unidades_raw]

    frame_unidad_sel = CTkFrame(scroll_modal, fg_color="white")
    frame_unidad_sel.pack(fill="x", padx=24)
    CTkLabel(frame_unidad_sel, text="Seleccionar Unidad *",
             font=("Arial Rounded MT Bold", 13), text_color="#374151").pack(anchor="w", pady=(0, 6))
    cb_unidad = CTkComboBox(frame_unidad_sel, values=opciones_unidad,
                            state="readonly", height=42, font=("Arial", 14))
    if opciones_unidad:
        cb_unidad.set(opciones_unidad[0])
    cb_unidad.pack(fill="x")

    # Porcentaje
    CTkLabel(scroll_modal, text="Porcentaje de Bonus *", font=("Arial Rounded MT Bold", 13),
             text_color="#374151", fg_color="white").pack(anchor="w", padx=24, pady=(14, 4))
    e_bonus_frame = CTkFrame(scroll_modal, fg_color="white")
    e_bonus_frame.pack(fill="x", padx=24)
    e_bonus_frame.grid_columnconfigure(0, weight=1)
    e_bonus = CTkEntry(e_bonus_frame, height=42, font=("Arial", 15),
                       placeholder_text="0", border_color="#E2E8F0",
                       fg_color="white", text_color="#0F172A")
    e_bonus.grid(row=0, column=0, sticky="ew")
    CTkLabel(e_bonus_frame, text="%", font=("Arial Rounded MT Bold", 15),
             text_color="#6B7280", fg_color="white", width=36).grid(row=0, column=1, padx=(6, 0))
    CTkLabel(scroll_modal, text="Ingrese un valor entre 0 y 100",
             font=("Arial", 11), text_color="#9CA3AF", fg_color="white").pack(anchor="w", padx=24, pady=(2, 0))

    # Justificación
    CTkLabel(scroll_modal, text="Justificación *", font=("Arial Rounded MT Bold", 13),
             text_color="#374151", fg_color="white").pack(anchor="w", padx=24, pady=(14, 4))
    e_just = CTkTextbox(scroll_modal, height=80, font=("Arial", 14),
                        border_color="#E2E8F0", fg_color="white",
                        text_color="#0F172A", border_width=1)
    e_just.pack(fill="x", padx=24)
    CTkLabel(scroll_modal, text="Explica brevemente la razón del bonus",
             font=("Arial", 11), text_color="#9CA3AF", fg_color="white").pack(anchor="w", padx=24, pady=(2, 0))

    # ── CÁLCULO DE CALIFICACIÓN ───────────────────────────────
    calc_frame = CTkFrame(scroll_modal, fg_color=COLOR_AZUL_CLARO, corner_radius=10)
    calc_frame.pack(fill="x", padx=24, pady=14)

    CTkLabel(calc_frame, text="Resumen del Bonus", font=("Arial Rounded MT Bold", 14),
             text_color="#0F172A", fg_color="transparent").pack(anchor="w", padx=16, pady=(12, 4))
    CTkLabel(calc_frame, text=f"Alumno: {nombre_completo}",
             font=("Arial", 13), text_color="#374151", fg_color="transparent").pack(anchor="w", padx=16, pady=2)
    lbl_res_tipo = CTkLabel(calc_frame, text="Tipo: Bonus por Unidad",
                            font=("Arial", 13), text_color="#374151", fg_color="transparent")
    lbl_res_tipo.pack(anchor="w", padx=16, pady=2)
    lbl_res_unidad = CTkLabel(calc_frame, text=f"Unidad: {opciones_unidad[0] if opciones_unidad else '-'}",
                              font=("Arial", 13), text_color="#374151", fg_color="transparent")
    lbl_res_unidad.pack(anchor="w", padx=16, pady=(2, 8))

    # Cálculo numérico
    sep_calc = CTkFrame(calc_frame, fg_color="white", corner_radius=8)
    sep_calc.pack(fill="x", padx=16, pady=(0, 12))

    CTkLabel(sep_calc, text="CÁLCULO DE CALIFICACIÓN",
             font=("Arial", 10, "bold"), text_color="#6B7280",
             fg_color="transparent").pack(anchor="w", padx=12, pady=(10, 4))

    promedio_actual = obtener_promedio_final_alumno(id_registro, id_grupo)

    fila_actual = CTkFrame(sep_calc, fg_color="transparent")
    fila_actual.pack(fill="x", padx=12, pady=2)
    CTkLabel(fila_actual, text="Calificación Actual:", font=("Arial", 13),
             text_color="#374151", fg_color="transparent").pack(side="left")
    CTkLabel(fila_actual, text=f"{promedio_actual:.1f}", font=("Arial Rounded MT Bold", 15),
             text_color="#0F172A", fg_color="transparent").pack(side="right")

    fila_bonus = CTkFrame(sep_calc, fg_color="transparent")
    fila_bonus.pack(fill="x", padx=12, pady=2)
    CTkLabel(fila_bonus, text="Bonus a Aplicar:", font=("Arial", 13),
             text_color="#374151", fg_color="transparent").pack(side="left")
    lbl_bonus_preview = CTkLabel(fila_bonus, text="+0.0", font=("Arial Rounded MT Bold", 15),
                                  text_color=COLOR_AZUL, fg_color="transparent")
    lbl_bonus_preview.pack(side="right")

    CTkFrame(sep_calc, height=1, fg_color="#E2E8F0").pack(fill="x", padx=12, pady=6)

    fila_op = CTkFrame(sep_calc, fg_color="transparent")
    fila_op.pack(fill="x", padx=12, pady=2)
    CTkLabel(fila_op, text="Operación:", font=("Arial", 11),
             text_color="#9CA3AF", fg_color="transparent").pack(anchor="center")
    lbl_operacion = CTkLabel(fila_op, text=f"{promedio_actual:.1f} + 0.0 = {promedio_actual:.1f}",
                              font=("Arial", 13), text_color="#374151", fg_color="transparent")
    lbl_operacion.pack(anchor="center")

    fila_final = CTkFrame(sep_calc, fg_color="transparent")
    fila_final.pack(fill="x", padx=12, pady=(4, 12))
    CTkLabel(fila_final, text="Calificación Final:", font=("Arial Rounded MT Bold", 14),
             text_color="#0F172A", fg_color="transparent").pack(side="left")
    lbl_final_preview = CTkLabel(fila_final, text=f"{promedio_actual:.1f}",
                                  font=("Arial Rounded MT Bold", 22),
                                  text_color="#1B5E20", fg_color="transparent")
    lbl_final_preview.pack(side="right")

    def actualizar_calculo(*_):
        try:
            b = float(e_bonus.get().strip())
        except Exception:
            b = 0.0
        nueva = round(min(100.0, promedio_actual + b), 1)
        lbl_bonus_preview.configure(text=f"+{b:.1f}")
        lbl_operacion.configure(text=f"{promedio_actual:.1f} + {b:.1f} = {nueva:.1f}")
        lbl_final_preview.configure(text=f"{nueva:.1f}",
                                     text_color="#1B5E20" if nueva >= 60 else "#B00020")

    e_bonus.bind("<KeyRelease>", actualizar_calculo)

    lbl_estado = CTkLabel(scroll_modal, text="", font=("Arial", 13),
                          text_color="gray", fg_color="white", wraplength=500)
    lbl_estado.pack(anchor="w", padx=24, pady=(4, 0))

    # Lógica tipo
    def sel_unidad():
        tipo_var.set("unidad")
        btn_unidad.configure(fg_color=COLOR_AZUL_CLARO, text_color=COLOR_AZUL,
                             border_width=2, border_color=COLOR_AZUL)
        btn_semestre.configure(fg_color="white", text_color="#374151",
                               border_width=1, border_color="#E2E8F0")
        frame_unidad_sel.pack(fill="x", padx=24)
        lbl_res_tipo.configure(text="Tipo: Bonus por Unidad")
        lbl_res_unidad.pack(anchor="w", padx=16, pady=(2, 8))

    def sel_semestre():
        tipo_var.set("semestre")
        btn_semestre.configure(fg_color=COLOR_AZUL_CLARO, text_color=COLOR_AZUL,
                               border_width=2, border_color=COLOR_AZUL)
        btn_unidad.configure(fg_color="white", text_color="#374151",
                             border_width=1, border_color="#E2E8F0")
        frame_unidad_sel.pack_forget()
        lbl_res_tipo.configure(text="Tipo: Bonus por Semestre")
        lbl_res_unidad.pack_forget()

    btn_unidad.configure(command=sel_unidad)
    btn_semestre.configure(command=sel_semestre)
    cb_unidad.configure(command=lambda v: lbl_res_unidad.configure(text=f"Unidad: {v}"))

    # ── FOOTER FIJO ───────────────────────────────────────────
    CTkFrame(modal, height=1, fg_color="#E2E8F0").pack(fill="x")
    footer = CTkFrame(modal, fg_color="white")
    footer.pack(fill="x", padx=24, pady=12)

    CTkButton(footer, text="Cancelar", fg_color="white", text_color="#374151",
              border_width=1, border_color="#E2E8F0", hover_color="#F1F5F9",
              height=40, corner_radius=8, command=modal.destroy).pack(side="left")

    def aplicar():
        try:
            bonus = float(e_bonus.get().strip())
        except ValueError:
            lbl_estado.configure(text="⚠ Ingresa un porcentaje válido.", text_color="#B00020")
            return
        if bonus <= 0 or bonus > 100:
            lbl_estado.configure(text="⚠ El bonus debe estar entre 0 y 100.", text_color="#B00020")
            return
        justificacion = e_just.get("1.0", "end").strip()
        if not justificacion:
            lbl_estado.configure(text="⚠ La justificación es obligatoria.", text_color="#B00020")
            return
        try:
            if tipo_var.get() == "unidad":
                idx = opciones_unidad.index(cb_unidad.get())
                id_unidad = ids_unidad[idx]
                ejecutar_insert(
                    'INSERT INTO bonusunidad (id_registro, id_unidad, valor, justificacion) VALUES (%s, %s, %s, %s)',
                    (id_registro, id_unidad, bonus, justificacion)
                )
            else:
                ejecutar_insert(
                    'INSERT INTO bonusmateria (id_registro, valor, justificacion) VALUES (%s, %s, %s)',
                    (id_registro, bonus, justificacion)
                )
            lbl_estado.configure(text="✓ Bonus aplicado correctamente.", text_color="#1B5E20")
            if on_guardado:
                modal.after(800, lambda: (modal.destroy(), on_guardado()))
            else:
                modal.after(800, modal.destroy)
        except Exception as ex:
            lbl_estado.configure(text=f"Error: {ex}", text_color="#B00020")

    CTkButton(footer, text="Aplicar Bonus", fg_color=COLOR_AZUL, hover_color=COLOR_HEADER_AZUL,
              text_color="white", height=40, corner_radius=8,
              font=("Arial Rounded MT Bold", 14), command=aplicar).pack(side="right")


def vista_bonus(frame, id_grupo):
    """Vista unificada de bonus: tabla con alumnos, bonus y promedio final."""
    print(f"DEBUG: vista_bonus called with id_grupo={id_grupo}")
    for w in frame.winfo_children():
        w.destroy()

    # Header
    header = CTkFrame(frame, fg_color="white", corner_radius=12)
    header.pack(fill="x", padx=16, pady=(16, 4))
    CTkLabel(header, text="Gestión de Bonus",
             font=("Arial Rounded MT Bold", 24), text_color="#0F172A").pack(anchor="w", padx=4)
    CTkLabel(header, text="Asigna puntos bonus por unidad o por semestre a tus alumnos",
             font=("Arial", 13), text_color="#6B7280").pack(anchor="w", padx=4, pady=(2, 12))

    # Obtener alumnos y mostrar estado en la cabecera
    alumnos = obtener_alumnos_grupo_bonus(id_grupo)
    CTkLabel(header, text=f"Grupo: {id_grupo} — Alumnos: {len(alumnos)}",
             font=("Arial", 12), text_color="#374151").pack(anchor="w", padx=4, pady=(0, 8))
    if not alumnos:
        CTkLabel(frame, text="No hay alumnos inscritos en este grupo.",
                 font=("Arial", 16), text_color="gray").pack(pady=40)
        return

    # Tabla
    tabla = CTkFrame(frame, fg_color="white", corner_radius=12,
                     border_width=1, border_color="#E2E8F0")
    tabla.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    # Encabezado
    enc = CTkFrame(tabla, fg_color="#F8FAFC", corner_radius=0)
    enc.pack(fill="x")
    for col, (texto, minsize) in enumerate([
        ("MATRÍCULA", 130), ("NOMBRE COMPLETO", 0),
        ("BONUS UNIDADES", 140), ("BONUS SEMESTRE", 140),
        ("PROMEDIO FINAL", 140), ("ACCIONES", 170)
    ]):
        enc.grid_columnconfigure(col, minsize=minsize, weight=1 if minsize == 0 else 0)
        CTkLabel(enc, text=texto, font=("Arial", 11, "bold"),
                 text_color="#6B7280", anchor="w").grid(
                 row=0, column=col, padx=16, pady=12, sticky="w")

    scroll = CTkScrollableFrame(tabla, fg_color="white")
    scroll.pack(fill="both", expand=True)

    def render_filas():
        for w in scroll.winfo_children():
            w.destroy()

        alumnos = obtener_alumnos_grupo_bonus(id_grupo)
        if not alumnos:
            CTkLabel(scroll, text="No hay alumnos inscritos en este grupo.",
                     font=("Arial", 14), text_color="gray").pack(pady=20)
            return

        for idx, (id_registro, numero_control, nombre, ap_pat, ap_mat) in enumerate(alumnos):
            nombre_completo = f"{nombre} {ap_pat} {ap_mat or ''}".strip()
            bonus_sem = obtener_bonus_semestre_alumno(id_registro, id_grupo)
            promedio = obtener_promedio_final_alumno(id_registro, id_grupo)

            color_fila = "#FAFAFA" if idx % 2 == 0 else "white"
            fila = CTkFrame(scroll, fg_color=color_fila, corner_radius=0)
            fila.pack(fill="x")
            CTkFrame(fila, height=1, fg_color="#F1F5F9").pack(fill="x")

            for col, minsize in enumerate([130, 0, 140, 140, 140, 170]):
                fila.grid_columnconfigure(col, minsize=minsize, weight=1 if minsize == 0 else 0)

            CTkLabel(fila, text=numero_control, font=("Arial", 13, "bold"),
                     text_color="#0F172A", anchor="w").grid(row=0, column=0, padx=16, pady=14, sticky="w")
            CTkLabel(fila, text=nombre_completo, font=("Arial", 13),
                     text_color="#374151", anchor="w").grid(row=0, column=1, padx=16, pady=14, sticky="w")
            CTkLabel(fila, text="-", font=("Arial", 13),
                     text_color="#6B7280", anchor="w").grid(row=0, column=2, padx=16, pady=14, sticky="w")
            CTkLabel(fila,
                     text=f"+{bonus_sem:.1f}%" if bonus_sem > 0 else "-",
                     font=("Arial", 13),
                     text_color="#1B5E20" if bonus_sem > 0 else "#6B7280",
                     anchor="w").grid(row=0, column=3, padx=16, pady=14, sticky="w")
            CTkLabel(fila, text=f"{promedio:.1f}",
                     font=("Arial Rounded MT Bold", 13),
                     text_color="#1B5E20" if promedio >= 60 else "#B00020",
                     anchor="w").grid(row=0, column=4, padx=16, pady=14, sticky="w")
            CTkButton(fila, text="🎓  Asignar Bonus",
                      fg_color=COLOR_MAIN, hover_color=COLOR_HOVER,
                      text_color="white", font=("Arial Rounded MT Bold", 13),
                      height=34, corner_radius=8,
                      command=lambda ir=id_registro, nc=numero_control, nm=nombre_completo:
                          abrir_modal_bonus(frame, ir, nc, nm, id_grupo, on_guardado=render_filas)
                      ).grid(row=0, column=5, padx=16, pady=10, sticky="w")

    render_filas()