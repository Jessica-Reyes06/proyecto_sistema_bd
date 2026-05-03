from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton
import tkinter as tk
from customtkinter import *
from PIL import Image
from config_principal import calendario, limpiar_frame, crear_tarjeta
from formularios_bd import *
import datetime
import os
import sys


def ruta_recurso(ruta_relativa):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, ruta_relativa)

def crear_tabla_editable(parent, headers, registros, tabla_sql, actualizar_callback=None):
 
    tabla = CTkFrame(parent)
    tabla.pack(fill="both", expand=True)

    encabezado = CTkFrame(tabla, fg_color="#e0e0e0")
    encabezado.pack(fill="x")
    for i, h in enumerate(headers):
        encabezado.grid_columnconfigure(i, weight=1)
        CTkLabel(encabezado, text=h, text_color="white", font=("Arial", 14, "bold"), anchor="w", justify="left").grid(row=0, column=i, padx=10, pady=10, sticky="w")
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

    import mysql.connector
    from db_conexion import obtener_conexion
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, valores)
        conexion.commit()
    finally:
        conexion.close()

pendientes_admin = []

def mostrar_dashboard(frame):
    limpiar_frame(frame)

    header = CTkFrame(frame, height=60, fg_color="#154b74")
    header.pack(fill="x", pady=(0,20))

    titulo = CTkLabel(header,text="Panel de Administración",text_color="white",font=("Arial",28,"bold"))
    titulo.pack(pady=15)

    contenedor = CTkFrame(frame, fg_color="#b8d0e1")
    contenedor.pack(fill="both", expand=True, padx=20, pady=(10, 0))

    for c in range(5):
        contenedor.grid_columnconfigure(c, weight=1)

    for r in range(3):
        contenedor.grid_rowconfigure(r, weight=1)

    icono_alumnos = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/alumnos.png")),size=(64,64))
    icono_maestros = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/maestros.png")),size=(64,64))
    icono_materias = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/materias.png")),size=(64,64))
    icono_grupos = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/grupos.png")),size=(64,64))
    icono_inscripciones = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/inscripciones.png")),size=(64,64))
    icono_usuarios = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/usuario.png")),size=(64,64))
    icono_horarios = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_alumnos/reloj.png")),size=(64,64)) 

    crear_tarjeta(contenedor,"Alumnos",lambda: mostrar_alumnos(frame),"#510054",icono_alumnos).grid(row=0,column=0,padx=10,pady=10)
    crear_tarjeta(contenedor,"Maestros",lambda: mostrar_maestros(frame),"#004235",icono_maestros).grid(row=0,column=1,padx=10,pady=10)
    crear_tarjeta(contenedor,"Materias",lambda: mostrar_materias(frame),"#761127",icono_materias).grid(row=0,column=2,padx=10,pady=10)
    crear_tarjeta(contenedor,"Grupos",lambda: mostrar_grupos(frame),"#1f6aa5",icono_grupos).grid(row=0,column=3,padx=10,pady=10)
    crear_tarjeta(contenedor,"Horarios",lambda: mostrar_horarios(frame),"#1f6aa5",icono_horarios).grid(row=0,column=4,padx=10,pady=10)
    crear_tarjeta(contenedor,"Inscripciones",lambda: mostrar_inscripciones(frame),"#7A3500",icono_inscripciones).grid(row=1,column=0,padx=10,pady=10)
    crear_tarjeta(contenedor,"Usuarios",lambda: mostrar_usuarios(frame),"#2b4d7a",icono_usuarios).grid(row=1,column=1,padx=10,pady=10)

    zona_inferior = CTkFrame(frame, height=120, fg_color="#f1f3f5")
    zona_inferior.pack(side="bottom", fill="x", padx=20, pady=(0,15))
    zona_inferior.pack_propagate(False)

    frame_calendario = CTkFrame(zona_inferior, fg_color="#ffffff")
    frame_calendario.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")

    calendario(frame_calendario)

    frame_texto = CTkFrame(zona_inferior, fg_color="#cfe5f3")
    frame_texto.grid(row=0,column=1,padx=10,pady=10,sticky="nsew")

    frame_texto.grid_columnconfigure(0, weight=1)
    frame_texto.grid_columnconfigure(1, weight=1)

    CTkLabel(frame_texto,text="Enero - Junio 2026",justify="left",font=("Arial",16,"bold"),text_color="#000000").grid(row=0,column=0,columnspan=2,padx=15,pady=(10,5),sticky="w")

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

    mitad = (len(eventos)+1)//2

    for i in range(len(eventos)):
        if i < mitad:
            columna = 0
            fila = i+1
        else:
            columna = 1
            fila = (i-mitad)+1

        CTkLabel(frame_texto,text=eventos[i],justify="left",anchor="w",font=("Arial",14),text_color="#000000").grid(row=fila,column=columna,padx=(15,15),pady=2,sticky="w")

def mostrar_calendario_imagen(frame):
    limpiar_frame(frame)

    header = CTkFrame(frame,height=60,fg_color="#154b74")
    header.pack(fill="x",pady=10)

    CTkLabel(header,text="Calendario",text_color="white",font=("Arial",26,"bold")).pack(pady=15)

    cuerpo = CTkFrame(frame,fg_color="#ffffff")
    cuerpo.pack(fill="both",expand=True,padx=20,pady=10)

    imagen_cal = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/calendario.png")),size=(600,800))

    CTkLabel(cuerpo,text="",image=imagen_cal).pack(expand=True)

def mostrar_pendientes(frame):
    limpiar_frame(frame)

    header = CTkFrame(frame,height=60,fg_color="#154b74")
    header.pack(fill="x",pady=10)

    CTkLabel(header,text="Pendientes",text_color="white",font=("Arial",26,"bold")).pack(pady=15)

    cuerpo = CTkFrame(frame,fg_color="#ffffff")
    cuerpo.pack(fill="both",expand=True,padx=20,pady=10)

    lista = CTkScrollableFrame(cuerpo,fg_color="#ffffff")
    lista.pack(fill="both",expand=True,padx=10,pady=10)

    if not pendientes_admin:
        CTkLabel(lista,text="No hay pendientes registrados",font=("Arial",16,"bold")).pack(pady=10)
    else:
        for i,texto in enumerate(pendientes_admin,start=1):
            CTkLabel(lista,text=f"{i}. {texto}",anchor="w",justify="left",font=("Arial",14)).pack(fill="x",padx=5,pady=4)

def mostrar_notificaciones(frame):
    limpiar_frame(frame)

    header = CTkFrame(frame,height=60,fg_color="#154b74")
    header.pack(fill="x",pady=10)

    CTkLabel(header,text="Notificaciones",text_color="white",font=("Arial",26,"bold")).pack(pady=15)

    cuerpo = CTkFrame(frame,fg_color="#ffffff")
    cuerpo.pack(fill="both",expand=True,padx=20,pady=10)

    CTkLabel(cuerpo,text="No hay notificaciones",font=("Arial",18,"bold")).pack(pady=20)

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

            if not tabla_sql:
                CTkLabel(area_contenido, text="No hay registros").pack()
                return

            try:

                registros = ejecutar_select(f"SELECT * FROM {tabla_sql}")

                if not registros:
                    CTkLabel(area_contenido, text="No hay registros").pack()
                    return

                # columnas reales de la tabla
                cursor = conexion.cursor()
                cursor.execute(f"SHOW COLUMNS FROM {tabla_sql}")
                columnas = [col[0] for col in cursor.fetchall()]
                cursor.close()

                crear_tabla_editable_con_doble_click(
                    area_contenido,
                    headers,
                    registros,
                    tabla_sql,
                    columnas,
                    columnas[0],
                    volver_a_lista=mostrar_tabla_base
                )

            except Exception as e:

                CTkLabel(
                    area_contenido,
                    text=f"Error al cargar datos: {e}",
                    text_color="red"
                ).pack(pady=10)

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
    ruta = seleccionar_csv()
    if not ruta:
        return
    try:
        importar_csv(tabla,ruta)
        tk.messagebox.showinfo("Importar CSV","Datos importados correctamente.")
        if volver:
            volver()
    except Exception as e:
        tk.messagebox.showerror("Error",str(e))

def ejecutar_exportacion(tabla,nombre):
    ruta = guardar_csv(nombre)
    if not ruta:
        return
    try:
        exportar_csv(tabla,ruta)
        tk.messagebox.showinfo("Exportar CSV","Datos exportados correctamente.")
    except Exception as e:
        tk.messagebox.showerror("Error",str(e))


def crear_respaldo_completo():
    """Respaldo completo de la base de datos en archivos CSV individuales por tabla."""

    carpeta = filedialog.askdirectory(title="Selecciona carpeta para el respaldo")
    if not carpeta:
        return

    marca_tiempo = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    tablas = ["alumnos", "maestros", "materias", "grupos", "registros"]

    try:
        for tabla in tablas:
            nombre_archivo = f"{tabla}_{marca_tiempo}.csv"
            ruta = f"{carpeta}/{nombre_archivo}"
            exportar_csv(tabla, ruta)

        tk.messagebox.showinfo("Respaldo", "Respaldo creado correctamente.")
    except Exception as e:
        tk.messagebox.showerror("Respaldo", f"Error al crear respaldo:\n{e}")


def restaurar_desde_respaldo():
    """Restaura datos desde los CSV de respaldo más recientes en una carpeta.

    Para cada tabla principal busca el archivo con nombre
    "tabla_YYYYMMDD_HHMMSS.csv" más reciente y lo importa.
    """

    carpeta = filedialog.askdirectory(title="Selecciona carpeta con respaldos")
    if not carpeta:
        return

    tablas = ["alumnos", "maestros", "materias", "grupos", "registros"]

    try:
        for tabla in tablas:
            prefijo = f"{tabla}_"
            archivos = [f for f in os.listdir(carpeta) if f.startswith(prefijo) and f.endswith(".csv")]
            if not archivos:
                continue

            archivos.sort()  # por nombre; con YYYYMMDD_HHMMSS el último es el más reciente
            archivo_reciente = archivos[-1]
            ruta = os.path.join(carpeta, archivo_reciente)

            importar_csv(tabla, ruta)

        tk.messagebox.showinfo("Restaurar", "Datos restaurados desde los respaldos más recientes.")
    except Exception as e:
        tk.messagebox.showerror("Restaurar", f"Error al restaurar datos:\n{e}")

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

    headers = ["Clave","Materia","Horas","Créditos","Tipo"]

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

    headers = ["ID Grupo","Maestro","Materia","Cupo", "Estado"]

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

    headers = ["ID","No.Control","ID Grupo","Fecha","Estatus","Tipo"]

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

    headers = ["ID","Usuario","Contraseña","Rol"]

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
