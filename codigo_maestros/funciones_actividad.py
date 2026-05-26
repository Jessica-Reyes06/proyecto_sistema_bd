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
        SELECT a.id_actividad, a.detalles, a.ponderacion
        FROM actividad a
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
        for id_actividad, detalles, ponderacion in actividades:
            tarjetas_frame.grid_columnconfigure(col, weight=1)

            card = CTkFrame(tarjetas_frame, fg_color=COLOR_AZUL_CLARO,
                            corner_radius=10, border_width=1, border_color="#BFDBFE",
                            cursor="hand2")
            card.grid(row=0, column=col, padx=6, pady=6, sticky="ew")

            # Contenido de la tarjeta
            top = CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(12, 4))

            CTkLabel(top, text=detalles or f"Actividad {id_actividad}",
                     font=("Arial Rounded MT Bold", 14), text_color="#1E3A5F",
                     wraplength=180, justify="left").pack(side="left", anchor="w")
            CTkLabel(top, text="›", font=("Arial", 20), text_color=COLOR_AZUL).pack(side="right")

            badge_frame = CTkFrame(card, fg_color="transparent")
            badge_frame.pack(anchor="w", padx=12, pady=(0, 12))

            badge = CTkFrame(badge_frame, fg_color=COLOR_AZUL, corner_radius=20)
            badge.pack(side="left")
            CTkLabel(badge, text=f"{int(ponderacion)}%",
                     font=("Arial Rounded MT Bold", 13), text_color="white").pack(padx=10, pady=3)
            CTkLabel(badge_frame, text=" del total",
                     font=("Arial", 13), text_color="#374151").pack(side="left")

            # Click en toda la tarjeta
            def abrir(ia=id_actividad, det=detalles, pond=ponderacion,
                      nu=numero_unidad, tu=tema_unidad):
                vista_calificacion(frame, id_grupo, ia, det, pond, nu, tu, nombre_materia)

            card.bind("<Button-1>", lambda e, fn=abrir: fn())
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, fn=abrir: fn())
                for grandchild in child.winfo_children():
                    grandchild.bind("<Button-1>", lambda e, fn=abrir: fn())

            col += 1


def vista_calificacion(frame, id_grupo, id_actividad, detalles, ponderacion,
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
    CTkLabel(breadcrumb, text=detalles or f"Actividad {id_actividad}",
             font=("Arial", 14, "bold"), text_color=COLOR_AZUL).pack(side="left")

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