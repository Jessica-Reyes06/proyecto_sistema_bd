from tkinter import messagebox
from customtkinter import *
from PIL import Image
from config_principal import calendario, limpiar_frame, crear_tarjeta
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

def crear_tabla_editable(parent, headers, registros, tabla_sql, color_tabla="#e0e0e0", actualizar_callback=None):
 
    tabla = CTkFrame(parent)
    tabla.pack(fill="both", expand=True)

    encabezado = CTkFrame(tabla, fg_color=color_tabla)
    encabezado.pack(fill="x")
    color_texto = color_texto_legible(color_tabla)
    for i, h in enumerate(headers):
        encabezado.grid_columnconfigure(i, weight=1)
        CTkLabel(encabezado, text=h, text_color=color_texto, font=("Arial", 14, "bold"), anchor="w", justify="left").grid(row=0, column=i, padx=10, pady=10, sticky="w")
    encabezado.grid_columnconfigure(len(headers), weight=1)

    cuerpo = CTkFrame(tabla)
    cuerpo.pack(fill="both", expand=True)

    fila_editando = {"idx": None}
    entries = {}
    btn_editar_ref = {}

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

    def on_row_leave(event, idx):
        btn = btn_editar_ref.get(idx)
        if btn:
            btn.grid_remove()

    def mostrar_filas():
        for widget in cuerpo.winfo_children():
            widget.destroy()
        btn_editar_ref.clear()
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
            # Vincular eventos de mouse para mostrar/ocultar el botón
            for w in row_widgets:
                w.bind("<Enter>", lambda e, idx=fila_idx: on_row_enter(e, idx))
                w.bind("<Leave>", lambda e, idx=fila_idx: on_row_leave(e, idx))

    mostrar_filas()
    return tabla

def ejecutar_update(sql, valores):

   # import mysql.connector
        return None

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
        ("Alumnos",         "342", "#9B30FF"),
        ("Maestros",        "45",  "#1A6B3C"),
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
    icono_tipos          = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/tipos.png")),          size=(64,64))
    icono_usuarios       = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/usuario.png")),        size=(64,64))

    # ── ÁREA PRINCIPAL: izquierda + derecha ──────────────────
    main_area = CTkFrame(frame, fg_color="transparent")
    main_area.pack(fill="both", expand=True, padx=24, pady=(0, 16))
    main_area.grid_columnconfigure(0, weight=0)
    main_area.grid_columnconfigure(1, weight=1)
    main_area.grid_rowconfigure(0, weight=1)

    # ── PANEL IZQUIERDO: calendario + eventos ────────────────
    left_panel = CTkFrame(main_area, fg_color="#ffffff", corner_radius=12, width=270)
    left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
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
        ("Alumnos",              "Gestión de estudiantes",        lambda: mostrar_alumnos(frame),                      "#9B30FF", icono_alumnos),
        ("Maestros",             "Gestión de docentes",           lambda: mostrar_maestros(frame),                     "#1A6B3C", icono_maestros),
        ("Administradores",      "Gestión de administradores",    lambda: mostrar_admin(frame),                        "#1A3A8F", icono_admin),
        ("Materias",             "Catálogo de materias",          lambda: mostrar_materias(frame),                     "#2D3250", icono_materias),
        ("Grupos",               "Gestión de grupos",             lambda: mostrar_grupos(frame),                       "#2D3250", icono_grupos),
        ("Carreras",             "Catálogo de carreras",          lambda: mostrar_carreras(frame),                     "#2D3250", icono_carreras),
        ("Tipos de Actividades", "Clasificación de actividades",  lambda: mostrar_tipos_actividades(frame),            "#2D3250", icono_tipos),
        ("Actividades",          "Gestión de actividades",        lambda: mostrar_actividades(frame),                  "#2D3250", icono_actividades),
        ("Inscripciones",        "Registro de inscripciones",     lambda: mostrar_inscripciones(frame),                "#2D3250", icono_inscripciones),
        ("Reportes",             "Generación de reportes",        lambda: mostrar_seccion_pendiente(frame, "Reportes"),  "#2D3250", icono_reportes),
        ("Calificaciones",       "Gestión de calificaciones",     lambda: mostrar_calificaciones_finales(frame),       "#2D3250", icono_calificaciones),
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

def mostrar_solicitudes(frame):
    limpiar_frame(frame)

    header = CTkFrame(frame,height=60,fg_color="#154b74")
    header.pack(fill="x",pady=10)

    CTkLabel(header,text="Solicitudes",text_color="white",font=("Arial",26,"bold")).pack(pady=15)

    cuerpo = CTkFrame(frame,fg_color="#ffffff")
    cuerpo.pack(fill="both",expand=True,padx=20,pady=10)

    lista = CTkScrollableFrame(cuerpo,fg_color="#ffffff")
    lista.pack(fill="both",expand=True,padx=10,pady=10)

    if not pendientes_admin:
        CTkLabel(lista,text="No hay solicitudes registradas",font=("Arial",16,"bold")).pack(pady=10)
    else:
        for i,texto in enumerate(pendientes_admin,start=1):
            CTkLabel(lista,text=f"{i}. {texto}",anchor="w",justify="left",font=("Arial",14)).pack(fill="x",padx=5,pady=4)


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

            CTkLabel(
                area_contenido,
                text="Vista visual lista para conectar con la nueva base de datos.",
                font=("Arial", 15, "bold"),
                text_color="#000000"
            ).pack(pady=(10, 12))

            crear_tabla_editable(
                area_contenido,
                headers,
                [],
                tabla_sql or "pendiente",
                color_tabla,
                actualizar_callback=None
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

def ejecutar_importacion(tabla,volver):
    messagebox.showinfo("Importar CSV", "Funcion pendiente de conectar con la nueva base de datos.")
    if volver:
        volver()

def ejecutar_exportacion(tabla,nombre):
    messagebox.showinfo("Exportar CSV", "Funcion pendiente de conectar con la nueva base de datos.")


def crear_respaldo_completo():
    """Respaldo completo de la base de datos en archivos CSV individuales por tabla."""
    messagebox.showinfo("Respaldo", "Funcion pendiente de conectar con la nueva base de datos.")


def restaurar_desde_respaldo():
    """Restaura datos desde los CSV de respaldo más recientes en una carpeta.

    Para cada tabla principal busca el archivo con nombre
    "tabla_YYYYMMDD_HHMMSS.csv" más reciente y lo importa.
    """

    messagebox.showinfo("Restaurar", "Funcion pendiente de conectar con la nueva base de datos.")



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

    headers = ["No.Control","Nombre","A. Paterno","A. Materno","Correo","Carrera","Semestre","Estado"]

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

    headers = ["Matricula","Nombre","A. Paterno","A. Materno","Correo","Estatus","Estudios","Perfil","Carga Académica","Contrato","Cédula"]

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
    headers = ["Matricula","Nombre","A. Paterno","A. Materno","Area", "ID de usuario"]
    mostrar_seccion_gestion(frame, "Gestión de Administradores", "#610139", "#ffffff", "#9880a0", botones, headers, "administradores")

def mostrar_carreras(frame):
    def registrar(area,volver):
        mostrar_form_registro_carrera(area,volver)
    def importar(area,volver):
        ejecutar_importacion("carreras",volver)

    def exportar(area,volver):
        ejecutar_exportacion("carreras","carreras.csv")

    botones = [
        {"texto":"Registrar administrador","color":"#43000E","comando":registrar},
        {"texto":"Importar CSV","color":"#43000E","comando":importar},
        {"texto":"Exportar CSV","color":"#43000E","comando":exportar},
    ]
    headers = ["Nombre de la Carrera","Tipo"]
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

    headers = ["Clave","Materia","Horas","Créditos","Carrera"]

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

    headers = ["ID Grupo","Maestro","Materia","Cupo","Periodo", "Año", "Inscritos", "Estado" ]

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

    headers = ["ID","No.Control","ID Grupo","Estatus","Tipo de inscripción"]

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

    headers = ["ID","Contraseña","Rol"]

    mostrar_seccion_gestion(frame,"Gestión de Usuarios","#2b4d7a","#ffffff","#4c6fa0",botones,headers,"usuarios")

# === HORARIOS ===
def mostrar_horarios(frame):
    def registrar(area,volver):
        mostrar_form_registro_horario(area,volver)

    def importar(area,volver):
        ejecutar_importacion("horario",volver)

    def exportar(area,volver):
        ejecutar_exportacion("horario","horario.csv")

    botones = [
        {"texto":"Registrar horario","color":"#1f6aa5","comando":registrar},
        {"texto":"Importar CSV","color":"#1f6aa5","comando":importar},
        {"texto":"Exportar CSV","color":"#1f6aa5","comando":exportar},
    ]

    headers = ["ID Horario","ID Grupo","Día","Hora inicio","Hora fin","ID Salón"]

    mostrar_seccion_gestion(frame,"Gestión de Horarios","#1f6aa5","#ffffff","#8fb1cb",botones,headers,"horario")

# === ACTIVIDADES ===
def mostrar_actividades(frame):
    def importar(area,volver):
        ejecutar_importacion("actividades",volver)

    def exportar(area,volver):
        ejecutar_exportacion("actividades","actividades.csv")

    botones = [
        {"texto":"Importar CSV","color":"#1f6aa5","comando":importar},
        {"texto":"Exportar CSV","color":"#1f6aa5","comando":exportar},
    ]

    headers = ["ID Actividad","Tipo de Actividad","Unidad","Grupo","Materia","Ponderacion", "Detalles"]

    mostrar_seccion_gestion(frame,"Gestión de Actividades","#1f6aa5","#ffffff","#8fb1cb",botones,headers,"actividades")

def mostrar_tipos_actividades(frame):
    def importar(area,volver):
        ejecutar_importacion("tipos_actividades",volver)

    def exportar(area,volver):
        ejecutar_exportacion("tipos_actividades","tipos_actividades.csv")

    botones = [
        {"texto":"Crear Tipo de Actividad","color":"#2b4d7a","comando":importar},
        {"texto":"Importar CSV","color":"#2b4d7a","comando":importar},
        {"texto":"Exportar CSV","color":"#2b4d7a","comando":exportar},
    ]

    headers = ["ID Tipo","Nombre de la Actividad"]

    mostrar_seccion_gestion(frame,"Gestión de Tipos de Actividades","#1f6aa5","#ffffff","#8fb1cb",botones,headers,"tipos_actividades")

def mostrar_calificaciones_finales(frame):
    def importar(area,volver):
        ejecutar_importacion("calificaciones_finales",volver)

    def exportar(area,volver):
        ejecutar_exportacion("calificaciones_finales","calificaciones_finales.csv")

    botones = [
        {"texto":"Importar CSV","color":"#2b4d7a","comando":importar},
        {"texto":"Exportar CSV","color":"#2b4d7a","comando":exportar},
    ]

    headers = ["ID de Calificación","Calificación Final", "ID Registro"]

    mostrar_seccion_gestion(frame,"Gestión de Calificaciones Finales","#1f6aa5","#ffffff","#8fb1cb",botones,headers,"calificaciones_finales")
