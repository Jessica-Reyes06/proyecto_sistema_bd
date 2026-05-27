import os
import sys
import customtkinter as ctk
from PIL import Image
from funciones_admin import *
from escalado_dinamico import crear_escalador

ventana_principal = None
escalador = None


def ruta_recurso(ruta_relativa):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, ruta_relativa)


def crear_icono(ruta, size=(20, 20)):
    return ctk.CTkImage(
        light_image=Image.open(ruta_recurso(ruta)),
        size=size
    )


def iniciar_admin():
    global ventana_principal, escalador

    # ===== CONFIGURACIÓN =====

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    ventana_principal = ctk.CTk()
    ventana_principal.title("Panel Administrador")

    # NO ocultar la ventana ni maximizar automáticamente
    # Dejar que el usuario decida si maximizar

    # tamaño mínimo para evitar romper el layout
    ventana_principal.minsize(1100, 700)

    # ===== ESCALADO AUTOMÁTICO SEGÚN PANTALLA =====
    screen_w = ventana_principal.winfo_screenwidth()

    if screen_w >= 1900:
        ctk.set_widget_scaling(1.3)
    elif screen_w >= 1500:
        ctk.set_widget_scaling(1.15)
    else:
        ctk.set_widget_scaling(1.0)

    # ===== INICIALIZAR ESCALADOR DINÁMICO =====
    # IMPORTANTE: Crear escalador DESPUÉS de que la ventana es visible
    escalador = crear_escalador(ventana_principal)
    info_res = escalador.get_info_resolucion()
    print(
        f"🖥️  Resolución detectada: {info_res['screen_width']}x{info_res['screen_height']} ({info_res['categoria']})")
    print(f"📏 Factor de escala: {info_res['scale_factor']:.2f}x")

    # Compartir el escalador con funciones_admin.py
    from funciones_admin import set_escalador
    set_escalador(escalador)

    # ===== GRID PRINCIPAL =====

    ventana_principal.grid_columnconfigure(0, weight=0)  # sidebar fijo
    ventana_principal.grid_columnconfigure(1, weight=1)  # contenido crece
    ventana_principal.grid_rowconfigure(0, weight=1)

    # ===== SIDEBAR =====
    # Aumentar ancho base para acomodar botones más anchos (260px base + padding)
    ancho_sidebar = escalador.get_escalado_ancho(320)
    # Limitar el ancho máximo del sidebar
    ancho_sidebar = min(ancho_sidebar, escalador.get_escalado_ancho(400))

    sidebar = ctk.CTkFrame(
        ventana_principal, width=ancho_sidebar, fg_color="#003152")
    sidebar.grid(row=0, column=0, sticky="ns")

    logo_img = ctk.CTkImage(
        light_image=Image.open(ruta_recurso(
            "carpeta_iconos/general/logo.jpeg")),
        size=(220, 78)
    )
    frame_logo = ctk.CTkFrame(
        sidebar,
        fg_color="white",
        corner_radius=0,
        width=ancho_sidebar,
        height=96
    )
    frame_logo.pack(pady=(0, 6), padx=0, fill="x")
    frame_logo.pack_propagate(False)
    ctk.CTkLabel(
        frame_logo,
        text="",
        image=logo_img
    ).pack(expand=True)

    # Avatar en la parte superior del panel izquierdo
    avatar_image = ctk.CTkImage(
        light_image=Image.open(ruta_recurso(
            "carpeta_iconos/iconos_admin/usuario.png")),
        size=(100, 100)
    )
    ctk.CTkLabel(
        sidebar,
        text="",
        image=avatar_image
    ).pack(pady=(5, 5))

    ctk.CTkLabel(
        sidebar,
        text="¡Hola de nuevo! 😊",
        font=("Arial Rounded MT Bold", 20),
        text_color="#ffffff"
    ).pack(pady=10)

    # Iconos para los botones del sidebar (como en Inicio_Alumnos)
    # Tamaños de iconos dinámicos según la resolución
    tamano_icono = escalador.get_escalado_ancho(24)
    # Limitar el tamaño máximo de los iconos
    tamano_icono = min(tamano_icono, 32)

    img_inicio = crear_icono(ruta_recurso(
        "carpeta_iconos/iconos_alumnos/hogar.png"), (tamano_icono, tamano_icono))
    img_cerrar_sesion = crear_icono(ruta_recurso(
        "carpeta_iconos/iconos_alumnos/salida.png"), (tamano_icono, tamano_icono))
    img_calendario = crear_icono(ruta_recurso(
        "carpeta_iconos/iconos_alumnos/calendario.png"), (tamano_icono, tamano_icono))
    img_pendientes = crear_icono(ruta_recurso(
        "carpeta_iconos/iconos_alumnos/lista.png"), (tamano_icono, tamano_icono))
    img_respaldo = crear_icono(ruta_recurso(
        "carpeta_iconos/iconos_alumnos/archivo-de-carpetas.png"), (tamano_icono, tamano_icono))

    # Frame clickeable para "Inicio"
    frame_inicio = ctk.CTkFrame(sidebar, fg_color="transparent")
    frame_inicio.pack(pady=10, padx=20, fill="x")

    # ===== AREA PRINCIPAL =====
    main_frame = ctk.CTkFrame(ventana_principal, fg_color="transparent")
    main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # Crear botones dinámicos con el escalador
    # Aumentar ancho base para acomodar textos largos
    ancho_boton = escalador.get_escalado_ancho(260)
    alto_boton = escalador.get_escalado_alto(40)
    tamano_fuente = escalador.get_tamano_fuente(14)

    btn_inicio = ctk.CTkButton(
        frame_inicio,
        text="   Inicio",
        fg_color="#003152",
        hover_color="#1c669f",
        text_color="white",
        width=ancho_boton,
        height=alto_boton,
        image=img_inicio,
        anchor="w",
        font=("Arial", tamano_fuente),
        command=lambda: mostrar_dashboard(main_frame)
    )
    btn_inicio.pack()

    # Hacer que todo el frame también sea clickeable
    frame_inicio.bind(
        "<Button-1>", lambda event: mostrar_dashboard(main_frame))

    # Botón "Calendario"
    frame_cal = ctk.CTkFrame(sidebar, fg_color="transparent")
    frame_cal.pack(pady=5, padx=20, fill="x")

    btn_cal = ctk.CTkButton(
        frame_cal,
        text="   Calendario",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=ancho_boton,
        height=alto_boton,
        image=img_calendario,
        anchor="w",
        font=("Arial", tamano_fuente),
        command=lambda: mostrar_calendario_imagen(main_frame)
    )
    btn_cal.pack(fill="x")

    frame_cal.bind(
        "<Button-1>", lambda event: mostrar_calendario_imagen(main_frame))

    # Botón "Solicitudes"
    frame_pend = ctk.CTkFrame(sidebar, fg_color="transparent")
    frame_pend.pack(pady=5, padx=20, fill="x")

    btn_pend = ctk.CTkButton(
        frame_pend,
        text="   Solicitudes",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=ancho_boton,
        height=alto_boton,
        image=img_pendientes,
        anchor="w",
        font=("Arial", tamano_fuente),
        command=lambda: mostrar_solicitudes(main_frame)
    )
    btn_pend.pack(fill="x")

    frame_pend.bind(
        "<Button-1>", lambda event: mostrar_solicitudes(main_frame))

    # Botón "Crear respaldo"
    frame_respaldo = ctk.CTkFrame(sidebar, fg_color="transparent")
    frame_respaldo.pack(pady=5, padx=20, fill="x")

    btn_respaldo = ctk.CTkButton(
        frame_respaldo,
        text="   Crear respaldo",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=ancho_boton,
        height=alto_boton,
        image=img_respaldo,
        anchor="w",
        font=("Arial", tamano_fuente),
        command=crear_respaldo_completo,
    )
    btn_respaldo.pack(fill="x")

    frame_respaldo.bind("<Button-1>", lambda event: crear_respaldo_completo())

    # Botón "Restaurar respaldo"
    frame_restaurar = ctk.CTkFrame(sidebar, fg_color="transparent")
    frame_restaurar.pack(pady=5, padx=20, fill="x")

    btn_restaurar = ctk.CTkButton(
        frame_restaurar,
        text="   Rest. respaldo",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=ancho_boton,
        height=alto_boton,
        image=img_respaldo,
        anchor="w",
        font=("Arial", tamano_fuente),
        command=restaurar_desde_respaldo,
    )
    btn_restaurar.pack(fill="x")

    frame_restaurar.bind(
        "<Button-1>", lambda event: restaurar_desde_respaldo())

    # "Cerrar sesión"
    frame_cerrar = ctk.CTkFrame(sidebar, fg_color="transparent")
    frame_cerrar.pack(side="bottom", pady=20, padx=20, fill="x")

    btn_cerrar = ctk.CTkButton(
        frame_cerrar,
        text="   Cerrar sesión",
        fg_color="transparent",
        hover_color="#962d22",
        text_color="white",
        width=ancho_boton,
        height=alto_boton,
        image=img_cerrar_sesion,
        anchor="w",
        font=("Arial", tamano_fuente),
        command=ventana_principal.destroy
    )
    btn_cerrar.pack(fill="x")

    frame_cerrar.bind("<Button-1>", lambda event: ventana_principal.destroy())

    # Mostrar Inicio por defecto
    mostrar_dashboard(main_frame)

    ventana_principal.mainloop()


if __name__ == "__main__":
    iniciar_admin()
