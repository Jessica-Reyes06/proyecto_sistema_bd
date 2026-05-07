from customtkinter import CTkFrame, CTkButton
from tkcalendar import Calendar
import datetime


def limpiar_frame(frame):
	"""Elimina todos los widgets hijos de un frame"""
	for widget in frame.winfo_children():
		widget.destroy()

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
		background="#ffffff",
		foreground="#000000",
		headersbackground="#ffffff",
		headersforeground="#000000",
		normalbackground="#ffffff",
		normalforeground="#000000",
		weekendbackground="#ffffff",
		weekendforeground="#000000",
		selectbackground="#d9d9d9",
		selectforeground="#000000",
		bordercolor="#ffffff",
	)

	cal.pack(fill="both", expand=True, padx=5, pady=5)

	return cal

