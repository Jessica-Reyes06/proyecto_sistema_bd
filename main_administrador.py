import os
import sys

from customtkinter import *
import customtkinter
from PIL import Image
from funciones_login import cambiar_modo
from funciones_admin import *

ventana_principal = None


def ruta_recurso(ruta_relativa):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, ruta_relativa)


def crear_icono(ruta, size=(20, 20)):
    return CTkImage(
        light_image=Image.open(ruta_recurso(ruta)),
        size=size
    )


def iniciar_admin():
    global ventana_principal

    # ===== CONFIGURACIÓN =====

    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("blue")

    ventana_principal = customtkinter.CTk()
    ventana_principal.title("Panel Administrador")

    ventana_principal.withdraw()

    def mostrar_max_admin():
        ventana_principal.deiconify()
        ventana_principal.state("zoomed")

    ventana_principal.after(10, mostrar_max_admin)

    # tamaño mínimo para evitar romper el layout
    ventana_principal.minsize(1100, 700)

    # ===== ESCALADO AUTOMÁTICO SEGÚN PANTALLA =====

    screen_w = ventana_principal.winfo_screenwidth()

    if screen_w >= 1900:
        customtkinter.set_widget_scaling(1.3)
    elif screen_w >= 1500:
        customtkinter.set_widget_scaling(1.15)
    else:
        customtkinter.set_widget_scaling(1.0)

    # ===== GRID PRINCIPAL =====

    ventana_principal.grid_columnconfigure(0, weight=0)  # sidebar fijo
    ventana_principal.grid_columnconfigure(1, weight=1)  # contenido crece
    ventana_principal.grid_rowconfigure(0, weight=1)

    # ===== SIDEBAR =====

    sidebar = customtkinter.CTkFrame(ventana_principal, width=220, fg_color="#003152")
    sidebar.grid(row=0, column=0, sticky="ns")

    logo_img = CTkImage(light_image=Image.open(ruta_recurso("carpeta_iconos/general/logo.jpeg")), size=(180, 60))
    customtkinter.CTkLabel(
        sidebar,
        text="",
        image=logo_img
    ).pack(pady=(20, 5))

    # Avatar en la parte superior del panel izquierdo
    avatar_image = CTkImage(
        light_image=Image.open(ruta_recurso("carpeta_iconos/iconos_admin/usuario.png")),
        size=(100, 100)
    )
    customtkinter.CTkLabel(
        sidebar,
        text="",
        image=avatar_image
    ).pack(pady=(5, 5))

    customtkinter.CTkLabel(
        sidebar,
        text="¡Hola de nuevo! 😊",
        font=("Arial Rounded MT Bold", 20),
        text_color="#ffffff"
    ).pack(pady=10)

    # Iconos para los botones del sidebar (como en Inicio_Alumnos)
    img_inicio = crear_icono(ruta_recurso("carpeta_iconos/iconos_alumnos/hogar.png"), (24, 24))
    img_cerrar_sesion = crear_icono(ruta_recurso("carpeta_iconos/iconos_alumnos/salida.png"), (24, 24))
    img_modo = crear_icono(ruta_recurso("carpeta_iconos/iconos_alumnos/modo.png"), (24, 24))
    img_calendario = crear_icono(ruta_recurso("carpeta_iconos/iconos_alumnos/calendario.png"), (24, 24))
    img_pendientes = crear_icono(ruta_recurso("carpeta_iconos/iconos_alumnos/lista.png"), (24, 24))
    img_notificaciones = crear_icono(ruta_recurso("carpeta_iconos/iconos_alumnos/reloj.png"), (24, 24))
    img_respaldo = crear_icono(ruta_recurso("carpeta_iconos/iconos_alumnos/archivo-de-carpetas.png"), (24, 24))

    # Frame clickeable para "Inicio"
    frame_inicio = customtkinter.CTkFrame(sidebar, fg_color="transparent")
    frame_inicio.pack(pady=10, padx=20, fill="x")

    # ===== AREA PRINCIPAL =====
    main_frame = customtkinter.CTkFrame(ventana_principal, fg_color="transparent")
    main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    btn_inicio = customtkinter.CTkButton(
        frame_inicio,
        text="   Inicio",
        fg_color="#003152",
        hover_color="#1c669f",
        text_color="white",
        width=150,
        height=40,
        image=img_inicio,
        anchor="w",
        command=lambda: mostrar_dashboard(main_frame)
    )
    btn_inicio.pack()

    # Hacer que todo el frame también sea clickeable
    frame_inicio.bind("<Button-1>", lambda event: mostrar_dashboard(main_frame))

    # Botón "Calendario"
    frame_cal = customtkinter.CTkFrame(sidebar, fg_color="transparent")
    frame_cal.pack(pady=5, padx=20, fill="x")

    btn_cal = customtkinter.CTkButton(
        frame_cal,
        text="   Calendario",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=150,
        height=40,
        image=img_calendario,
        anchor="w",
        command=lambda: mostrar_calendario_imagen(main_frame)
    )
    btn_cal.pack(fill="x")

    frame_cal.bind("<Button-1>", lambda event: mostrar_calendario_imagen(main_frame))

    # Botón "Pendientes"
    frame_pend = customtkinter.CTkFrame(sidebar, fg_color="transparent")
    frame_pend.pack(pady=5, padx=20, fill="x")

    btn_pend = customtkinter.CTkButton(
        frame_pend,
        text="   Pendientes",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=150,
        height=40,
        image=img_pendientes,
        anchor="w",
        command=lambda: mostrar_pendientes(main_frame)
    )
    btn_pend.pack(fill="x")

    frame_pend.bind("<Button-1>", lambda event: mostrar_pendientes(main_frame))

    # Botón "Notificaciones"
    frame_notif = customtkinter.CTkFrame(sidebar, fg_color="transparent")
    frame_notif.pack(pady=5, padx=20, fill="x")

    btn_notif = customtkinter.CTkButton(
        frame_notif,
        text="   Notificaciones",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=150,
        height=40,
        image=img_notificaciones,
        anchor="w",
        command=lambda: mostrar_notificaciones(main_frame)
    )
    btn_notif.pack(fill="x")

    frame_notif.bind("<Button-1>", lambda event: mostrar_notificaciones(main_frame))

    # Frame clickeable para cambiar modo oscuro/claro
    frame_modo = customtkinter.CTkFrame(sidebar, fg_color="transparent")
    frame_modo.pack(pady=5, padx=20, fill="x")

    btn_modo = customtkinter.CTkButton(
        frame_modo,
        text="   Cambiar modo",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=150,
        height=40,
        anchor="w",
        command=cambiar_modo,
        image=img_modo
    )
    btn_modo.pack(fill="x")

    frame_modo.bind("<Button-1>", lambda event: cambiar_modo())

    # Botón "Crear respaldo"
    frame_respaldo = customtkinter.CTkFrame(sidebar, fg_color="transparent")
    frame_respaldo.pack(pady=5, padx=20, fill="x")

    btn_respaldo = customtkinter.CTkButton(
        frame_respaldo,
        text="   Crear respaldo",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=150,
        height=40,
        image=img_respaldo,
        anchor="w",
        command=crear_respaldo_completo,
    )
    btn_respaldo.pack(fill="x")

    frame_respaldo.bind("<Button-1>", lambda event: crear_respaldo_completo())

    # Botón "Restaurar respaldo"
    frame_restaurar = customtkinter.CTkFrame(sidebar, fg_color="transparent")
    frame_restaurar.pack(pady=5, padx=20, fill="x")

    btn_restaurar = customtkinter.CTkButton(
        frame_restaurar,
        text="   Rest. respaldo",
        fg_color="transparent",
        hover_color="#1c669f",
        text_color="white",
        width=150,
        height=40,
        image=img_respaldo,
        anchor="w",
        command=restaurar_desde_respaldo,
    )
    btn_restaurar.pack(fill="x")

    frame_restaurar.bind("<Button-1>", lambda event: restaurar_desde_respaldo())

    # "Cerrar sesión"
    frame_cerrar = customtkinter.CTkFrame(sidebar, fg_color="transparent")
    frame_cerrar.pack(side="bottom", pady=20, padx=20, fill="x")

    btn_cerrar = customtkinter.CTkButton(
        frame_cerrar,
        text="   Cerrar sesión",
        fg_color="transparent",
        hover_color="#962d22",
        text_color="white",
        width=150,
        height=40,
        image=img_cerrar_sesion,
        anchor="w",
        command=ventana_principal.destroy
    )
    btn_cerrar.pack(fill="x")

    frame_cerrar.bind("<Button-1>", lambda event: ventana_principal.destroy())

    mostrar_dashboard(main_frame)

    ventana_principal.mainloop()


from funciones_admin import mostrar_horarios

if __name__ == "__main__":
    iniciar_admin()
