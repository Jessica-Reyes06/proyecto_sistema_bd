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
ventana_login.geometry("1320x820+120+60")
ventana_login.minsize(1320, 820)
ventana_login.configure(fg_color="#e8eef4")

# ── BARRA SUPERIOR ────────────────────────────────────────────────────────────
barra_top = CTkFrame(ventana_login, fg_color="white", height=120, corner_radius=0)
barra_top.pack(fill="x", side="top")
barra_top.pack_propagate(False)


logo_tecnm = CTkImage(Image.open(ruta_recurso("carpeta_iconos/general/logo_tecnm.png")), size=(190, 94))
CTkLabel(barra_top, image=logo_tecnm, text="", fg_color="transparent").pack(side="left", padx=(26, 6), pady=(12,2))


CTkFrame(barra_top, width=1, height=40, fg_color="#d1d5db").pack(side="left", padx=16, pady=12)

CTkLabel(barra_top, text="Portal Académico\nSistema de Gestión",
         font=("Arial", 20), text_color="#374151",
         fg_color="transparent", justify="right").pack(side="right", padx=24, pady=10)

CTkFrame(ventana_login, height=1, fg_color="#d1d5db").pack(fill="x")

# ── ÁREA CENTRAL ──────────────────────────────────────────────────────────────
area_central = CTkFrame(ventana_login, fg_color="#e8eef4", corner_radius=0)
area_central.pack(fill="both", expand=True)

# ── TARJETA CENTRADA ──────────────────────────────────────────────────────────
contenedor = CTkFrame(area_central, fg_color="white", corner_radius=16, width=1180, height=700)
contenedor.place(relx=0.5, rely=0.5, anchor="center")

# ── PANEL IZQUIERDO (azul sólido) ─────────────────────────────────────────────
panel_izq = CTkFrame(contenedor, fg_color="#153274", corner_radius=12, width=450)
panel_izq.pack(side="left", fill="y", padx=8, pady=8)
panel_izq.pack_propagate(False)

# Frame interno para centrar verticalmente
centro_izq = CTkFrame(panel_izq, fg_color="transparent")
centro_izq.place(relx=0.5, rely=0.5, anchor="center")

try:
    logo_img = CTkImage(Image.open(ruta_recurso("carpeta_iconos/general/itver.png")), size=(180, 160))
    CTkLabel(centro_izq, image=logo_img, text="", fg_color="transparent").pack(pady=(0, 16))
except Exception:
    CTkLabel(centro_izq, text="🏫", font=("Arial", 64), fg_color="transparent").pack(pady=(0, 16))

CTkLabel(centro_izq, text="Instituto Tecnológico\nde Veracruz",
         font=("Arial", 26, "bold"), text_color="white",
         fg_color="transparent", justify="center").pack(pady=(0, 12))

CTkFrame(centro_izq, height=2, width=60, fg_color="white").pack(pady=8)

CTkLabel(centro_izq, text='"Excelencia en educación tecnológica"',
         font=("Arial", 15, "italic"), text_color="#a8c8e8",
         fg_color="transparent", wraplength=320, justify="center").pack(pady=(0, 0))

# ── PANEL DERECHO (formulario) ────────────────────────────────────────────────
panel_der = CTkFrame(contenedor, fg_color="white", corner_radius=0)
panel_der.pack(side="left", fill="both", expand=True, padx=64)

CTkLabel(panel_der, text="Bienvenido",
         font=("Arial", 40, "bold"), text_color="#0d1b2a").pack(anchor="w", pady=(78, 10))

CTkLabel(panel_der, text="Ingresa tus credenciales para acceder al sistema",
         font=("Arial", 17), text_color="#6b7280").pack(anchor="w", pady=(0, 38))

CTkLabel(panel_der, text="Usuario", font=("Arial", 13, "bold"),
         text_color="#374151").pack(anchor="w")
entry_usuario = CTkEntry(panel_der, width=460, height=50,
                         placeholder_text="Ingresa tu usuario",
                         border_color="#d1d5db", fg_color="white",
                         text_color="black")
entry_usuario.pack(anchor="w", pady=(7, 20))

CTkLabel(panel_der, text="Contraseña", font=("Arial", 13, "bold"),
         text_color="#374151").pack(anchor="w")
entry_contra = CTkEntry(panel_der, width=460, height=50, show="*",
                        placeholder_text="Ingresa tu contraseña",
                        border_color="#d1d5db", fg_color="white",
                        text_color="black")
entry_contra.pack(anchor="w", pady=(4, 6))

boton_contra = CTkButton(panel_der, text="Mostrar contraseña",
                         fg_color="transparent", text_color="#153274",
                         hover_color="#f0f4f8", height=32, width=230,
                         font=("Arial", 15))
boton_contra.pack(anchor="w", pady=(0, 24))
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


boton_login = CTkButton(panel_der, text="Iniciar sesión",text_color="white", command=on_login,
                        fg_color="#153274", hover_color="#0d3b6e",
                        width=460, height=56, font=("Arial", 17, "bold"),
                        corner_radius=8)
boton_login.pack(anchor="w", pady=(0, 14))

label_mensaje = CTkLabel(panel_der, text="", fg_color="transparent",
                         font=("Arial", 15), wraplength=430)
label_mensaje.pack(anchor="w", pady=(0, 14))

CTkFrame(panel_der, height=1, width=460, fg_color="#e5e7eb").pack(anchor="w", pady=(10, 14))

CTkLabel(panel_der, text="Soporte técnico: soporte@itver.edu.mx\n© 2026 Instituto Tecnológico de Veracruz",
         font=("Arial", 14), text_color="#9ca3af",
         fg_color="transparent", justify="center").pack(anchor="center", pady=(0, 20))

ventana_login.mainloop()