from tkinter import messagebox
from customtkinter import *
from PIL import Image
from config_principal import calendario, limpiar_frame
from formularios_bd import *
import os
import sys


def ruta_recurso(ruta_relativa):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, ruta_relativa)


def color_texto_legible(color_hex):
    if not isinstance(color_hex, str) or not color_hex.startswith("#") or len(color_hex) != 7:
        return "white"

    rojo = int(color_hex[1:3], 16)
    verde = int(color_hex[3:5], 16)
    azul = int(color_hex[5:7], 16)
    luminosidad = (0.299 * rojo) + (0.587 * verde) + (0.114 * azul)
    return "black" if luminosidad > 160 else "white"


def crear_tabla_editable(parent, headers, registros, tabla_sql, color_tabla="#e0e0e0", actualizar_callback=None, eliminar_callback=None, header_text_color=None, ocultar_primer_campo=False, editar_callback=None, callback_recargar_tabla=None):
    """
    Crea tabla editable con:
    - Ancho máximo de celdas (180px)
    - Texto envuelto verticalmente
    - Scroll horizontal para tablas anchas
    - callback_recargar_tabla: Función para recargar la tabla después de eliminar (recarga desde BD)
    """
    tabla = CTkFrame(parent)
    tabla.pack(fill="both", expand=True)

    # ENCABEZADO FIJO
    encabezado = CTkFrame(tabla, fg_color=color_tabla)
    encabezado.pack(fill="x")
    color_texto = header_text_color or color_texto_legible(color_tabla)

    # Ancho fijo para columnas
    ANCHO_CELDA = 180

    for i, h in enumerate(headers):
        encabezado.grid_columnconfigure(i, minsize=ANCHO_CELDA)
        CTkLabel(
            encabezado,
            text=h,
            text_color=color_texto,
            font=("Arial", 14, "bold"),
            anchor="w",
            justify="left",
            wraplength=ANCHO_CELDA - 20
        ).grid(row=0, column=i, padx=10, pady=10, sticky="ew")

    # Columnas para botones
    encabezado.grid_columnconfigure(len(headers), minsize=100)
    if eliminar_callback:
        encabezado.grid_columnconfigure(len(headers) + 1, minsize=100)

    # CONTENEDOR CON SCROLL (Canvas para scroll horizontal)
    from tkinter import Canvas, Scrollbar

    canvas_frame = CTkFrame(tabla)
    canvas_frame.pack(fill="both", expand=True)

    canvas = Canvas(canvas_frame, bg="#ffffff", highlightthickness=0)
    scrollbar_h = Scrollbar(
        canvas_frame, orient="horizontal", command=canvas.xview)
    scrollbar_v = Scrollbar(canvas_frame, orient="vertical")

    canvas.config(xscrollcommand=scrollbar_h.set,
                  yscrollcommand=scrollbar_v.set)

    # Frame interno para el contenido
    cuerpo = CTkFrame(canvas, fg_color="#ffffff")
    canvas_window = canvas.create_window((0, 0), window=cuerpo, anchor="nw")

    # Posicionar scrollbars y canvas
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar_h.grid(row=1, column=0, sticky="ew")
    scrollbar_v.grid(row=0, column=1, sticky="ns")

    canvas_frame.grid_rowconfigure(0, weight=1)
    canvas_frame.grid_columnconfigure(0, weight=1)

    def on_frame_configure(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Ajustar ancho del canvas window al ancho del canvas
        canvas_width = canvas.winfo_width()
        if canvas_width > 1:
            canvas.itemconfig(canvas_window, width=canvas_width)

    cuerpo.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", lambda e: cuerpo.event_generate("<Configure>"))

    fila_editando = {"idx": None}
    entries = {}
    btn_editar_ref = {}
    btn_eliminar_ref = {}

    def editar_fila(idx):
        fila = registros[idx]
        valores_visibles = fila[1:] if ocultar_primer_campo else fila
        # Si hay un callback de edición personalizado, usarlo (ej: para Carreras)
        if editar_callback:
            editar_callback(fila, mostrar_filas)
            return
        # Si no, usar edición inline
            widget.destroy()
        for col_idx, valor in enumerate(valores_visibles):
            e = CTkEntry(cuerpo, width=ANCHO_CELDA - 20)
            e.insert(0, str(valor))
            e.grid(row=idx, column=col_idx, padx=10, pady=4, sticky="ew")
            entries[col_idx] = e

        def confirmar():
            nuevos = [entries[i].get() for i in range(len(headers))]
            if actualizar_callback:
                actualizar_callback(tabla_sql, fila[0], nuevos)
            fila_editando["idx"] = None
            mostrar_filas()
        CTkButton(cuerpo, text="Confirmar", fg_color="#007b3a", command=confirmar,
                  width=80).grid(row=idx, column=len(headers), padx=10, pady=4)

    def on_row_enter(event, idx):
        pass

    def on_row_leave(event, idx):
        pass

    def mostrar_filas():
        for widget in cuerpo.winfo_children():
            widget.destroy()
        btn_editar_ref.clear()
        btn_eliminar_ref.clear()

        for i in range(len(headers)):
            cuerpo.grid_columnconfigure(i, minsize=ANCHO_CELDA)

        for fila_idx, fila in enumerate(registros):
            valores_visibles = fila[1:] if ocultar_primer_campo else fila
            row_widgets = []
            for col_idx, valor in enumerate(valores_visibles):
                # CTkLabel con wraplength para que el texto se envuelva verticalmente
                l = CTkLabel(
                    cuerpo,
                    text=str(valor),
                    font=("Arial", 13),
                    anchor="nw",
                    justify="left",
                    wraplength=ANCHO_CELDA - 20,
                    text_color="#000000"
                )
                l.grid(row=fila_idx, column=col_idx,
                       padx=10, pady=8, sticky="nsew")
                row_widgets.append(l)

            def hacer_editar(idx=fila_idx):
                return lambda: editar_fila(idx)

            btn_editar = CTkButton(cuerpo, text="Editar", fg_color="#715a72", command=hacer_editar(fila_idx), width=80)
            btn_editar.grid(row=fila_idx, column=len(headers), padx=10, pady=8, sticky="ew")
            btn_editar_ref[fila_idx] = btn_editar

            # BOTÓN ELIMINAR
            if eliminar_callback:
                def hacer_eliminar(idx=fila_idx, id_registro=fila[0]):
                    def callback_eliminar():
                        try:
                            if callback_recargar_tabla:
                                callback_recargar_tabla()
                            else:
                                mostrar_filas()
                        except:
                            pass
                    return lambda: eliminar_callback(tabla_sql, id_registro, callback_eliminar)
                btn_eliminar = CTkButton(cuerpo, text="Eliminar", fg_color="#962d22", command=hacer_eliminar(fila_idx), width=80)
                btn_eliminar.grid(row=fila_idx, column=len(headers) + 1, padx=10, pady=8, sticky="ew")
                btn_eliminar_ref[fila_idx] = btn_eliminar

    mostrar_filas()
    return tabla


def ejecutar_update(sql, valores):
    """Función temporal para compatibilidad - usar db_conexion.ejecutar_update"""
    from db_conexion import ejecutar_update as db_ejecutar_update
    return db_ejecutar_update(sql, valores)


def actualizar_registro(tabla, id_valor, nuevos_valores):
    """Callback para actualizar un registro"""
    from db_conexion import ejecutar_update, conexion
    from tkinter import messagebox

    # Determinar el campo ID según la tabla
    campos_id = {
        "alumnos": "numero_control",
        "maestros": "matricula_maestro",
        "administradores": "matricula",
        "usuarios": "usuario",
        "Carreras": "id_carrera",
        "Materia": "id_materia",
        "registros": "id_registro",
        "salones": "id_salon",
        "Grupo": "id_grupo",
        "actividades": "id_actividad",
        "tipos_actividades": "id_tipo",
        "calificaciones_finales": "id_calificacion",
    }

    campo_id = campos_id.get(tabla, "id")

    # Construir UPDATE dinámico
    try:
        # Obtener las columnas de la tabla
        cursor = conexion.cursor()
        cursor.execute(f"DESCRIBE {tabla}")
        columnas = [col[0] for col in cursor.fetchall()]
        cursor.close()

        # Excluir el ID de los valores a actualizar
        columnas_sin_id = [col for col in columnas if col != campo_id]

        # Construir SET
        set_clause = ", ".join([f"{col}=%s" for col in columnas_sin_id])

        sql = f"UPDATE {tabla} SET {set_clause} WHERE {campo_id}=%s"

        ejecutar_update(sql, tuple(nuevos_valores) + (id_valor,))
        messagebox.showinfo("Éxito", "Registro actualizado correctamente")
        return True

    except Exception as e:
        messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
        return False


def verificar_dependencias(tabla, campo_id, id_valor):
    """
    Verifica si un registro tiene dependencias antes de eliminarlo.
    Retorna una lista de dicts con dependencias encontradas.
    """
    from db_conexion import ejecutar_select

    # Mapa de dependencias por tabla
    dependencias = {
        "alumnos": [
            ("registros", "numero_control", "inscripciones"),
            ("calificaciones_finales", "numero_control", "calificaciones finales"),
        ],
        "maestros": [
            ("Grupo", "matricula_maestro", "grupos asignados"),
        ],
        "administradores": [],
        "usuarios": [],
        "Carreras": [],
        "salones": [
            ("horario", "id_salon", "horarios asignados"),
        ],
        "Grupo": [
            ("registros", "id_grupo", "inscripciones"),
            ("calificaciones_finales", "id_grupo", "calificaciones finales"),
        ],
        "actividades": [],
        "calificaciones_finales": [],
        "calificaciones_actividades": [],
        "registros": [],
        "Materia": [],
    }

    deps_encontradas = []

    if tabla in dependencias:
        for (tabla_dep, campo_dep, nombre_legible) in dependencias[tabla]:
            try:
                resultado = ejecutar_select(
                    f"SELECT COUNT(*) FROM {tabla_dep} WHERE {campo_dep}=%s",
                    (id_valor,)
                )
                cantidad = resultado[0][0] if resultado else 0
                if cantidad > 0:
                    deps_encontradas.append({
                        "tabla": tabla_dep,
                        "campo": campo_dep,
                        "cantidad": cantidad,
                        "nombre": nombre_legible
                    })
            except Exception as e:
                print(f"Error verificando {tabla_dep}: {e}")

    return deps_encontradas


def eliminar_registro(tabla, id_valor, callback_recargar):
    """
    Elimina un registro después de verificar dependencias y pedir confirmación.
    Si hay dependencias, pregunta al usuario si desea eliminarlas también.
    """
    from db_conexion import ejecutar_delete
    from tkinter import messagebox

    campos_id = {
        "alumnos": "numero_control",
        "maestros": "matricula_maestro",
        "administradores": "matricula",
        "usuarios": "usuario",
        "Carreras": "id_carrera",
        "Materia": "id_materia",
        "registros": "id_registro",
        "salones": "id_salon",
        "Grupo": "id_grupo",
        "actividades": "id_actividad",
        "tipos_actividades": "id_tipo",
        "calificaciones_finales": "id_calificacion",
    }

    campo_id = campos_id.get(tabla, "id")

    # VERIFICAR DEPENDENCIAS
    dependencias = verificar_dependencias(tabla, campo_id, id_valor)

    if dependencias:
        # CONSTRUIR MENSAJE DE DEPENDENCIAS
        mensaje = f"El registro '{id_valor}' tiene las siguientes dependencias:\n\n"
        for dep in dependencias:
            mensaje += f"• {dep['cantidad']} {dep['nombre']}\n"

        mensaje += "\n¿Qué desea hacer?"

        # OFRECER OPCIONES
        respuesta = messagebox.askyesnocancel(
            "Dependencias detectadas",
            mensaje +
            "\n\nSí = Eliminar todo (incluyendo dependencias)\nNo = Cancelar eliminación"
        )

        if respuesta is None or respuesta == False:  # Cancel o No
            return

        # ELIMINAR EN CASCADA
        try:
            # Primero eliminar las dependencias
            for dep in dependencias:
                dep_campo_id = dep['campo']
                sql_dep = f"DELETE FROM {dep['tabla']} WHERE {dep_campo_id}=%s"
                ejecutar_delete(sql_dep, (id_valor,))

            # Luego eliminar el registro principal
            sql = f"DELETE FROM {tabla} WHERE {campo_id}=%s"
            exito = ejecutar_delete(sql, (id_valor,))

            if exito:
                messagebox.showinfo(
                    "Éxito",
                    f"Registro y {len(dependencias)} tipo(s) de dependencia(s) eliminados correctamente"
                )
                if callback_recargar:
                    callback_recargar()
            else:
                messagebox.showwarning(
                    "Advertencia", "No se encontró el registro a eliminar")

        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
            return

    # SIN DEPENDENCIAS - ELIMINACIÓN DIRECTA
    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Está seguro de eliminar el registro '{id_valor}'?\n\nEsta acción no se puede deshacer."
    )

    if not confirmar:
        return

    sql = f"DELETE FROM {tabla} WHERE {campo_id}=%s"

    try:
        exito = ejecutar_delete(sql, (id_valor,))
        if exito:
            messagebox.showinfo("Éxito", "Registro eliminado correctamente")
            if callback_recargar:
                callback_recargar()
        else:
            messagebox.showwarning(
                "Advertencia", "No se encontró el registro a eliminar")
    except Exception as e:
        messagebox.showerror("Error", f"Error al eliminar: {str(e)}")


pendientes_admin = []


def mostrar_dashboard(frame):
    limpiar_frame(frame)

    # ── HEADER ──────────────────────────────────────────────
    header = CTkFrame(frame, fg_color="transparent")
    header.pack(fill="x", padx=24, pady=(18, 6))
    CTkLabel(header, text="Panel de Administración",
             font=("Arial", 28, "bold"), text_color="#000000").pack(anchor="w")

    # ── TARJETAS DE ESTADÍSTICAS ─────────────────────────────
    stats_frame = CTkFrame(frame, fg_color="transparent")
    stats_frame.pack(fill="x", padx=24, pady=(6, 14))

    stats = [
        ("Alumnos",         "342", "#510054"),
        ("Maestros",        "45",  "#004235"),
        ("Administradores", "8",   "#1A3A8F"),
        ("Materias",        "67",  "#2D3250"),
        ("Grupos",          "24",  "#2D3250"),
        ("Inscripciones",   "318", "#2D3250"),
    ]

    for i, (label, valor, color) in enumerate(stats):
        stats_frame.grid_columnconfigure(i, weight=1)
        card = CTkFrame(stats_frame, fg_color=color, corner_radius=10)
        card.grid(row=0, column=i, padx=6, pady=4, sticky="ew")
        CTkLabel(card, text=label, font=("Arial", 13), text_color="white").pack(
            anchor="w", padx=12, pady=(10, 0))
        CTkLabel(card, text=valor, font=("Arial", 28, "bold"),
                 text_color="white").pack(anchor="w", padx=12, pady=(0, 10))

    # ── CARGA DE ÍCONOS ──────────────────────────────────────
    icono_alumnos = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/alumnos.png")),        size=(64, 64))
    icono_maestros = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/maestros.png")),       size=(64, 64))
    icono_materias = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/materias.png")),       size=(64, 64))
    icono_grupos = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/grupos.png")),         size=(64, 64))
    icono_inscripciones = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/inscripciones.png")), size=(64, 64))
    icono_admin = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/admin.png")),          size=(64, 64))
    icono_carreras = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/carreras.png")),       size=(64, 64))
    icono_calificaciones = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/calificaciones.png")), size=(64, 64))
    icono_actividades = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/actividades.png")),    size=(64, 64))
    icono_reportes = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/reportes.png")),       size=(64, 64))
    icono_usuario = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/usuario.png")),       size=(64, 64))


    # ── ÁREA PRINCIPAL: izquierda + derecha ──────────────────
    main_area = CTkFrame(frame, fg_color="transparent")
    main_area.pack(fill="both", expand=True, padx=24, pady=(0, 16))
    main_area.grid_columnconfigure(0, weight=0)
    main_area.grid_columnconfigure(1, weight=1)
    main_area.grid_rowconfigure(0, weight=1)

    # ── PANEL IZQUIERDO: calendario + eventos ────────────────
    left_panel = CTkFrame(main_area, fg_color="#ffffff",
                          corner_radius=12, width=270, height=540)
    left_panel.grid(row=0, column=0, sticky="nw", padx=(0, 16), pady=(100, 0))
    left_panel.grid_propagate(False)

    calendario(left_panel)

    eventos_frame = CTkFrame(left_panel, fg_color="#f0f4f8", corner_radius=10)
    eventos_frame.pack(fill="both", expand=True, padx=10, pady=(8, 10))

    CTkLabel(eventos_frame, text="🗓  Eventos",
             font=("Arial", 15, "bold"), text_color="#000000").pack(anchor="w", padx=10, pady=(8, 4))

    scroll_eventos = CTkScrollableFrame(eventos_frame, fg_color="transparent")
    scroll_eventos.pack(fill="both", expand=True, padx=4, pady=(0, 6))

    eventos = [
        "7 al 16 de enero: Actividades intersemestrales",
        "12 al 16 de enero: Curso de inducción de nuevo ingreso",
        "19 y 20 de enero: Inscripciones",
        "21 al 23 de enero: Reinscripciones",
        "26 de enero: Inicio de clases",
        "30 de marzo al 10 de abril: Periodo vacacional",
        "29 de mayo: Fin de clases",
        "1 al 3 de junio: Evaluación sumativa de complementación",
        "4 y 5 de junio: Entrega de calificaciones a servicios escolares",
        "8 de julio al 3 de agosto: Actividades intersemestrales",
        "6 al 31 de julio: Periodo vacacional",
    ]

    for ev in eventos:
        fila = CTkFrame(scroll_eventos, fg_color="transparent")
        fila.pack(fill="x", pady=3)
        CTkLabel(fila, text="●", text_color="#1A6B3C", font=(
            "Arial", 10)).pack(side="left", padx=(4, 6))
        CTkLabel(fila, text=ev, font=("Arial", 12), text_color="#000000",
                 anchor="w", justify="left", wraplength=190).pack(side="left", fill="x")

    # ── PANEL DERECHO: catálogos ─────────────────────────────
    right_panel = CTkFrame(main_area, fg_color="transparent")
    right_panel.grid(row=0, column=1, sticky="nsew")

    CTkLabel(right_panel, text="Catálogos del Sistema",
             font=("Arial", 20, "bold"), text_color="#000000").pack(anchor="w", pady=(0, 10))

    grid_frame = CTkFrame(right_panel, fg_color="transparent")
    grid_frame.pack(fill="both", expand=True)
    for col in range(3):
        grid_frame.grid_columnconfigure(col, weight=1)

    catalogos = [
        ("Alumnos","Gestión de estudiantes", lambda: mostrar_alumnos(frame),                      "#510054", icono_alumnos),
        ("Maestros","Gestión de docentes", lambda: mostrar_maestros(frame),                     "#004235", icono_maestros),
        ("Administradores","Gestión de administradores", lambda: mostrar_admin(frame),                        "#1A3A8F", icono_admin),
        ("Materias","Catálogo de materias", lambda: mostrar_materias(frame),                     "#2D3250", icono_materias),
        ("Grupos","Gestión de grupos", lambda: mostrar_grupos(frame),                       "#2D3250", icono_grupos),
        ("Carreras","Catálogo de carreras", lambda: mostrar_carreras(frame),                     "#2D3250", icono_carreras),
        ("Actividades","Gestión de actividades", lambda: mostrar_actividades(frame),                  "#2D3250", icono_actividades),
        ("Inscripciones","Registro de inscripciones", lambda: mostrar_inscripciones(frame),                "#2D3250", icono_inscripciones),
        ("Reportes","Generación de reportes", lambda: mostrar_reportes(frame),                     "#2D3250", icono_reportes),
        ("Calificaciones","Gestión de calificaciones",lambda: mostrar_calificaciones_finales(frame),       "#2D3250", icono_calificaciones),
        ("Usuarios","Gestión de las cuentas de usuarios", lambda: mostrar_usuarios(frame),                     "#2D3250", icono_usuario),

    ]

    for idx, (titulo_c, subtitulo_c, comando_c, color_c, icono_c) in enumerate(catalogos):
        r = idx // 3
        c = idx % 3
        grid_frame.grid_rowconfigure(r, weight=1)

        card = CTkFrame(grid_frame, fg_color=color_c,
                        corner_radius=12, cursor="hand2")
        card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
        card.bind("<Button-1>", lambda e, cmd=comando_c: cmd())

        lbl_icono = CTkLabel(card, text="", image=icono_c)
        lbl_icono.pack(pady=(16, 4))
        lbl_icono.bind("<Button-1>", lambda e, cmd=comando_c: cmd())

        lbl_titulo = CTkLabel(card, text=titulo_c, font=(
            "Arial", 15, "bold"), text_color="white")
        lbl_titulo.pack(pady=(0, 2))
        lbl_titulo.bind("<Button-1>", lambda e, cmd=comando_c: cmd())

        lbl_sub = CTkLabel(card, text=subtitulo_c, font=(
            "Arial", 11), text_color="#cccccc")
        lbl_sub.pack(pady=(0, 16))
        lbl_sub.bind("<Button-1>", lambda e, cmd=comando_c: cmd())


def mostrar_calendario_imagen(frame):
    limpiar_frame(frame)

    header = CTkFrame(frame, height=60, fg_color="#154b74")
    header.pack(fill="x", pady=10)

    CTkLabel(header, text="Calendario", text_color="white",
             font=("Arial", 26, "bold")).pack(pady=15)

    cuerpo = CTkFrame(frame, fg_color="#ffffff")
    cuerpo.pack(fill="both", expand=True, padx=20, pady=10)

    imagen_cal = CTkImage(light_image=Image.open(ruta_recurso(
        "carpeta_iconos/iconos_admin/calendario.png")), size=(600, 800))

    CTkLabel(cuerpo, text="", image=imagen_cal).pack(expand=True)


def mostrar_seccion_pendiente(frame, titulo):
    limpiar_frame(frame)

    header = CTkFrame(frame, height=60, fg_color="#154b74")
    header.pack(fill="x", pady=10)

    CTkLabel(header, text=titulo, text_color="white",
             font=("Arial", 26, "bold")).pack(pady=15)

    cuerpo = CTkFrame(frame, fg_color="#ffffff")
    cuerpo.pack(fill="both", expand=True, padx=20, pady=10)

    CTkLabel(
        cuerpo,
        text="Seccion pendiente de integrar con la nueva distribucion.",
        font=("Arial", 16, "bold"),
        text_color="#000000"
    ).pack(pady=30)


def mostrar_seccion_gestion(frame,titulo,color_header,color_menu,color_tabla,botones,headers,tabla_sql=None,header_text_color=None,registros_precargados=None):
    limpiar_frame(frame)

    CTkButton(frame, text="←", width=80, command=lambda: mostrar_dashboard(
        frame)).pack(anchor="w", padx=20, pady=10)

    header = CTkFrame(frame, height=60, fg_color=color_header)
    header.pack(fill="x")

    CTkLabel(header, text=titulo, text_color="white",
             font=("Arial", 26, "bold")).pack(pady=15)

    menu = CTkFrame(frame, fg_color=color_menu)
    menu.pack(fill="x", padx=20, pady=10)

    for i in range(len(botones)):
        menu.grid_columnconfigure(i, weight=1)

    barra_busqueda = CTkEntry(frame, corner_radius=20, border_width=1, border_color="#888888",
                              width=200, height=35, placeholder_text="Buscar...", placeholder_text_color="#888888")
    barra_busqueda.pack(fill="x", padx=20, pady=10)

    area_contenido = CTkFrame(frame)
    area_contenido.pack(fill="both", expand=True, padx=20, pady=10)

    def mostrar_tabla_base():
        limpiar_frame(area_contenido)

        # CARGAR DATOS REALES DE LA BD
        if tabla_sql == "Carreras":
            # Usar función personalizada para Carreras
            from funciones_datos import obtener_carreras_ordenadas
            try:
                registros = obtener_carreras_ordenadas()
            except Exception as e:
                print(f"Error cargando datos de Carreras: {e}")
                registros = []
        elif tabla_sql == "Materia":
            # Usar función personalizada para Materias
            from funciones_datos import obtener_materias_ordenadas
            try:
                registros = obtener_materias_ordenadas()
            except Exception as e:
                print(f"Error cargando datos de Materia: {e}")
                registros = []
        elif tabla_sql == "Grupo":
            # Usar función personalizada para Grupos
            from funciones_datos import obtener_grupos_ordenadas
            try:
                registros = obtener_grupos_ordenadas()
            except Exception as e:
                print(f"Error cargando datos de Grupo: {e}")
                registros = []
        elif tabla_sql:
            from db_conexion import ejecutar_select_todo
            try:
                registros = ejecutar_select_todo(tabla_sql)
            except Exception as e:
                print(f"Error cargando datos de {tabla_sql}: {e}")
                registros = []
        else:
            registros = []

        # Siempre mostrar los encabezados de la tabla
        # Crear callback de edición personalizado para Carreras
        editar_cb = None
        if tabla_sql == "Carreras":
            from formularios_edicion import editar_carreras
            def editar_cb(fila, callback_recargar):
                try:
                    # fila = (id_carrera, nombre_carrera, tipo_carrera, numero_semestres, clave_carrera)
                    # Pasar mostrar_tabla_base para que recargue toda la tabla
                    editar_carreras(area_contenido, fila[0], fila[1], fila[2], fila[3], fila[4], mostrar_tabla_base)
                except Exception as e:
                    print(f"Error en edición de carrera: {e}")
        elif tabla_sql == "Materia":
            from formularios_edicion import editar_materias
            from funciones_datos import obtener_id_carrera_por_nombre
            def editar_cb(fila, callback_recargar):
                try:
                    # fila = (id_materia, clave, nombre_materia, horas_semana, nombre_carrera, unidades)
                    # Necesito obtener id_carrera a partir del nombre de carrera
                    id_carrera = obtener_id_carrera_por_nombre(fila[4])
                    editar_materias(area_contenido, fila[0], fila[1], fila[2], fila[3], id_carrera, fila[5], mostrar_tabla_base)
                except Exception as e:
                    print(f"Error en edición de materia: {e}")
        elif tabla_sql == "Grupo":
            from formularios_edicion import editar_grupo
            def editar_cb(fila, callback_recargar):
                try:
                    # fila = (id_grupo, nombre_maestro, nombre_materia, cupo_maximo, periodo, anio, inscritos, horario, estado)
                    editar_grupo(area_contenido, fila[0], fila[1], fila[2], fila[3], fila[4], fila[5], fila[6], fila[7], fila[8], mostrar_tabla_base)
                except Exception as e:
                    print(f"Error en edición de grupo: {e}")
        
        crear_tabla_editable(
            area_contenido,
            headers,
            registros,
            tabla_sql or "pendiente",
            color_tabla,
            actualizar_callback=actualizar_registro if tabla_sql else None,
            eliminar_callback=eliminar_registro if tabla_sql else None,
            header_text_color=header_text_color,
            editar_callback=editar_cb,
            callback_recargar_tabla=mostrar_tabla_base if tabla_sql else None
        )
        
        # Mostrar mensaje si no hay registros
        if not registros:
            CTkLabel(
                area_contenido,
                text="No hay registros en la base de datos",
                font=("Arial", 15, "bold"),
                text_color="#000000"
            ).pack(pady=(10, 12))

    mostrar_tabla_base()

    for i, btn in enumerate(botones):
        comando_base = btn.get("comando")
        cmd = (lambda cb=comando_base: cb(area_contenido,
               mostrar_tabla_base)) if comando_base else mostrar_tabla_base
        CTkButton(menu, text=btn["texto"], fg_color=btn["color"], command=cmd).grid(
            row=0, column=i, padx=10, pady=10)


def seleccionar_csv():
    return filedialog.askopenfilename(title="Selecciona CSV", filetypes=[("CSV", "*.csv")])


def guardar_csv(nombre):
    return filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile=nombre)


def ejecutar_importacion(tabla, volver):
    """Importa datos desde un archivo CSV a la tabla especificada"""
    from formularios_bd import importar_csv
    from tkinter import filedialog

    ruta_csv = filedialog.askopenfilename(
        title=f"Seleccionar archivo CSV para importar a {tabla}",
        filetypes=[("CSV", "*.csv"), ("Todos los archivos", "*.*")]
    )

    if ruta_csv:
        try:
            importar_csv(tabla, ruta_csv)
            messagebox.showinfo(
                "Importación Exitosa", f"Datos importados correctamente a la tabla '{tabla}'")
            if volver:
                volver()
        except Exception as e:
            messagebox.showerror("Error de Importación",
                                 f"Error al importar: {str(e)}")


def ejecutar_exportacion(tabla, nombre):
    """Exporta datos de una tabla a un archivo CSV"""
    from formularios_bd import exportar_csv
    from tkinter import filedialog

    ruta_csv = filedialog.asksaveasfilename(
        title=f"Exportar {tabla} a CSV",
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv"), ("Todos los archivos", "*.*")],
        initialfile=nombre
    )

    if ruta_csv:
        try:
            exportar_csv(tabla, ruta_csv)
            messagebox.showinfo("Exportación Exitosa",
                                f"Datos de '{tabla}' exportados a {ruta_csv}")
        except Exception as e:
            messagebox.showerror("Error de Exportación",
                                 f"Error al exportar: {str(e)}")


def crear_respaldo_completo():
    """Respaldo completo de la base de datos en archivos CSV individuales por tabla."""
    from tkinter import filedialog
    from formularios_bd import exportar_csv
    import datetime
    import os

    # Seleccionar carpeta raíz donde se creará la carpeta del respaldo
    carpeta_raiz = filedialog.askdirectory(
        title="Seleccionar dónde crear la carpeta del respaldo")

    if not carpeta_raiz:
        return

    # Crear nombre de carpeta con formato: Respaldo_DB_YYYYMMDD_HHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_carpeta = f"Respaldo_DB_{timestamp}"

    # Ruta completa de la nueva carpeta
    ruta_carpeta = os.path.join(carpeta_raiz, nombre_carpeta)

    # Crear la carpeta
    try:
        os.makedirs(ruta_carpeta, exist_ok=False)
        print(f"✓ Carpeta de respaldo creada: {ruta_carpeta}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear la carpeta: {str(e)}")
        return

    tablas = [
        "alumnos", "maestros", "administradores", "usuarios",
        "Carreras", "Materia", "Grupo", "registros",
        "tipos_actividades", "salones",
        "calificaciones_finales", "calificaciones_actividades", "horario"
    ]

    exportados = 0
    errores = []

    for tabla in tablas:
        try:
            nombre_archivo = f"{tabla}.csv"
            ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
            exportar_csv(tabla, ruta_completa)
            exportados += 1
        except Exception as e:
            errores.append(f"{tabla}: {str(e)}")

    mensaje = f"✅ Respaldo completado:\n\n📁 Carpeta: {nombre_carpeta}\n📍 Ubicación: {carpeta_raiz}\n\n✓ Tablas exportadas: {exportados}/{len(tablas)}"

    if errores:
        mensaje += f"\n\n❌ Errores:\n" + "\n".join(errores)

    messagebox.showinfo("Respaldo Completo", mensaje)


def restaurar_desde_respaldo():
    """Restaura datos desde los CSV de respaldo más recientes en una carpeta."""
    from tkinter import filedialog
    from formularios_bd import importar_csv
    import os
    import glob

    # Primero seleccionar la carpeta raíz donde buscar carpetas de respaldo
    carpeta_raiz = filedialog.askdirectory(
        title="Seleccionar carpeta donde buscar respaldos")

    if not carpeta_raiz:
        return

    # Buscar carpetas que tengan el formato Respaldo_DB_*
    carpetas_respaldo = []
    for carpeta in os.listdir(carpeta_raiz):
        ruta_completa = os.path.join(carpeta_raiz, carpeta)
        if os.path.isdir(ruta_completa) and carpeta.startswith("Respaldo_DB_"):
            carpetas_respaldo.append((carpeta, ruta_completa))

    if not carpetas_respaldo:
        messagebox.showwarning(
            "No hay respaldos", "No se encontraron carpetas de respaldo (formato: Respaldo_DB_*)")
        return

    # Si hay múltiples carpetas, dejar elegir
    if len(carpetas_respaldo) == 1:
        carpeta_seleccionada = carpetas_respaldo[0][1]
    else:
        # Crear diálogo simple para seleccionar carpeta
        from tkinter import simpledialog

        nombres_carpetas = [c[0] for c in carpetas_respaldo]
        seleccion = simpledialog.askstring(
            "Seleccionar Respaldo",
            f"Se encontraron {len(carpetas_respaldo)} carpetas de respaldo:\n\n" +
            "\n".join(nombres_carpetas) +
            "\n\nEscribe el nombre exacto de la carpeta que deseas restaurar:",
            initialvalue=nombres_carpetas[0]
        )

        if not seleccion:
            return

        # Encontrar la ruta completa
        for nombre, ruta in carpetas_respaldo:
            if nombre == seleccion:
                carpeta_seleccionada = ruta
                break

    # Buscar todos los archivos CSV en la carpeta seleccionada
    archivos_csv = glob.glob(os.path.join(carpeta_seleccionada, "*.csv"))

    if not archivos_csv:
        messagebox.showwarning(
            "No hay archivos", f"No se encontraron archivos CSV en la carpeta:\n{carpeta_seleccionada}")
        return

    importados = 0
    errores = []

    for archivo in archivos_csv:
        try:
            # Obtener nombre de la tabla desde el nombre del archivo
            nombre_archivo = os.path.basename(archivo)
            # El formato es: tabla.csv
            nombre_tabla = nombre_archivo.replace(".csv", "")

            importar_csv(nombre_tabla, archivo)
            importados += 1
        except Exception as e:
            errores.append(f"{nombre_archivo}: {str(e)}")

    mensaje = f"✅ Restauración completada:\n\n📁 Carpeta: {os.path.basename(carpeta_seleccionada)}\n📍 Ubicación: {carpeta_raiz}\n\n✓ Archivos importados: {importados}/{len(archivos_csv)}"

    if errores:
        mensaje += f"\n\n❌ Errores:\n" + "\n".join(errores)

    messagebox.showinfo("Restauración Completada", mensaje)


def mostrar_alumnos(frame):

    def registrar(area, volver):
        mostrar_form_registro_alumno(area, volver)

    def importar(area, volver):
        ejecutar_importacion("alumnos", volver)

    def exportar(area, volver):
        ejecutar_exportacion("alumnos", "alumnos.csv")

    botones = [
        {"texto": "Registrar alumno", "color": "#552157", "comando": registrar},
        {"texto": "Importar CSV", "color": "#552157", "comando": importar},
        {"texto": "Exportar CSV", "color": "#552157", "comando": exportar},
    ]

    headers = ["Número de Control", "Nombre", "Apellido Paterno",
               "Apellido Materno", "Correo", "Carrera", "Semestre", "Estado"]

    mostrar_seccion_gestion(frame, "Gestión de Alumnos", "#510054",
                            "#fafafa", "#9880a0", botones, headers, "alumnos")


def mostrar_maestros(frame):

    def registrar(area, volver):
        mostrar_form_registro_maestro(area, volver)

    def importar(area, volver):
        ejecutar_importacion("maestros", volver)

    def exportar(area, volver):
        ejecutar_exportacion("maestros", "maestros.csv")

    botones = [
        {"texto": "Registrar maestro", "color": "#022A22", "comando": registrar},
        {"texto": "Importar CSV", "color": "#022A22", "comando": importar},
        {"texto": "Exportar CSV", "color": "#022A22", "comando": exportar},
    ]

    headers = ["Matrícula", "Nombre", "Apellido Paterno", "Apellido Materno", "Correo",
               "Estatus", "Estudios", "Perfil", "Carga Académica", "Contrato", "Cédula"]

    mostrar_seccion_gestion(frame, "Gestión de Maestros", "#004235",
                            "#ffffff", "#6F8A90", botones, headers, "maestros")


def mostrar_admin(frame):
    def registrar(area, volver):
        mostrar_form_registro_administrador(area, volver)

    def importar(area, volver):
        ejecutar_importacion("administradores", volver)

    def exportar(area, volver):
        ejecutar_exportacion("administradores", "administradores.csv")

    botones = [
        {"texto": "Registrar administrador",
            "color": "#610139", "comando": registrar},
        {"texto": "Importar CSV", "color": "#610139", "comando": importar},
        {"texto": "Exportar CSV", "color": "#610139", "comando": exportar},
    ]
    headers = ["Matrícula", "Nombre", "Apellido Paterno", "Apellido Materno"]
    mostrar_seccion_gestion(frame, "Gestión de Administradores", "#610139",
                            "#ffffff", "#9880a0", botones, headers, "administradores")


def mostrar_carreras(frame):
    def registrar(area,volver):
        mostrar_form_registro_carrera(area,volver)
    def importar(area,volver):
        ejecutar_importacion("Carreras",volver)

    def exportar(area,volver):
        ejecutar_exportacion("Carreras","Carreras.csv")

    botones = [
        {"texto": "Registrar Carrera nueva",
            "color": "#43000E", "comando": registrar},
        {"texto": "Importar CSV", "color": "#43000E", "comando": importar},
        {"texto": "Exportar CSV", "color": "#43000E", "comando": exportar},
    ]
    headers = ["Nombre de la Carrera", "Tipo", "Semestres", "Clave"]
    mostrar_seccion_gestion(frame, "Gestión de Carreras", "#43000E", "#ffffff",
                            "#d1c4b3", botones, headers, "Carreras", header_text_color="white")


def mostrar_materias(frame):
    def registrar(area, volver):
        mostrar_form_registro_materia(area, volver)

    def importar(area, volver):
        ejecutar_importacion("materias", volver)

    def exportar(area, volver):
        ejecutar_exportacion("materias", "materias.csv")

    botones = [
        {"texto": "Registrar materia", "color": "#510113", "comando": registrar},
        {"texto": "Importar CSV", "color": "#510113", "comando": importar},
        {"texto": "Exportar CSV", "color": "#510113", "comando": exportar},
    ]

    headers = ["Clave", "Nombre Materia", "Carrera", "Horas a la semana", "Unidades"]

    mostrar_seccion_gestion(frame, "Gestión de Materias", "#761127", "#ffffff", "#9A0000", botones, headers, tabla_sql="Materia", header_text_color="white")

def mostrar_grupos(frame):

    def registrar(area, volver):
        mostrar_form_registro_grupo(area, volver)

    def importar(area,volver):
        ejecutar_importacion("Grupo",volver)

    def exportar(area,volver):
        ejecutar_exportacion("Grupo","Grupo.csv")

    botones = [
        {"texto": "Crear grupo", "color": "#184c73", "comando": registrar},
        {"texto": "Importar CSV", "color": "#184c73", "comando": importar},
        {"texto": "Exportar CSV", "color": "#184c73", "comando": exportar},
    ]

    # Headers sin el ID (que se salta): nombre_maestro, nombre_materia, cupo_maximo, periodo, anio, inscritos, horario, estado
    headers = ["Maestro", "Materia", "Cupo máximo", "Período", "Año", "Inscritos", "Horario", "Estado"]

    mostrar_seccion_gestion(frame,"Gestión de Grupos","#1f6aa5","#ffffff","#8fb1cb",botones,headers,"Grupo",header_text_color="white")

def mostrar_inscripciones(frame):

    def registrar(area, volver):
        mostrar_form_registro_inscripcion(area, volver)

    def importar(area, volver):
        ejecutar_importacion("registros", volver)

    def exportar(area, volver):
        ejecutar_exportacion("registros", "inscripciones.csv")

    botones = [
        {"texto": "Inscribir alumno", "color": "#A64500", "comando": registrar},
        {"texto": "Importar CSV", "color": "#A64500", "comando": importar},
        {"texto": "Exportar CSV", "color": "#A64500", "comando": exportar},
    ]

    headers = ["Alumno", "Número de Control", "Grupo",
               "Materia", "Estatus", "Tipo de inscripción"]

    mostrar_seccion_gestion(frame, "Inscripciones", "#7A3500",
                            "#ffffff", "#C75C00", botones, headers, "registros")


def mostrar_usuarios(frame):
    """Mostrar tabla de usuarios con datos de Cuentas, Roles y alumnos/maestros/administradores"""
   
    def importar(area, volver):
        ejecutar_importacion("Cuentas", volver)

    def exportar(area, volver):
        ejecutar_exportacion("Cuentas", "usuarios.csv")

    botones = [
        {"texto": "Importar CSV", "color": "#2D3250", "comando": importar},
        {"texto": "Exportar CSV", "color": "#2D3250", "comando": exportar},
    ]

    headers = ["Usuario", "Contraseña", "Rol"]

    limpiar_frame(frame)

    CTkButton(frame, text="←", width=80, command=lambda: mostrar_dashboard(
        frame)).pack(anchor="w", padx=20, pady=10)

    header = CTkFrame(frame, height=60, fg_color="#2D3250")
    header.pack(fill="x")

    CTkLabel(header, text="Gestión de Usuarios", text_color="white",
             font=("Arial", 26, "bold")).pack(pady=15)

    menu = CTkFrame(frame, fg_color="#ffffff")
    menu.pack(fill="x", padx=20, pady=10)

    for i in range(len(botones)):
        menu.grid_columnconfigure(i, weight=1)

    area_contenido = CTkFrame(frame)
    area_contenido.pack(fill="both", expand=True, padx=20, pady=10)

    def mostrar_tabla_usuarios():
        limpiar_frame(area_contenido)

        try:
            sql = """
            SELECT 
                c.id_cuenta,
                COALESCE(a.numero_control, m.matricula, adm.matricula) AS usuario,
                c.password,
                r.nombre AS rol
            FROM Cuentas c
            JOIN Roles r ON c.id_rol = r.id_rol
            LEFT JOIN Alumno a ON a.id_cuenta = c.id_cuenta
            LEFT JOIN Maestro m ON m.id_cuenta = c.id_cuenta
            LEFT JOIN Administrador adm ON adm.id_cuenta = c.id_cuenta
            """
            registros = ejecutar_select(sql)
        except Exception as e:
            print(f"Error cargando usuarios: {e}")
            registros = []

        crear_tabla_editable(
            area_contenido,
            headers,
            registros,
            "Cuentas",
            color_tabla="#6d8fa3",
            actualizar_callback=actualizar_registro,
            eliminar_callback=eliminar_registro,
            header_text_color="white",
            ocultar_primer_campo=True
        )

        if not registros:
            CTkLabel(area_contenido, text="No hay registros en la base de datos",
                     font=("Arial", 15, "bold"), text_color="#000000").pack(pady=(10, 12))

    mostrar_tabla_usuarios()

    for i, btn in enumerate(botones):
        comando_base = btn.get("comando")
        cmd = (lambda cb=comando_base: cb(area_contenido, mostrar_tabla_usuarios)) if comando_base else mostrar_tabla_usuarios
        CTkButton(menu, text=btn["texto"], fg_color=btn["color"], command=cmd).grid(
            row=0, column=i, padx=10, pady=10)


# === ACTIVIDADES ===
def mostrar_actividades(frame):
    limpiar_frame(frame)

    CTkButton(frame, text="←", width=80, command=lambda: mostrar_dashboard(
        frame)).pack(anchor="w", padx=20, pady=10)

    header = CTkFrame(frame, height=60, fg_color="#1f6aa5")
    header.pack(fill="x")

    CTkLabel(header, text="Gestión de Actividades", text_color="white",
             font=("Arial", 26, "bold")).pack(pady=15)

    menu = CTkFrame(frame, fg_color="#ffffff")
    menu.pack(fill="x", padx=20, pady=(10, 6))

    area_filtros = CTkFrame(frame, fg_color="transparent")
    area_filtros.pack(fill="x", padx=20, pady=(0, 10))

    CTkLabel(area_filtros, text="Filtrar por grupo", font=("Arial", 14, "bold"),
             text_color="#000000").grid(row=0, column=0, padx=(0, 10), pady=6, sticky="w")

    grupos = ["Todos"] + obtener_lista("grupos", "id_grupo")
    combo_grupo = CTkComboBox(
        area_filtros, values=grupos, width=220, state="readonly")
    combo_grupo.set(grupos[0])
    combo_grupo.grid(row=0, column=1, padx=10, pady=6, sticky="w")

    area_contenido = CTkFrame(frame)
    area_contenido.pack(fill="both", expand=True, padx=20, pady=10)

    def abrir_nuevo_tipo(area, volver):
        mostrar_form_registro_tipo_actividad(area, volver)

    def registrar_actividad(area, volver):
        mostrar_form_actividad(area, volver)

    def importar(area, volver):
        ejecutar_importacion("actividades", volver)

    def exportar(area, volver):
        ejecutar_exportacion("actividades", "actividades.csv")

    botones = [
        {"texto": "Nuevo tipo de actividad",
            "color": "#1f6aa5", "comando": abrir_nuevo_tipo},
        {"texto": "Registrar Actividad", "color": "#1f6aa5",
            "comando": registrar_actividad},
        {"texto": "Importar CSV", "color": "#1f6aa5", "comando": importar},
        {"texto": "Exportar CSV", "color": "#1f6aa5", "comando": exportar},
    ]

    for i, btn in enumerate(botones):
        CTkButton(
            menu,
            text=btn["texto"],
            fg_color=btn["color"],
            command=(lambda cb=btn["comando"]: cb(
                area_contenido, mostrar_tabla_actividades))
        ).grid(row=0, column=i, padx=10, pady=10)

    headers = ["Tipo de Actividad", "Unidad",
               "Grupo", "Materia", "Ponderacion", "Detalles"]

    def cargar_tabla(grupo_seleccionado=None):
        limpiar_frame(area_contenido)

        try:
            if grupo_seleccionado and grupo_seleccionado != "Todos":
                registros = ejecutar_select(
                    "SELECT id_actividad, tipo_actividad, unidad, id_grupo, materia, ponderacion, detalles FROM actividades WHERE id_grupo=%s ORDER BY id_actividad DESC",
                    (grupo_seleccionado,)
                )
            else:
                registros = ejecutar_select(
                    "SELECT id_actividad, tipo_actividad, unidad, id_grupo, materia, ponderacion, detalles FROM actividades ORDER BY id_actividad DESC"
                )
        except Exception as e:
            print(f"Error cargando actividades: {e}")
            registros = []

        crear_tabla_editable(
            area_contenido,
            headers,
            registros,
            "actividades",
            color_tabla="#8fb1cb",
            actualizar_callback=actualizar_registro,
            eliminar_callback=eliminar_registro,
            header_text_color="white",
            ocultar_primer_campo=True,
        )

        if not registros:
            CTkLabel(area_contenido, text="No hay registros en la base de datos", font=(
                "Arial", 15, "bold"), text_color="#000000").pack(pady=(10, 12))

    def mostrar_tabla_actividades():
        cargar_tabla(combo_grupo.get())

    combo_grupo.bind("<<ComboboxChanged>>",
                     lambda event: mostrar_tabla_actividades())

    mostrar_tabla_actividades()


def mostrar_calificaciones_finales(frame):
    def registrar(area, volver):
        mostrar_form_registro_calificacion_final(area, volver)

    def importar(area, volver):
        ejecutar_importacion("calificaciones_finales", volver)

    def exportar(area, volver):
        ejecutar_exportacion("calificaciones_finales",
                             "calificaciones_finales.csv")

    botones = [
        {"texto": "Registrar calificación",
            "color": "#2b4d7a", "comando": registrar},
        {"texto": "Importar CSV", "color": "#2b4d7a", "comando": importar},
        {"texto": "Exportar CSV", "color": "#2b4d7a", "comando": exportar},
    ]

    headers = ["Numero de control", "Alumno", "Grupo",
               "Materia", "Periodo", "Calificación Final", ]

    mostrar_seccion_gestion(
        frame,
        "Gestión de Calificaciones Finales",
        "#2b4d7a",
        "#ffffff",
        "#8fb1cb",
        botones,
        headers,
        "calificaciones_finales",
        header_text_color="white"
    )





def mostrar_solicitudes(frame, datos=None):
    limpiar_frame(frame)

    CTkLabel(frame, text="Solicitudes Pendientes",
             font=("Arial", 24, "bold"), text_color="#000000").pack(anchor="w", padx=30, pady=(0, 4))

    scroll = CTkScrollableFrame(frame, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=20, pady=(0, 4))

    if datos is None:
        datos = [
            {
                "nombre":      "Juan Pérez",
                "matricula":   "21490001",
                "estado":      "ALTA",
                "titulo":      "Recuperación de Contraseña",
                "descripcion": "El alumno Juan Pérez solicita recuperar su contraseña",
            },
            {
                "nombre":      "Carlos Ruiz",
                "matricula":   "21490032",
                "estado":      "ALTA",
                "titulo":      "Cita Programada para el 20 de mayo a las 10:00 AM",
                "descripcion": "El alumno Carlos Ruiz solicita una cita programada para el 20 de mayo a las 10:00 AM",
            },
            {
                "nombre":      "Carlos González",
                "matricula":   "M00245",
                "estado":      "MEDIA",
                "titulo":      "Nuevo Tipo de Actividad",
                "descripcion": "El alumno Carlos González solicita un nuevo tipo de actividad",
            },
            {
                "nombre":      "María López",
                "matricula":   "M00189",
                "estado":      "BAJA",
                "titulo":      "Modificación de Grupo",
                "descripcion": "La alumna María López solicita una modificación de grupo",
            },
        ]

    colores_estado = {
        "ALTA":  {"borde": "#e53935", "etiqueta": "#fdecea", "texto": "#e53935"},
        "MEDIA": {"borde": "#f9a825", "etiqueta": "#fffde7", "texto": "#f57f17"},
        "BAJA":  {"borde": "#1565c0", "etiqueta": "#e3f2fd", "texto": "#1565c0"},
    }

    if not datos:
        CTkLabel(scroll, text="No hay solicitudes pendientes.",
                 font=("Arial", 14), text_color="#888888").pack(pady=20)
        return

    for sol in datos:
        estado = sol.get("estado", "BAJA").strip().upper()
        c = colores_estado.get(estado, colores_estado["BAJA"])

        tarjeta = CTkFrame(scroll, fg_color="#ffffff", corner_radius=10,
                           border_width=2, border_color=c["borde"])
        tarjeta.pack(fill="x", pady=4, padx=4)
        tarjeta.grid_columnconfigure(1, weight=1)

        franja = CTkFrame(
            tarjeta, fg_color=c["borde"], width=6, corner_radius=0)
        franja.grid(row=0, column=0, sticky="ns")

        contenido = CTkFrame(tarjeta, fg_color="transparent")
        contenido.grid(row=0, column=1, sticky="ew", padx=12, pady=0)

        fila_top = CTkFrame(contenido, fg_color="transparent")
        fila_top.pack(fill="x")

        CTkLabel(fila_top, text=sol.get("titulo", "Sin título"),
                 font=("Arial", 13, "bold"), text_color="#000000").pack(side="left", pady=(0, 2))

        etiqueta = CTkFrame(fila_top, fg_color=c["etiqueta"], corner_radius=4)
        etiqueta.pack(side="right", padx=(0, 4))
        CTkLabel(etiqueta, text=f"PRIORIDAD {estado}",
                 font=("Arial", 9, "bold"), text_color=c["texto"]).pack(padx=7, pady=1)

        CTkLabel(contenido,
                 text=f"👤  {sol.get('nombre', '—')}   •   Matrícula / No. Control: {sol.get('matricula', '—')}",
                 font=("Arial", 10), text_color="#333333").pack(anchor="w", pady=(2, 1))

        CTkLabel(contenido, text=sol.get("descripcion", " "),
                 font=("Arial", 10), text_color="#444444",
                 anchor="w", justify="left", wraplength=900).pack(anchor="w", pady=(0, 2))

        CTkButton(contenido, text="✔  Marcar como Completada",
                  fg_color="#2e7d32", hover_color="#1b5e20",
                  text_color="white", corner_radius=8,
                  width=220, height=26).pack(anchor="w", pady=(0, 0))


def mostrar_reporte_grupal(frame, id_grupo):
    limpiar_frame(frame)

    CTkButton(frame, text="←", width=80, command=lambda: mostrar_reportes(
        frame)).pack(anchor="w", padx=20, pady=10)

    header = CTkFrame(frame, height=60, fg_color="#154b74")
    header.pack(fill="x")

    CTkLabel(header, text="Reporte de Grupo", text_color="white",
             font=("Arial", 26, "bold")).pack(pady=15)

    menu = CTkFrame(frame, fg_color="#ffffff")
    menu.pack(fill="x", padx=20, pady=10)

    area_contenido = CTkFrame(frame)
    area_contenido.pack(fill="both", expand=True, padx=20, pady=10)


def crear_tabla_reportes(contenedor, registros, frame_principal):
    """Función interna para crear tabla. Recibe frame_principal por referencia.
    Nota: El primer elemento de cada registro es id_grupo (oculto), comenzamos a mostrar desde índice 1.
    """
    headers = ["Grupo", "Materia", "Maestro", "Período", "Año", "Estado"]
    # Anchos predefinidos para cada columna
    column_widths = [60, 150, 270, 150, 60, 100]

    tabla = CTkFrame(contenedor)
    tabla.pack(fill="both", expand=True)

    encabezado = CTkFrame(tabla, fg_color="#5d91b9")
    encabezado.pack(fill="x")
    color_texto = color_texto_legible("#fafafa")
    for i, h in enumerate(headers):
        encabezado.grid_columnconfigure(i, weight=0, minsize=column_widths[i])
        CTkLabel(encabezado, text=h, text_color=color_texto, font=("Arial", 14, "bold"), anchor="center",
                 justify="center", width=column_widths[i]).grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

    cuerpo = CTkFrame(tabla, fg_color="transparent")
    cuerpo.pack(fill="both", expand=True)

    fila_seleccionada = {"idx": None}
    row_frames = {}

    def seleccionar_fila(idx):
        # Deseleccionar fila anterior si existe
        if fila_seleccionada["idx"] is not None:
            prev_frame = row_frames.get(fila_seleccionada["idx"])
            if prev_frame:
                prev_frame.configure(fg_color="transparent")

        # Seleccionar nueva fila
        fila_seleccionada["idx"] = idx
        nueva_frame = row_frames.get(idx)
        if nueva_frame:
            nueva_frame.configure(fg_color="#e0e7ff")  # Azul claro

        # Ejecutar mostrar_reporte_grupal con el frame principal
        if registros and idx < len(registros):
            id_grupo = registros[idx][0]  # Primer elemento es el id_grupo
            mostrar_reporte_grupal(frame_principal, id_grupo)

    def on_enter(idx):
        """Evento cuando el cursor entra en una fila"""
        frame = row_frames.get(idx)
        if frame and fila_seleccionada["idx"] != idx:
            frame.configure(fg_color="#f5f5f5")  # Gris muy claro

    def on_leave(idx):
        """Evento cuando el cursor sale de una fila"""
        frame = row_frames.get(idx)
        if frame:
            if fila_seleccionada["idx"] == idx:
                # Mantiene el color de selección
                frame.configure(fg_color="#e0e7ff")
            else:
                # Vuelve a transparente
                frame.configure(fg_color="transparent")

    def mostrar_filas():
        for widget in cuerpo.winfo_children():
            widget.destroy()
        row_frames.clear()
        fila_seleccionada["idx"] = None

        # Si no hay registros, mostrar mensaje
        if not registros:
            CTkLabel(
                cuerpo,
                text="No hay registros en la base de datos",
                font=("Arial", 15, "bold"),
                text_color="#000000"
            ).pack(pady=(10, 12))
            return

        for fila_idx, fila in enumerate(registros):
            # Frame contenedor de la fila con eventos de mouse
            frame_fila = CTkFrame(
                cuerpo, fg_color="transparent", corner_radius=6)
            frame_fila.pack(fill="x", padx=4, pady=2)

            row_frames[fila_idx] = frame_fila

            # Crear frame interno para las celdas
            inner_frame = CTkFrame(frame_fila, fg_color="transparent")
            inner_frame.pack(fill="x", expand=True)

            for col_idx, valor in enumerate(headers):
                inner_frame.grid_columnconfigure(
                    col_idx, weight=0, minsize=column_widths[col_idx])

            # Crear labels para cada celda (comenzar desde índice 1, saltando id_grupo)
            labels = []
            # ← Comienza desde índice 1
            for col_idx, valor in enumerate(fila[1:]):
                l = CTkLabel(inner_frame, text=str(valor), font=("Arial", 13), anchor="center", justify="center",
                             wraplength=column_widths[col_idx]-20, text_color="#000000", width=column_widths[col_idx])
                l.grid(row=0, column=col_idx, padx=10, pady=8, sticky="nsew")
                labels.append(l)

            # Vincular eventos de selección y hover a todos los elementos de la fila
            def hacer_seleccionar(idx=fila_idx):
                return lambda: seleccionar_fila(idx)

            frame_fila.bind("<Button-1>", lambda e,
                            idx=fila_idx: seleccionar_fila(idx))
            frame_fila.bind("<Enter>", lambda e, idx=fila_idx: on_enter(idx))
            frame_fila.bind("<Leave>", lambda e, idx=fila_idx: on_leave(idx))

            inner_frame.bind("<Button-1>", lambda e,
                             idx=fila_idx: seleccionar_fila(idx))
            inner_frame.bind("<Enter>", lambda e, idx=fila_idx: on_enter(idx))
            inner_frame.bind("<Leave>", lambda e, idx=fila_idx: on_leave(idx))

            for lbl in labels:
                lbl.bind("<Button-1>", lambda e,
                         idx=fila_idx: seleccionar_fila(idx))
                lbl.bind("<Enter>", lambda e, idx=fila_idx: on_enter(idx))
                lbl.bind("<Leave>", lambda e, idx=fila_idx: on_leave(idx))

    mostrar_filas()


def mostrar_reportes(frame):
    limpiar_frame(frame)

    CTkButton(frame, text="←", width=80, command=lambda: mostrar_dashboard(
        frame)).pack(anchor="w", padx=20, pady=10)

    header = CTkFrame(frame, height=60, fg_color="#154b74")
    header.pack(fill="x")

    CTkLabel(header, text="Reportes", text_color="white",
             font=("Arial", 26, "bold")).pack(pady=15)

    menu = CTkFrame(frame, fg_color="#ffffff")
    menu.pack(fill="x", padx=20, pady=10)

    CTkLabel(menu, text="Filtrar por:", font=("Arial", 20, "bold"),
             text_color="#000000").grid(row=0, column=0, padx=10, pady=10, sticky="w")

    area_contenido = CTkFrame(frame)
    area_contenido.pack(fill="both", expand=True, padx=20, pady=10)

    """registros=[(1,"1J1-A", "Matemáticas", "Dr. Juan Pérez", "Enero-Junio", "2024", "Activo"),
              (2,"1J4-B", "Física", "Dra. María López", "Agosto-Diciembre", "2024", "Inactivo"),
              (3,"1J3-C", "Química", "Dr. Carlos Ruiz", "Enero-Junio", "2023", "Activo"),
              (4,"2J1-D", "Biología", "Dra. Ana Gómez", "Agosto-Diciembre", "2023", "Inactivo")]"""

    def recargar_tabla_con_filtros():
        # Recarga la tabla según los filtros seleccionados
        # from db_conexion import ejecutar_select

        periodo = filtro_periodo.get()
        año = filtro_año.get()

        # Construir consulta SQL dinámicamente
        sql = """SELECT 
            g.id_grupo,
            g.clave_grupo,
            m.nombre_materia,
            CONCAT(ma.nombre_maestro, ' ', ma.apellido_paterno, ' ', ma.apellido_materno) as maestro,
            g.periodo, 
            g.years, 
            g.estado 
        FROM grupos g
        LEFT JOIN materias m ON g.id_materia = m.id_materia
        LEFT JOIN maestros ma ON g.id_maestro = ma.id_maestro
        WHERE 1=1"""
        params = []

        if periodo and periodo != "Período":
            sql += " AND g.periodo=%s"
            params.append(periodo)

        if año and año != "Año":
            sql += " AND g.years=%s"
            params.append(año)

        try:
            registros = ejecutar_select(sql, tuple(params) if params else None)
        except Exception as e:
            print(f"Error cargando grupos desde BD: {e}")
            registros = []

        # Limpiar área de contenido y recrear tabla
        limpiar_frame(area_contenido)
        crear_tabla_reportes(area_contenido, registros, frame)

    # Crear OptionMenus con comando para filtrar
    filtro_periodo = CTkOptionMenu(menu, values=["Período", "Enero-Junio", "Agosto-Diciembre",
                                   "Verano"], corner_radius=20, command=lambda x: recargar_tabla_con_filtros())
    filtro_periodo.set("Período")
    filtro_periodo.grid(row=1, column=0, padx=10, pady=10)

    filtro_año = CTkOptionMenu(menu, values=["Año"] + [str(a) for a in range(
        2015, 2026)], corner_radius=20, command=lambda x: recargar_tabla_con_filtros())
    filtro_año.set("Año")
    filtro_año.grid(row=1, column=1, padx=10, pady=10)

    # Cargar datos iniciales
    recargar_tabla_con_filtros()
