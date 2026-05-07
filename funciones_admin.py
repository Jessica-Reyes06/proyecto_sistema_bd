from tkinter import messagebox
from customtkinter import *
from PIL import Image
from config_principal import calendario, limpiar_frame
from formularios_bd import *
import os
import sys

def ruta_recurso(ruta_relativa):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, ruta_relativa)

def color_texto_legible(color_hex):
    if not isinstance(color_hex, str) or not color_hex.startswith("#") or len(color_hex) != 7:
        return "white"

    rojo = int(color_hex[1:3], 16)
    verde = int(color_hex[3:5], 16)
    azul = int(color_hex[5:7], 16)
    luminosidad = (0.299 * rojo) + (0.587 * verde) + (0.114 * azul)
    return "black" if luminosidad > 160 else "white"

def crear_tabla_editable(parent, headers, registros, tabla_sql, color_tabla="#e0e0e0", actualizar_callback=None, eliminar_callback=None):

    tabla = CTkFrame(parent)
    tabla.pack(fill="both", expand=True)

    encabezado = CTkFrame(tabla, fg_color=color_tabla)
    encabezado.pack(fill="x")
    color_texto = color_texto_legible(color_tabla)
    for i, h in enumerate(headers):
        encabezado.grid_columnconfigure(i, weight=1)
        CTkLabel(encabezado, text=h, text_color=color_texto, font=("Arial", 14, "bold"), anchor="w", justify="left").grid(row=0, column=i, padx=10, pady=10, sticky="w")
    encabezado.grid_columnconfigure(len(headers), weight=1)
    encabezado.grid_columnconfigure(len(headers) + 1, weight=1)

    cuerpo = CTkFrame(tabla)
    cuerpo.pack(fill="both", expand=True)

    fila_editando = {"idx": None}
    entries = {}
    btn_editar_ref = {}
    btn_eliminar_ref = {}

    def editar_fila(idx):
        fila = registros[idx]
        for widget in cuerpo.grid_slaves(row=idx):
            widget.destroy()
        for col_idx, valor in enumerate(fila):
            e = CTkEntry(cuerpo)
            e.insert(0, str(valor))
            e.grid(row=idx, column=col_idx, padx=10, pady=4, sticky="ew")
            entries[col_idx] = e
        def confirmar():
            nuevos = [entries[i].get() for i in range(len(headers))]
            if actualizar_callback:
                actualizar_callback(tabla_sql, fila[0], nuevos)
            fila_editando["idx"] = None
            mostrar_filas()
        CTkButton(cuerpo, text="Confirmar", fg_color="#007b3a", command=confirmar).grid(row=idx, column=len(headers), padx=10, pady=4)

    def on_row_enter(event, idx):
        btn = btn_editar_ref.get(idx)
        if btn:
            btn.grid()
        btn_elim = btn_eliminar_ref.get(idx)
        if btn_elim:
            btn_elim.grid()

    def on_row_leave(event, idx):
        btn = btn_editar_ref.get(idx)
        if btn:
            btn.grid_remove()
        btn_elim = btn_eliminar_ref.get(idx)
        if btn_elim:
            btn_elim.grid_remove()

    def mostrar_filas():
        for widget in cuerpo.winfo_children():
            widget.destroy()
        btn_editar_ref.clear()
        btn_eliminar_ref.clear()
        for fila_idx, fila in enumerate(registros):
            row_widgets = []
            for col_idx, valor in enumerate(fila):
                l = CTkLabel(cuerpo, text=str(valor), font=("Arial", 13), anchor="w", justify="left", wraplength=200, text_color="#000000")
                l.grid(row=fila_idx, column=col_idx, padx=10, pady=4, sticky="ew")
                row_widgets.append(l)
            def hacer_editar(idx=fila_idx):
                return lambda: editar_fila(idx)
            btn_editar = CTkButton(cuerpo, text="Editar", fg_color="#715a72", command=hacer_editar(fila_idx))
            btn_editar.grid(row=fila_idx, column=len(headers), padx=10, pady=4)
            btn_editar.grid_remove()
            btn_editar_ref[fila_idx] = btn_editar

            # BOTÓN ELIMINAR (NUEVO)
            if eliminar_callback:
                def hacer_eliminar(idx=fila_idx):
                    return lambda: eliminar_callback(tabla_sql, fila[0], mostrar_filas)
                btn_eliminar = CTkButton(cuerpo, text="Eliminar", fg_color="#962d22", command=hacer_eliminar(fila_idx))
                btn_eliminar.grid(row=fila_idx, column=len(headers) + 1, padx=10, pady=4)
                btn_eliminar.grid_remove()
                btn_eliminar_ref[fila_idx] = btn_eliminar

            # Vincular eventos de mouse para mostrar/ocultar los botones
            for w in row_widgets:
                w.bind("<Enter>", lambda e, idx=fila_idx: on_row_enter(e, idx))
                w.bind("<Leave>", lambda e, idx=fila_idx: on_row_leave(e, idx))

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
        "registros": "id_registro",
        "salones": "id_salon",
        "grupos": "id_grupo",
        "calificaciones_finales": "id_calificacion",
        "calificaciones_actividades": "id_calif_actividad",
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
            ("calificaciones_actividades", "numero_control", "calificaciones de actividades"),
        ],
        "maestros": [
            ("grupos", "matricula_maestro", "grupos asignados"),
        ],
        "administradores": [],
        "usuarios": [],
        "salones": [
            ("horario", "id_salon", "horarios asignados"),
        ],
        "grupos": [
            ("registros", "id_grupo", "inscripciones"),
            ("calificaciones_finales", "id_grupo", "calificaciones finales"),
            ("horario", "id_grupo", "horarios"),
        ],
        "calificaciones_finales": [],
        "calificaciones_actividades": [],
        "registros": [],
        "materias": [],
        "carreras": [],
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
        "registros": "id_registro",
        "salones": "id_salon",
        "grupos": "id_grupo",
        "calificaciones_finales": "id_calificacion",
        "calificaciones_actividades": "id_calif_actividad",
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
            mensaje + "\n\nSí = Eliminar todo (incluyendo dependencias)\nNo = Cancelar eliminación"
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
                messagebox.showwarning("Advertencia", "No se encontró el registro a eliminar")

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
            messagebox.showwarning("Advertencia", "No se encontró el registro a eliminar")
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
        CTkLabel(card, text=label, font=("Arial", 13), text_color="white").pack(anchor="w", padx=12, pady=(10, 0))
        CTkLabel(card, text=valor, font=("Arial", 28, "bold"), text_color="white").pack(anchor="w", padx=12, pady=(0, 10))

    # ── CARGA DE ÍCONOS ──────────────────────────────────────
    icono_alumnos        = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/alumnos.png")),        size=(64,64))
    icono_maestros       = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/maestros.png")),       size=(64,64))
    icono_materias       = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/materias.png")),       size=(64,64))
    icono_grupos         = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/grupos.png")),         size=(64,64))
    icono_inscripciones  = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/inscripciones.png")), size=(64,64))
    icono_admin          = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/admin.png")),          size=(64,64))
    icono_carreras       = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/carreras.png")),       size=(64,64))
    icono_calificaciones = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/calificaciones.png")),size=(64,64))
    icono_actividades    = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/actividades.png")),    size=(64,64))
    icono_reportes       = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/reportes.png")),       size=(64,64))
    icono_usuarios       = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/usuario.png")),        size=(64,64))

    # ── ÁREA PRINCIPAL: izquierda + derecha ──────────────────
    main_area = CTkFrame(frame, fg_color="transparent")
    main_area.pack(fill="both", expand=True, padx=24, pady=(0, 16))
    main_area.grid_columnconfigure(0, weight=0)
    main_area.grid_columnconfigure(1, weight=1)
    main_area.grid_rowconfigure(0, weight=1)

    # ── PANEL IZQUIERDO: calendario + eventos ────────────────
    left_panel = CTkFrame(main_area, fg_color="#ffffff", corner_radius=12, width=270, height=540)
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
        CTkLabel(fila, text="●", text_color="#1A6B3C", font=("Arial", 10)).pack(side="left", padx=(4, 6))
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
        ("Alumnos",              "Gestión de estudiantes",        lambda: mostrar_alumnos(frame),                      "#510054", icono_alumnos),
        ("Maestros",             "Gestión de docentes",           lambda: mostrar_maestros(frame),                     "#004235", icono_maestros),
        ("Administradores",      "Gestión de administradores",    lambda: mostrar_admin(frame),                        "#1A3A8F", icono_admin),
        ("Materias",             "Catálogo de materias",          lambda: mostrar_materias(frame),                     "#2D3250", icono_materias),
        ("Grupos",               "Gestión de grupos",             lambda: mostrar_grupos(frame),                       "#2D3250", icono_grupos),
        ("Carreras",             "Catálogo de carreras",          lambda: mostrar_carreras(frame),                     "#2D3250", icono_carreras),
        ("Actividades",          "Gestión de actividades",        lambda: mostrar_actividades(frame),                  "#2D3250", icono_actividades),
        ("Inscripciones",        "Registro de inscripciones",     lambda: mostrar_inscripciones(frame),                "#2D3250", icono_inscripciones),
        ("Reportes",             "Generación de reportes",        lambda: mostrar_seccion_pendiente(frame, "Reportes"),  "#2D3250", icono_reportes),
        ("Calificaciones",       "Gestión de calificaciones",     lambda: mostrar_calificaciones_finales(frame),       "#2D3250", icono_calificaciones),
        ("Calif. Actividades",   "Gestión de calif. parciales",   lambda: mostrar_calificaciones_actividades(frame),   "#2D3250", icono_actividades),
        ("Usuarios",             "Gestión de usuarios",           lambda: mostrar_usuarios(frame),                     "#2D3250", icono_usuarios),
    ]

    for idx, (titulo_c, subtitulo_c, comando_c, color_c, icono_c) in enumerate(catalogos):
        r = idx // 3
        c = idx % 3
        grid_frame.grid_rowconfigure(r, weight=1)

        card = CTkFrame(grid_frame, fg_color=color_c, corner_radius=12, cursor="hand2")
        card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
        card.bind("<Button-1>", lambda e, cmd=comando_c: cmd())

        lbl_icono = CTkLabel(card, text="", image=icono_c)
        lbl_icono.pack(pady=(16, 4))
        lbl_icono.bind("<Button-1>", lambda e, cmd=comando_c: cmd())

        lbl_titulo = CTkLabel(card, text=titulo_c, font=("Arial", 15, "bold"), text_color="white")
        lbl_titulo.pack(pady=(0, 2))
        lbl_titulo.bind("<Button-1>", lambda e, cmd=comando_c: cmd())

        lbl_sub = CTkLabel(card, text=subtitulo_c, font=("Arial", 11), text_color="#cccccc")
        lbl_sub.pack(pady=(0, 16))
        lbl_sub.bind("<Button-1>", lambda e, cmd=comando_c: cmd())
def mostrar_calendario_imagen(frame):
    limpiar_frame(frame)

    header = CTkFrame(frame,height=60,fg_color="#154b74")
    header.pack(fill="x",pady=10)

    CTkLabel(header,text="Calendario",text_color="white",font=("Arial",26,"bold")).pack(pady=15)

    cuerpo = CTkFrame(frame,fg_color="#ffffff")
    cuerpo.pack(fill="both",expand=True,padx=20,pady=10)

    imagen_cal = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/calendario.png")),size=(600,800))

    CTkLabel(cuerpo,text="",image=imagen_cal).pack(expand=True)

def mostrar_seccion_pendiente(frame, titulo):
    limpiar_frame(frame)

    header = CTkFrame(frame, height=60, fg_color="#154b74")
    header.pack(fill="x", pady=10)

    CTkLabel(header, text=titulo, text_color="white", font=("Arial", 26, "bold")).pack(pady=15)

    cuerpo = CTkFrame(frame, fg_color="#ffffff")
    cuerpo.pack(fill="both", expand=True, padx=20, pady=10)

    CTkLabel(
        cuerpo,
        text="Seccion pendiente de integrar con la nueva distribucion.",
        font=("Arial", 16, "bold"),
        text_color="#000000"
    ).pack(pady=30)


def mostrar_seccion_gestion(frame,titulo,color_header,color_menu,color_tabla,botones,headers,tabla_sql=None):
    limpiar_frame(frame)

    CTkButton(frame,text="←",width=80,command=lambda: mostrar_dashboard(frame)).pack(anchor="w",padx=20,pady=10)

    header = CTkFrame(frame,height=60,fg_color=color_header)
    header.pack(fill="x")

    CTkLabel(header,text=titulo,text_color="white",font=("Arial",26,"bold")).pack(pady=15)

    menu = CTkFrame(frame,fg_color=color_menu)
    menu.pack(fill="x",padx=20,pady=10)

    for i in range(len(botones)):
        menu.grid_columnconfigure(i,weight=1)

    area_contenido = CTkFrame(frame)
    area_contenido.pack(fill="both",expand=True,padx=20,pady=10)

    def mostrar_tabla_base():
            limpiar_frame(area_contenido)

            # CARGAR DATOS REALES DE LA BD
            if tabla_sql:
                from db_conexion import ejecutar_select_todo
                try:
                    registros = ejecutar_select_todo(tabla_sql)
                except Exception as e:
                    print(f"Error cargando datos de {tabla_sql}: {e}")
                    registros = []
            else:
                registros = []

            if not registros:
                CTkLabel(
                    area_contenido,
                    text="No hay registros en la base de datos",
                    font=("Arial", 15, "bold"),
                    text_color="#000000"
                ).pack(pady=(10, 12))
            else:
                crear_tabla_editable(
                    area_contenido,
                    headers,
                    registros,
                    tabla_sql or "pendiente",
                    color_tabla,
                    actualizar_callback=actualizar_registro if tabla_sql else None,
                    eliminar_callback=eliminar_registro if tabla_sql else None
                )

    mostrar_tabla_base()

    for i,btn in enumerate(botones):
        comando_base = btn.get("comando")
        cmd = (lambda cb=comando_base: cb(area_contenido,mostrar_tabla_base)) if comando_base else mostrar_tabla_base
        CTkButton(menu,text=btn["texto"],fg_color=btn["color"],command=cmd).grid(row=0,column=i,padx=10,pady=10)

def seleccionar_csv():
    return filedialog.askopenfilename(title="Selecciona CSV",filetypes=[("CSV","*.csv")])

def guardar_csv(nombre):
    return filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile=nombre)

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
            messagebox.showinfo("Importación Exitosa", f"Datos importados correctamente a la tabla '{tabla}'")
            if volver:
                volver()
        except Exception as e:
            messagebox.showerror("Error de Importación", f"Error al importar: {str(e)}")


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
            messagebox.showinfo("Exportación Exitosa", f"Datos de '{tabla}' exportados a {ruta_csv}")
        except Exception as e:
            messagebox.showerror("Error de Exportación", f"Error al exportar: {str(e)}")


def crear_respaldo_completo():
    """Respaldo completo de la base de datos en archivos CSV individuales por tabla."""
    from tkinter import filedialog
    from formularios_bd import exportar_csv
    import datetime
    import os

    # Seleccionar carpeta raíz donde se creará la carpeta del respaldo
    carpeta_raiz = filedialog.askdirectory(title="Seleccionar dónde crear la carpeta del respaldo")

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
        "carreras", "materias", "grupos", "registros",
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
    carpeta_raiz = filedialog.askdirectory(title="Seleccionar carpeta donde buscar respaldos")

    if not carpeta_raiz:
        return

    # Buscar carpetas que tengan el formato Respaldo_DB_*
    carpetas_respaldo = []
    for carpeta in os.listdir(carpeta_raiz):
        ruta_completa = os.path.join(carpeta_raiz, carpeta)
        if os.path.isdir(ruta_completa) and carpeta.startswith("Respaldo_DB_"):
            carpetas_respaldo.append((carpeta, ruta_completa))

    if not carpetas_respaldo:
        messagebox.showwarning("No hay respaldos", "No se encontraron carpetas de respaldo (formato: Respaldo_DB_*)")
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
        messagebox.showwarning("No hay archivos", f"No se encontraron archivos CSV en la carpeta:\n{carpeta_seleccionada}")
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

    def registrar(area,volver):
        mostrar_form_registro_alumno(area,volver)

    def importar(area,volver):
        ejecutar_importacion("alumnos",volver)

    def exportar(area,volver):
        ejecutar_exportacion("alumnos","alumnos.csv")

    botones = [
        {"texto":"Registrar alumno","color":"#552157","comando":registrar},
        {"texto":"Importar CSV","color":"#552157","comando":importar},
        {"texto":"Exportar CSV","color":"#552157","comando":exportar},
    ]

    headers = ["Número de Control","Nombre","Apellido Paterno","Apellido Materno","Correo","Carrera","Semestre","Estado"]

    mostrar_seccion_gestion(frame,"Gestión de Alumnos","#510054","#fafafa","#9880a0",botones,headers,"alumnos")

def mostrar_maestros(frame):

    def registrar(area,volver):
        mostrar_form_registro_maestro(area,volver)

    def importar(area,volver):
        ejecutar_importacion("maestros",volver)

    def exportar(area,volver):
        ejecutar_exportacion("maestros","maestros.csv")

    botones = [
        {"texto":"Registrar maestro","color":"#022A22","comando":registrar},
        {"texto":"Importar CSV","color":"#022A22","comando":importar},
        {"texto":"Exportar CSV","color":"#022A22","comando":exportar},
    ]

    headers = ["Matrícula","Nombre","Apellido Paterno","Apellido Materno","Correo","Estatus","Estudios","Perfil","Carga Académica","Contrato","Cédula"]

    mostrar_seccion_gestion(frame,"Gestión de Maestros","#004235","#ffffff","#6F8A90",botones,headers,"maestros")

def mostrar_admin(frame):
    def registrar(area,volver):
        mostrar_form_registro_administrador(area,volver)
    def importar(area,volver):
        ejecutar_importacion("administradores",volver)

    def exportar(area,volver):
        ejecutar_exportacion("administradores","administradores.csv")

    botones = [
        {"texto":"Registrar administrador","color":"#610139","comando":registrar},
        {"texto":"Importar CSV","color":"#610139","comando":importar},
        {"texto":"Exportar CSV","color":"#610139","comando":exportar},
    ]
    headers = ["Matrícula","Nombre","Apellido Paterno","Apellido Materno","Área"]
    mostrar_seccion_gestion(frame, "Gestión de Administradores", "#610139", "#ffffff", "#9880a0", botones, headers, "administradores")

def mostrar_carreras(frame):
    def registrar(area,volver):
        mostrar_form_registro_carrera(area,volver)
    def importar(area,volver):
        ejecutar_importacion("carreras",volver)

    def exportar(area,volver):
        ejecutar_exportacion("carreras","carreras.csv")

    botones = [
        {"texto":"Registrar Carrera nueva","color":"#43000E","comando":registrar},
        {"texto":"Importar CSV","color":"#43000E","comando":importar},
        {"texto":"Exportar CSV","color":"#43000E","comando":exportar},
    ]
    headers = ["Nombre de la Carrera","Siglas","Semestres","Tipo"]
    mostrar_seccion_gestion(frame, "Gestión de Carreras", "#43000E", "#ffffff", "#d1c4b3", botones, headers, "carreras")

def mostrar_materias(frame):

    def registrar(area,volver):
        mostrar_form_registro_materia(area,volver)

    def importar(area,volver):
        ejecutar_importacion("materias",volver)

    def exportar(area,volver):
        ejecutar_exportacion("materias","materias.csv")

    botones = [
        {"texto":"Registrar materia","color":"#510113","comando":registrar},
        {"texto":"Importar CSV","color":"#510113","comando":importar},
        {"texto":"Exportar CSV","color":"#510113","comando":exportar},
    ]

    headers = ["Clave","Materia","Carrera","Horas","Créditos",]

    mostrar_seccion_gestion(frame,"Gestión de Materias","#761127","#ffffff","#9A0000",botones,headers,"materias")

def mostrar_grupos(frame):

    def registrar(area,volver):
        mostrar_form_registro_grupo(area,volver)

    def importar(area,volver):
        ejecutar_importacion("grupos",volver)

    def exportar(area,volver):
        ejecutar_exportacion("grupos","grupos.csv")

    botones = [
        {"texto":"Crear grupo","color":"#184c73","comando":registrar},
        {"texto":"Importar CSV","color":"#184c73","comando":importar},
        {"texto":"Exportar CSV","color":"#184c73","comando":exportar},
    ]

    headers = ["Grupo","Materia","Maestro","Periodo", "Año","Cupo", "Inscritos", "Horario","Estado" ]

    mostrar_seccion_gestion(frame,"Gestión de Grupos","#1f6aa5","#ffffff","#8fb1cb",botones,headers,"grupos")

def mostrar_inscripciones(frame):

    def registrar(area,volver):
        mostrar_form_registro_inscripcion(area,volver)

    def importar(area,volver):
        ejecutar_importacion("registros",volver)

    def exportar(area,volver):
        ejecutar_exportacion("registros","inscripciones.csv")

    botones = [
        {"texto":"Inscribir alumno","color":"#A64500","comando":registrar},
        {"texto":"Importar CSV","color":"#A64500","comando":importar},
        {"texto":"Exportar CSV","color":"#A64500","comando":exportar},
    ]

    headers = ["Alumno","Número de Control","Grupo","Estatus","Tipo de inscripción"]

    mostrar_seccion_gestion(frame,"Inscripciones","#7A3500","#ffffff","#C75C00",botones,headers,"registros")


def mostrar_usuarios(frame):

    def registrar(area,volver):
        mostrar_form_registro_usuario(area,volver)

    def importar(area,volver):
        ejecutar_importacion("usuarios",volver)

    def exportar(area,volver):
        ejecutar_exportacion("usuarios","usuarios.csv")

    botones = [
        {"texto":"Registrar usuario","color":"#2b4d7a","comando":registrar},
        {"texto":"Importar CSV","color":"#2b4d7a","comando":importar},
        {"texto":"Exportar CSV","color":"#2b4d7a","comando":exportar},
    ]

    headers = ["Usuario","Contraseña","Rol"]

    mostrar_seccion_gestion(frame,"Gestión de Usuarios","#2b4d7a","#ffffff","#4c6fa0",botones,headers,"usuarios")


# === ACTIVIDADES ===
def mostrar_actividades(frame):
    def registrar(area,volver):
        mostrar_form_registro_tipo_actividad(area,volver)

    def importar(area,volver):
        ejecutar_importacion("actividades",volver)

    def exportar(area,volver):
        ejecutar_exportacion("actividades","actividades.csv")

    botones = [
        {"texto":"Crear nueva actividad","color":"#1f6aa5","comando":registrar},
        {"texto":"Importar CSV","color":"#1f6aa5","comando":importar},
        {"texto":"Exportar CSV","color":"#1f6aa5","comando":exportar},
    ]

    headers = ["Tipo de Actividad","Unidad","Grupo","Materia","Ponderacion", "Detalles"]

    mostrar_seccion_gestion(frame,"Gestión de Actividades","#1f6aa5","#ffffff","#8fb1cb",botones,headers,"actividades")

def mostrar_calificaciones_finales(frame):
    def registrar(area, volver):
        mostrar_form_registro_calificacion_final(area, volver)

    def importar(area, volver):
        ejecutar_importacion("calificaciones_finales", volver)

    def exportar(area, volver):
        ejecutar_exportacion("calificaciones_finales", "calificaciones_finales.csv")

    botones = [
        {"texto": "Registrar calificación", "color": "#2b4d7a", "comando": registrar},
        {"texto": "Importar CSV", "color": "#2b4d7a", "comando": importar},
        {"texto": "Exportar CSV", "color": "#2b4d7a", "comando": exportar},
    ]

    headers = ["Numero de control", "Alumno", "Grupo","Materia","Periodo", "Calificación Final", ]

    mostrar_seccion_gestion(
        frame,
        "Gestión de Calificaciones Finales",
        "#2b4d7a",
        "#ffffff",
        "#8fb1cb",
        botones,
        headers,
        "calificaciones_finales"
    )


def mostrar_calificaciones_actividades(frame):

    def importar(area, volver):
        ejecutar_importacion("calificaciones_actividades", volver)

    def exportar(area, volver):
        ejecutar_exportacion("calificaciones_actividades", "calificaciones_actividades.csv")

    botones = [
        {"texto": "Importar CSV", "color": "#2b4d7a", "comando": importar},
        {"texto": "Exportar CSV", "color": "#2b4d7a", "comando": exportar},
    ]

    headers = ["Numero de Control", "Alumno", "Actividad", "Calificación", "Fecha", "Observaciones"]

    mostrar_seccion_gestion(
        frame,
        "Gestión de Calificaciones de Actividades",
        "#2b4d7a",
        "#ffffff",
        "#8fb1cb",
        botones,
        headers,
        "calificaciones_actividades"
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

        franja = CTkFrame(tarjeta, fg_color=c["borde"], width=6, corner_radius=0)
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