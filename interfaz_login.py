import os
import sys  
import importlib

from customtkinter import *
from funciones_login import mostrar_ocultar, generar_mensaje_login
from PIL import Image


def ruta_recurso(ruta_relativa):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, ruta_relativa)

set_appearance_mode("light")
ventana_login = CTk()
ventana_login.title("Sistema de Registro Escolar")
ventana_login.geometry("400x450+700+300")
ventana_login.resizable(False, False)


fondo = CTkImage(Image.open(ruta_recurso("carpeta_iconos/general/login.jpg")), size=(400, 450))
label_fondo = CTkLabel(ventana_login, image=fondo, text="", fg_color="transparent")
label_fondo.place(x=0, y=0, relwidth=1, relheight=1)

frame = CTkFrame(ventana_login, width=380, height=320, fg_color="white")
frame.pack(expand=True, fill= "both", padx=50, pady=80)

etiqueta_bienvenida = CTkLabel(frame, text="¡Bienvenido!", font=("Helvetica", 16), text_color="black")
etiqueta_bienvenida.pack(pady=(20, 5))

entry_usuario = CTkEntry(frame, width=220, placeholder_text="Ingrese su usuario")
entry_usuario.pack( pady=(30,10))

entry_contra = CTkEntry(frame, width=220, show="*", placeholder_text="Ingrese su contraseña")
entry_contra.pack(pady=(0, 10))

# Botón para mostrar/ocultar contraseña, debajo de la entrada
boton_contra = CTkButton(frame, text="Mostrar contraseña", fg_color="#314560")
boton_contra.pack(pady=(20, 5))

boton_contra.configure(command=lambda: mostrar_ocultar(entry_contra, boton_contra))


def abrir_interfaz_maestro(usuario):
    try:
        modulo = importlib.import_module("codigo_maestros.Inicio_maestros")
    except Exception:
        modulo = importlib.import_module("Inicio_maestros")

    iniciar_maestro = getattr(modulo, "iniciar_maestro", None)
    if iniciar_maestro is None:
        raise ImportError("No se encontró iniciar_maestro en Inicio_maestros")

    iniciar_maestro(usuario)


def on_login():
    usuario = entry_usuario.get()
    contrasena = entry_contra.get()

    mensaje = generar_mensaje_login(usuario, contrasena)

    label_mensaje.configure(
        text=mensaje["texto"],
        fg_color=mensaje["fg_color"],
        text_color=mensaje["text_color"],
    )

    if mensaje["exitoso"] is True:
        rol = (mensaje["rol"] or "").strip().lower()
        # Abrir la plataforma según el rol
        if rol == "administrador":
            ventana_login.destroy()
            from main_administrador import iniciar_admin
            iniciar_admin()
        elif rol == "alumno":
            pass
        elif rol == "maestro":
            try:
                ventana_login.destroy()
                abrir_interfaz_maestro(mensaje["usuario"])
            except Exception as ex:
                label_mensaje.configure(
                    text=f"Error al abrir la interfaz de maestro: {ex}",
                    fg_color=("#FCE1E1", "#8A1F1F"),
                    text_color=("#B00020", "#FFB3B3"),
                )
        else:
            label_mensaje.configure(
                text=f"Rol no reconocido: {mensaje['rol']}",
                fg_color=("#FCE1E1", "#8A1F1F"),
                text_color=("#B00020", "#FFB3B3"),
            )
    

boton_login = CTkButton(frame, text="Iniciar sesión", command=on_login, fg_color="#314560")
boton_login.pack(pady=(5, 0))

# Label para mensajes de validación (vacío al inicio), debajo del botón de iniciar sesión
label_mensaje = CTkLabel(frame, text="")
label_mensaje.pack(pady=(5, 0), fill="x")

ventana_login.mainloop()

