from core.db_conexion import ejecutar_select, ejecutar_insert
from modulo_alumnos import Grupos_Alumno as grupos_alumno
import importlib
import datetime
from tkcalendar import Calendar
from PIL import Image
from customtkinter import *
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


ventana = None
frame_contenido = None
numero_control_alumno = None
nombre_alumno = None


def ruta_recurso(ruta_relativa):
    base_path = getattr(sys, "_MEIPASS", ROOT_DIR)
    return os.path.join(base_path, ruta_relativa)

# ------------------FUNCIONES----------------


def mostrar_maximizada():
    ventana.state("zoomed")
    ventana.deiconify()


def limpiar_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def cerrar_sesion():
    global ventana
    if ventana is not None:
        ventana.destroy()

    import ui.interfaz_login as interfaz_login
    importlib.reload(interfaz_login)


def crear_icono_clases(frame_clases, columna, fila, clave_grupo, maestro, materia, frame_contenido, id_grupo):
    frame_grupo_ind = CTkFrame(frame_clases,
                               fg_color="white")
    frame_grupo_ind.grid(row=fila, column=columna, padx=5, pady=5)
    img_grupo = CTkImage(
        light_image=Image.open(ruta_recurso(
            "ui/carpeta_iconos/iconos_alumnos/archivo-de-carpetas.png")),
        size=(90, 90)
    )
    CTkButton(
        frame_grupo_ind,
        text=clave_grupo,
        width=160,
        height=150,
        fg_color="#715a72",
        hover_color="#5e485f",
        text_color="white",
        image=img_grupo,
        compound="bottom",
        font=("Arial Rounded MT Bold", 18),
        command=lambda m=materia, p=maestro, g=id_grupo:
        grupos_alumno.Info_Grupo(
            frame_contenido, m, p, g, numero_control_alumno)
    ).grid(row=0, column=0, padx=10, pady=5)
    # Etiqueta para el nombre de la materia
    CTkLabel(frame_grupo_ind,
             text=materia,
             text_color="#000000",
             justify="left",
             font=("Arial Rounded MT Bold", 20, "bold")
             ).grid(row=1, column=0, padx=10, pady=(0, 0), sticky="w")
    # Etiqueta para el nombre del maestro
    CTkLabel(frame_grupo_ind,
             text=maestro,
             text_color="#000000",
             justify="left",
             font=("Arial", 16, "italic")
             ).grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")


def menu_opcioneas(frame_menu):
    global numero_control_alumno, nombre_alumno

    logo_img = CTkImage(light_image=Image.open(ruta_recurso(
        "ui/carpeta_iconos/general/logo.jpeg")), size=(120, 50))
    # Frame de fondo del color del logo
    frame_logo_bg = CTkFrame(frame_menu, fg_color="#003152", corner_radius=0)
    frame_logo_bg.pack(fill="x", pady=(0, 5), padx=0)
    CTkLabel(frame_logo_bg, text="", image=logo_img,
             bg_color="#003152").pack(padx=10, pady=5)

    frame_usuario = CTkFrame(frame_menu,
                             width=250,
                             fg_color="#cabece")
    frame_usuario.pack(pady=(5, 10), padx=20)

    img_usuario = CTkImage(
        light_image=Image.open(ruta_recurso(
            "ui/carpeta_iconos/iconos_alumnos/avatar.png")),
        size=(100, 100)
    )
    CTkLabel(frame_usuario,
             text="",
             text_color="black",
             image=img_usuario,
             font=("Arial Rounded MT Bold", 15)
             ).pack(pady=10, padx=10, anchor="center")

    texto_nombre = nombre_alumno if nombre_alumno else "Nombre del usuario"
    texto_numero = numero_control_alumno if numero_control_alumno else "Numero de control"

    CTkLabel(frame_usuario,
             text=texto_nombre,
             text_color="black",
             compound="left",
             font=("Arial Rounded MT Bold", 20),
             wraplength=240
             ).pack(pady=10, padx=10)
    CTkLabel(frame_usuario,
             text=texto_numero,
             text_color="black",
             compound="left",
             font=("Arial Rounded MT Bold", 20)
             ).pack(pady=(0, 10), padx=10)

    frame_opciones = CTkFrame(frame_menu,
                              width=250,
                              height=400,
                              fg_color="#cabece")
    frame_opciones.pack(pady=10, padx=20)

    crear_opciones_menu(frame_opciones, "      Inicio",
                        img_hogar, 5, lambda: Mis_Clases(frame_contenido))
    crear_opciones_menu(frame_opciones, "      Calendario",
                        img_calendario, 5, lambda: calendario(frame_contenido))
    crear_opciones_menu(frame_opciones, "      Tareas Pendientes",
                        img_pendiente, 5, lambda: tareas_pendientes(frame_contenido))
    crear_opciones_menu(frame_opciones, "      Cerrar Sesión",
                        img_cerrar_sesion, 260, cerrar_sesion)
    boton = CTkButton(frame_opciones,
                      text="Configuracion de Perfil",
                      width=300,
                      fg_color="#715a72",
                      hover_color="#5e485f",
                      text_color="white",
                      anchor="w",
                      font=("Arial Rounded MT Bold", 16),
                      command=Configuracion_Perfil
                      )
    boton.pack(pady=(10, 10), padx=10)


def Configuracion_Perfil():
    global numero_control_alumno, frame_contenido
    limpiar_frame(frame_contenido)

    CTkLabel(
        frame_contenido,
        text="Configuracion de Perfil",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 30)
    ).pack(fill="x", anchor="w", pady=10, padx=10)

    CTkLabel(
        frame_contenido,
        text="Consulta tu informacion y actualiza tu contrasena",
        text_color="gray",
        anchor="w",
        font=("Arial", 16)
    ).pack(fill="x", anchor="w", padx=12, pady=(0, 10))

    tarjeta_info = CTkFrame(frame_contenido, fg_color="white")
    tarjeta_info.pack(fill="x", padx=10, pady=10)

    if not numero_control_alumno:
        CTkLabel(
            tarjeta_info,
            text="No hay una sesion de alumno activa.",
            text_color="black",
            anchor="w",
            font=("Arial", 16)
        ).pack(fill="x", padx=10, pady=10)
        return

    consulta_alumno = """
        SELECT
            TRIM(A.nombre_alumno),
            TRIM(A.apellido_paterno),
            TRIM(A.apellido_materno),
            COALESCE(TRIM(A.correo_alumno), ''),
            COALESCE(TRIM(C.nombre_carrera), '')
        FROM alumno A
        LEFT JOIN carreras C ON A.id_carrera = C.id_carrera
        WHERE A.numero_control = %s
        LIMIT 1
    """
    datos_alumno = ejecutar_select(consulta_alumno, (numero_control_alumno,))

    if not datos_alumno:
        CTkLabel(
            tarjeta_info,
            text="No se encontro informacion del alumno en sesion.",
            text_color="black",
            anchor="w",
            font=("Arial", 16)
        ).pack(fill="x", padx=10, pady=10)
        return

    nombre, ap_paterno, ap_materno, correo, carrera = datos_alumno[0]
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
        text=f"Numero de control: {numero_control_alumno}",
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
        text=f"Carrera: {carrera if carrera else 'Sin carrera registrada'}",
        text_color="#333333",
        anchor="w",
        font=("Arial", 16)
    ).pack(fill="x", padx=12, pady=(4, 10))

    frame_formulario = CTkFrame(tarjeta_info, fg_color="#f4eef6")
    frame_formulario.pack(fill="x", padx=12, pady=(5, 10))
    frame_formulario.pack_forget()

    CTkLabel(
        frame_formulario,
        text="Nueva contrasena",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 14)
    ).pack(fill="x", padx=10, pady=(10, 5))

    entry_nueva = CTkEntry(frame_formulario, show="*", width=340)
    entry_nueva.pack(fill="x", padx=10, pady=(0, 10))

    CTkLabel(
        frame_formulario,
        text="Confirmar contrasena",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 14)
    ).pack(fill="x", padx=10, pady=(0, 5))

    entry_confirmar = CTkEntry(frame_formulario, show="*", width=340)
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
        text_color="#333333",
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
                UPDATE usuarios
                SET contrasena = %s
                WHERE usuario = %s
            """
            ejecutar_insert(sql_update, (nueva, numero_control_alumno))
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
        fg_color="#715a72",
        hover_color="#5e485f",
        text_color="white",
        font=("Arial Rounded MT Bold", 12),
        width=180,
        command=alternar_visibilidad_contrasena
    )
    boton_mostrar.pack(side="left")

    boton_guardar = CTkButton(
        frame_botones,
        text="Guardar contrasena",
        fg_color="#715a72",
        hover_color="#5e485f",
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
        fg_color="#715a72",
        hover_color="#5e485f",
        text_color="white",
        font=("Arial Rounded MT Bold", 14),
        command=alternar_formulario
    ).pack(anchor="e", padx=12, pady=(0, 12))


def crear_opciones_menu(frame, texto, imagen, y, funcion=None):
    boton = CTkButton(frame,
                      text=texto,
                      width=300,
                      fg_color="#715a72",
                      hover_color="#5e485f",
                      # selected_color="#715a72",
                      text_color="white",
                      image=imagen,
                      anchor="w",
                      font=("Arial Rounded MT Bold", 15),
                      command=funcion
                      )
    boton.pack(pady=(y, 10), padx=10)


def crear_icono(ruta):
    # aceptar `ruta` como ruta absoluta o relativa dentro del proyecto
    if os.path.isabs(ruta) and os.path.exists(ruta):
        path = ruta
    else:
        path = ruta_recurso(ruta)
    imagen = CTkImage(
        light_image=Image.open(path),
        size=(20, 20)
    )
    return imagen


def obtener_grupos_alumno(numero_control):
    consulta = """
        SELECT registro.id_grupo,
        grupo.clave_grupo,
        materia.nombre_materia,
        CONCAT(maestros.nombre_maestro, ' ', maestros.apellido_paterno, ' ', maestros.apellido_materno) AS nombre_maestro
        FROM registro
        JOIN grupo   ON registro.id_grupo       = grupo.id_grupo
        JOIN materia ON grupo.id_materia        = materia.id_materia
        JOIN maestro maestros ON grupo.id_maestro = maestros.id_maestro
        JOIN alumno A ON registro.id_alumno = A.id_alumno
        WHERE A.numero_control = %s
    """
    return ejecutar_select(consulta, (numero_control,))


def Mis_Clases(frame_contenido):
    global numero_control_alumno
    limpiar_frame(frame_contenido)

    CTkLabel(
        frame_contenido,
        text="Mis Clases",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 30)
    ).pack(fill="x", anchor="w", pady=10, padx=10)

    # Texto pequeño debajo de "Mis Clases"
    CTkLabel(
        frame_contenido,
        text="Gestiona y accede a tus cursos",
        text_color="gray",
        font=("Arial", 16)
    ).pack(anchor="w", padx=12, pady=(0, ))

    frame_clases = CTkScrollableFrame(
        frame_contenido,
        fg_color="#fbf8fd",
        width=1200,
        height=700,
        scrollbar_fg_color="#fbf8fd",
        scrollbar_button_color="#fbf8fd",
        scrollbar_button_hover_color="#fbf8fd"
    )
    frame_clases.pack(pady=(5, 10), padx=10, anchor="w")
    frame_clases.pack_propagate(False)

    if numero_control_alumno is None:
        CTkLabel(
            frame_clases,
            text="No se encontró el alumno actual.",
            text_color="black",
            anchor="w",
            font=("Arial Rounded MT Bold", 20)
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        return

    grupos = obtener_grupos_alumno(numero_control_alumno)

    if not grupos:
        CTkLabel(
            frame_clases,
            text="No tienes clases registradas.",
            text_color="black",
            anchor="w",
            font=("Arial Rounded MT Bold", 20)
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        return

    # máximo 6 por fila
    for i, (id_grupo, clave_grupo, nombre_materia, nombre_maestro) in enumerate(grupos):
        fila = i // 6
        columna = i % 6
        crear_icono_clases(
            frame_clases,
            columna,
            fila,
            clave_grupo,
            nombre_maestro,
            nombre_materia,
            frame_contenido,
            id_grupo
        )


def calendario(frame):
    global numero_control_alumno
    limpiar_frame(frame)

    CTkLabel(
        frame,
        text="Calendario",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 30)
    ).pack(fill="x", anchor="w", pady=10, padx=10)
    CTkLabel(
        frame,
        text="Consulta tus actividades y tareas pendientes",
        text_color="gray",
        font=("Arial", 16)
    ).pack(anchor="w", padx=12, pady=(0, 10))

    label_estado_tareas = CTkLabel(
        frame,
        text="",
        text_color="gray",
        anchor="w",
        justify="left",
        font=("Arial", 16)
    )
    label_estado_tareas.pack(fill="x", anchor="w", padx=12, pady=(0, 8))

    frame_calendario = CTkFrame(
        frame, fg_color="white", width=1200, height=500)
    frame_calendario.pack(pady=10, padx=20)
    frame_calendario.pack_propagate(False)

    hoy = datetime.date.today()

    cal = Calendar(
        frame_calendario,
        selectmode="day",
        year=hoy.year,
        month=hoy.month,
        day=hoy.day,
        font=("Arial Rounded MT Bold", 14),
        background="#715a72",
        foreground="white",
        headersbackground="#5e485f",
        headersforeground="white",
        normalbackground="#cabece",
        normalforeground="white",
        weekendbackground="#cabece",
        weekendforeground="white",
        selectbackground="#5e485f",
        selectforeground="white",
        bordercolor="#715a72"
    )
    cal.pack(fill="both", expand=True, padx=10, pady=10)

    frame_tareas_dia = CTkFrame(
        frame,
        fg_color="white",
        width=1200,
        height=180
    )
    frame_tareas_dia.pack(pady=(0, 10), padx=20)
    frame_tareas_dia.pack_propagate(False)

    consulta = """
        SELECT
        COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre') AS nombre_actividad,
        COALESCE(NULLIF(TRIM(A.descripcion), ''), A.nombre_actividad) AS descripcion,
        CONCAT('Grupo ', TRIM(G.id_grupo)) AS nombre_grupo,
        COALESCE(M.nombre_materia, 'Sin materia') AS nombre_materia,
        A.fecha_entrega,
        MAX(RES.fecha_registro) AS fecha_entrega_alumno
        FROM registro R
        JOIN grupo G ON TRIM(R.id_grupo) = TRIM(G.id_grupo)
        JOIN Actividad A ON TRIM(A.id_grupo) = TRIM(G.id_grupo)
        LEFT JOIN materia M ON G.id_materia = M.id_materia
        LEFT JOIN resultado RES ON RES.id_registro = R.id_registro
        AND RES.id_actividad = A.id_actividad
        JOIN alumno AL ON R.id_alumno = AL.id_alumno
        WHERE TRIM(AL.numero_control) = TRIM(%s)
        GROUP BY A.id_actividad, COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre'),
        COALESCE(NULLIF(TRIM(A.descripcion), ''), A.nombre_actividad), CONCAT('Grupo ', TRIM(G.id_grupo)),
        COALESCE(M.nombre_materia, 'Sin materia'), A.fecha_entrega
        ORDER BY A.fecha_entrega ASC
    """
    tareas = ejecutar_select(consulta, (numero_control_alumno,))

    if not tareas:
        label_estado_tareas.configure(text="Sin actividades por entregar")
        return cal

    tareas_por_fecha = {}
    primera_clave_fecha = None

    def normalizar_fecha(valor):
        if isinstance(valor, datetime.datetime):
            return valor.date()
        if isinstance(valor, datetime.date):
            return valor
        if isinstance(valor, str):
            for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%y", "%d/%m/%y", "%m/%d/%Y", "%d/%m/%Y"):
                try:
                    return datetime.datetime.strptime(valor, fmt).date()
                except ValueError:
                    continue
        return None

    def clave_fecha(valor):
        fecha = normalizar_fecha(valor)
        return fecha.isoformat() if fecha else None

    for nombre_actividad, descripcion, nombre_grupo, nombre_materia, fecha_entrega, fecha_entrega_alumno in tareas or []:
        fecha = normalizar_fecha(fecha_entrega)
        clave = clave_fecha(fecha_entrega)
        if fecha is None or clave is None:
            continue

        fecha_limite = fecha_entrega
        fecha_envio = fecha_entrega_alumno

        if isinstance(fecha_limite, datetime.date) and not isinstance(fecha_limite, datetime.datetime):
            fecha_limite = datetime.datetime.combine(
                fecha_limite, datetime.time(23, 59, 59))
        elif isinstance(fecha_limite, str):
            try:
                fecha_limite = datetime.datetime.fromisoformat(fecha_limite)
            except ValueError:
                try:
                    fecha_limite = datetime.datetime.strptime(
                        fecha_limite, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    fecha_limite = datetime.datetime.strptime(
                        fecha_limite, "%Y-%m-%d")

        if isinstance(fecha_envio, str):
            try:
                fecha_envio = datetime.datetime.fromisoformat(fecha_envio)
            except ValueError:
                try:
                    fecha_envio = datetime.datetime.strptime(
                        fecha_envio, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    fecha_envio = None

        if fecha_envio is None:
            estado_entrega = "SIN ENTREGAR"
        elif isinstance(fecha_limite, datetime.datetime) and fecha_envio <= fecha_limite:
            estado_entrega = "ENTREGADA"
        else:
            estado_entrega = "ENTREGA CON RETRASO"

        tareas_por_fecha.setdefault(clave, []).append(
            (nombre_actividad, descripcion, nombre_grupo,
             nombre_materia, estado_entrega)
        )

        if primera_clave_fecha is None or clave < primera_clave_fecha:
            primera_clave_fecha = clave

    if tareas_por_fecha:
        for fecha_iso in tareas_por_fecha.keys():
            fecha = datetime.date.fromisoformat(fecha_iso)
            cal.calevent_create(fecha, "", "actividad")
        cal.tag_config("actividad", background="#715a72", foreground="white")

        primera_fecha = datetime.date.fromisoformat(primera_clave_fecha)
        cal.selection_set(primera_fecha)
        cal.see(primera_fecha)

    label_estado_tareas.configure(
        text=f"Total de actividades encontradas: {sum(len(v) for v in tareas_por_fecha.values())}"
    )

    def mostrar_tareas_del_dia(_event=None):
        for widget in frame_tareas_dia.winfo_children():
            widget.destroy()

        clave_seleccionada = clave_fecha(cal.selection_get())
        if clave_seleccionada is None:
            clave_seleccionada = clave_fecha(cal.get_date())
        if clave_seleccionada is None:
            clave_seleccionada = primera_clave_fecha

        tareas_dia = tareas_por_fecha.get(clave_seleccionada, [])

        if not tareas_dia and primera_clave_fecha:
            tareas_dia = tareas_por_fecha.get(primera_clave_fecha, [])

        if not tareas_dia:
            CTkLabel(
                frame_tareas_dia,
                text="No hay actividades para la fecha seleccionada.",
                text_color="gray",
                anchor="w",
                justify="left",
                font=("Arial", 16)
            ).pack(fill="x", anchor="w", padx=10, pady=10)
            return

        for nombre_actividad, descripcion, nombre_grupo, nombre_materia, estado_entrega in tareas_dia:
            CTkLabel(
                frame_tareas_dia,
                text=f"Nombre: {nombre_actividad}",
                text_color="black",
                anchor="w",
                justify="left",
                wraplength=1100,
                font=("Arial Rounded MT Bold", 16)
            ).pack(fill="x", anchor="w", padx=10, pady=(8, 0))

            CTkLabel(
                frame_tareas_dia,
                text=f"Actividad: {descripcion}",
                text_color="black",
                anchor="w",
                justify="left",
                wraplength=1100,
                font=("Arial", 14)
            ).pack(fill="x", anchor="w", padx=10, pady=(8, 0))

            CTkLabel(
                frame_tareas_dia,
                text=f"Grupo: {nombre_grupo}",
                text_color="#4a4a4a",
                anchor="w",
                justify="left",
                wraplength=1100,
                font=("Arial", 14, "italic")
            ).pack(fill="x", anchor="w", padx=10, pady=(0, 2))

            CTkLabel(
                frame_tareas_dia,
                text=f"Materia: {nombre_materia}",
                text_color="#4a4a4a",
                anchor="w",
                justify="left",
                wraplength=1100,
                font=("Arial", 14, "italic")
            ).pack(fill="x", anchor="w", padx=10, pady=(0, 8))

            CTkLabel(
                frame_tareas_dia,
                text=f"Estado: {estado_entrega}",
                text_color="#333333",
                anchor="w",
                justify="left",
                wraplength=1100,
                font=("Arial Rounded MT Bold", 14)
            ).pack(fill="x", anchor="w", padx=10, pady=(0, 10))

    cal.bind("<<CalendarSelected>>", mostrar_tareas_del_dia)
    mostrar_tareas_del_dia()

    return cal


def tareas_pendientes(frame):
    global numero_control_alumno, frame_contenido
    limpiar_frame(frame)

    CTkLabel(
        frame,
        text="Tareas Pendientes",
        text_color="black",
        anchor="w",
        font=("Arial Rounded MT Bold", 30)
    ).pack(fill="x", anchor="w", pady=10, padx=10)

    CTkLabel(
        frame,
        text="Consulta tus actividades por materia",
        text_color="gray",
        anchor="w",
        font=("Arial", 16)
    ).pack(fill="x", anchor="w", padx=12, pady=(0, 10))

    contenedor = CTkScrollableFrame(
        frame,
        fg_color="white",
        width=1200,
        height=700,
        scrollbar_fg_color="white",
        scrollbar_button_color="white",
        scrollbar_button_hover_color="white"
    )
    contenedor.pack(padx=10, pady=(0, 10), fill="both", expand=True)

    grupos = obtener_grupos_alumno(numero_control_alumno)

    if not grupos:
        CTkLabel(
            contenedor,
            text="No tienes clases registradas.",
            text_color="black",
            anchor="w",
            font=("Arial Rounded MT Bold", 20)
        ).pack(fill="x", padx=10, pady=10)
        return

    consulta_tareas = """
        SELECT DISTINCT
        TRIM(A.id_grupo) AS id_grupo,
        COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre') AS nombre_actividad,
        A.fecha_entrega,
        MAX(RES.fecha_registro) AS fecha_entrega_alumno
        FROM registro R
        JOIN Actividad A ON TRIM(A.id_grupo) = TRIM(R.id_grupo)
        LEFT JOIN resultado RES ON RES.id_registro = R.id_registro
        AND RES.id_actividad = A.id_actividad
        JOIN alumno AL ON R.id_alumno = AL.id_alumno
        WHERE TRIM(AL.numero_control) = TRIM(%s)
        GROUP BY A.id_actividad, TRIM(A.id_grupo), COALESCE(NULLIF(TRIM(A.nombre_actividad), ''), 'Actividad sin nombre'), A.fecha_entrega
        ORDER BY A.fecha_entrega ASC
    """
    filas_tareas = ejecutar_select(
        consulta_tareas, (numero_control_alumno,)) or []

    tareas_por_grupo = {}

    for id_grupo, nombre_actividad, fecha_entrega, fecha_entrega_alumno in filas_tareas:
        fecha_limite = fecha_entrega
        fecha_envio = fecha_entrega_alumno

        if isinstance(fecha_entrega, datetime.datetime):
            fecha_limite = fecha_entrega
        elif isinstance(fecha_entrega, str):
            try:
                fecha_limite = datetime.datetime.fromisoformat(fecha_entrega)
            except ValueError:
                try:
                    fecha_limite = datetime.datetime.strptime(
                        fecha_entrega, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        fecha_limite = datetime.datetime.strptime(
                            fecha_entrega, "%Y-%m-%d")
                    except ValueError:
                        continue

        if isinstance(fecha_envio, str):
            try:
                fecha_envio = datetime.datetime.fromisoformat(fecha_envio)
            except ValueError:
                try:
                    fecha_envio = datetime.datetime.strptime(
                        fecha_envio, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    fecha_envio = None

        if isinstance(fecha_limite, datetime.date) and not isinstance(fecha_limite, datetime.datetime):
            fecha_limite = datetime.datetime.combine(
                fecha_limite, datetime.time(23, 59, 59))

        if not isinstance(fecha_limite, datetime.datetime):
            continue

        if fecha_envio is None:
            estado_entrega = "SIN ENTREGAR"
        elif fecha_envio <= fecha_limite:
            estado_entrega = "ENTREGADA"
        else:
            estado_entrega = "ENTREGA CON RETRASO"

        tareas_por_grupo.setdefault(id_grupo, []).append(
            (nombre_actividad, estado_entrega))

    for id_grupo, nombre_materia, nombre_maestro in grupos:
        frame_bloque = CTkFrame(contenedor, fg_color="white")
        frame_bloque.pack(fill="x", padx=5, pady=6)

        titulo = f"{nombre_materia} - Grupo {id_grupo}"
        frame_desplegable = CTkFrame(frame_bloque, fg_color="#f4eef6")
        desplegado = {"activo": False}

        def alternar_menu(panel=frame_desplegable, estado=desplegado):
            if estado["activo"]:
                panel.pack_forget()
                estado["activo"] = False
            else:
                panel.pack(fill="x", padx=0, pady=(0, 5))
                estado["activo"] = True

        CTkButton(
            frame_bloque,
            text=titulo,
            anchor="w",
            fg_color="#715a72",
            hover_color="#5e485f",
            text_color="white",
            font=("Arial Rounded MT Bold", 18),
            command=alternar_menu
        ).pack(fill="x")

        tareas_grupo = tareas_por_grupo.get(id_grupo, [])

        if tareas_grupo:
            for nombre_actividad, estado_entrega in tareas_grupo:
                fila = CTkFrame(frame_desplegable, fg_color="#f4eef6")
                fila.pack(fill="x", padx=10, pady=(6, 0))

                CTkLabel(
                    fila,
                    text=nombre_actividad,
                    text_color="black",
                    anchor="w",
                    justify="left",
                    wraplength=780,
                    font=("Arial Rounded MT Bold", 14)
                ).pack(side="left", fill="x", expand=True)

                CTkLabel(
                    fila,
                    text=estado_entrega,
                    text_color="#333333",
                    anchor="e",
                    justify="right",
                    font=("Arial", 14, "italic")
                ).pack(side="right", padx=(10, 0))
        else:
            CTkLabel(
                frame_desplegable,
                text="NO hay tareas asignadas por ahora",
                text_color="gray",
                anchor="w",
                justify="left",
                font=("Arial", 14)
            ).pack(fill="x", padx=10, pady=(8, 0))

        CTkButton(
            frame_desplegable,
            text="Ir al grupo",
            fg_color="#715a72",
            hover_color="#5e485f",
            text_color="white",
            font=("Arial Rounded MT Bold", 14),
            command=lambda m=nombre_materia, p=nombre_maestro, g=f"Grupo {id_grupo}":
                grupos_alumno.Info_Grupo(
                    frame_contenido, m, p, g, numero_control_alumno)
        ).pack(anchor="e", padx=10, pady=(8, 10))


def iniciar_alumno(numero_control):
    global ventana, frame_contenido, img_hogar, img_calendario, img_notificaciones, img_pendiente, img_cerrar_sesion, img_usuario
    global numero_control_alumno, nombre_alumno

    # Guardar número de control para usarlo en toda la vista
    numero_control_alumno = numero_control

    # Consultar nombre del alumno en la base de datos
    consulta_alumno = """
        SELECT nombre_alumno, apellido_paterno, apellido_materno
        FROM alumno
        WHERE numero_control = %s
    """
    resultado = ejecutar_select(consulta_alumno, (numero_control_alumno,))
    if resultado:
        nombre, ap_paterno, ap_materno = resultado[0]
        nombre_alumno = f"{nombre} {ap_paterno} {ap_materno}"
    else:
        nombre_alumno = None
    ventana = CTk(fg_color="white")
    ventana.title("Inicio Alumnos")
    # Mostrar y maximizar antes de crear recursos gráficos para evitar
    # errores de imagen vinculados a la instancia Tk
    mostrar_maximizada()

    img_hogar = crear_icono(
        "ui/carpeta_iconos/iconos_alumnos/hogar.png")
    img_calendario = crear_icono(
        "ui/carpeta_iconos/iconos_alumnos/calendario.png")
    img_notificaciones = crear_icono("ui/carpeta_iconos/iconos_alumnos/reloj.png")
    img_pendiente = crear_icono("ui/carpeta_iconos/iconos_alumnos/lista.png")
    img_cerrar_sesion = crear_icono("ui/carpeta_iconos/iconos_alumnos/salida.png")
    img_usuario = crear_icono("ui/carpeta_iconos/iconos_alumnos/avatar.png")

    frame_menu = CTkFrame(ventana,
                          width=300,
                          corner_radius=0,
                          fg_color="#cabece")
    frame_menu.pack(side="left", fill="y")
    frame_menu.pack_propagate(False)

    frame_contenido = CTkFrame(ventana,
                               fg_color="white")
    frame_contenido.pack(side="left", pady=10, padx=20,
                         fill="both", expand=True)

    menu_opcioneas(frame_menu)
    Mis_Clases(frame_contenido)

    ventana.mainloop()
