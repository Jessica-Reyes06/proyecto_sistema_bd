from customtkinter import CTkFrame, CTkButton
from tkcalendar import Calendar
import datetime


def limpiar_frame(frame):
	"""Elimina todos los widgets hijos de un frame"""
	for widget in frame.winfo_children():
		widget.destroy()


def crear_tarjeta(parent, titulo, comando, boton_color=None, icono=None):
	"""Crea una "tarjeta" con un botón grande centrado."""
	marco = CTkFrame(
		parent,
		fg_color="#ffffff",
		corner_radius=10
	)

	boton = CTkButton(
		marco,
		text=titulo,
		width=170,
		height=130,
		command=comando,
		fg_color=boton_color,
		font=("Arial", 18, "bold"),
		image=icono,
		compound="top"
	)
	boton.pack(padx=8, pady=8)

	return marco


def calendario(frame):
	"""Calendario reutilizable para el panel administrador.

	Crea un calendario compacto dentro del frame que se le pasa,
	sin limpiar el frame padre (eso lo hace quien llama).
	"""

	contenedor = CTkFrame(frame, fg_color="white")
	contenedor.pack(fill="both", expand=True, padx=5, pady=5)

	hoy = datetime.date.today()

	cal = Calendar(
		contenedor,
		selectmode="day",
		year=hoy.year,
		month=hoy.month,
		day=hoy.day,
		font=("Arial Rounded MT Bold", 20),
		background="#a4d6ff",
		foreground="white",
		headersbackground="#a4d6ff",
		headersforeground="white",
		normalbackground="#cabece",
		normalforeground="white",
		weekendbackground="#cabece",
		weekendforeground="white",
		selectbackground="#a4d6ff",
		selectforeground="white",
		bordercolor="#a4d6ff",
	)

	cal.pack(fill="both", expand=True, padx=5, pady=5)

	return cal

