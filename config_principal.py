from customtkinter import CTkFrame, CTkButton, CTkScrollableFrame, CTkLabel
from tkcalendar import Calendar
from funciones_auditoria import obtener_ultimos_cambios


def limpiar_frame(frame):
	"""Elimina todos los widgets hijos de un frame"""
	for widget in frame.winfo_children():
		widget.destroy()

def bitacora_cambios(frame):
	"""Muestra una lista con los ultimos cambios registrados en la bitácora de auditoría"""

	contenedor = CTkFrame(frame, fg_color="white")
	contenedor.pack(fill="both", expand=True, padx=5, pady=5)

	contenedor.columnconfigure(0, weight=1)
	contenedor.columnconfigure(1, weight=0)

	titulo = CTkLabel(contenedor, text="🗓 Bitácora de Cambios", font=("Arial", 16, "bold"))
	titulo.grid(pady=10, padx=10, sticky="w", column=0, row=0)

	boton_refresh = CTkButton(contenedor, text="↻", width=20, command=lambda: mostrar_cambios())
	boton_refresh.grid(pady=10, padx=10, sticky="w", column=1, row=0)

	contenedor_cambios = CTkScrollableFrame(contenedor, fg_color="transparent", width=300)
	contenedor_cambios.grid(pady=0, padx=5, sticky="nsew", column=0, row=1, columnspan=2)

	def mostrar_cambios():
		# Obtener cambios CADA VEZ que se presiona refresh
		cambios = obtener_ultimos_cambios(20)
		
		for widget in contenedor_cambios.winfo_children():
			widget.destroy()

		for admin, tabla, operacion, descripcion, fecha_hora in cambios:
			texto = f"{fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}: {descripcion}"
			label_cambio = CTkLabel(contenedor_cambios, wraplength=300, height=50, fg_color="#f0f4f8", text=texto, anchor="w", justify="left")
			label_cambio.pack(fill="x", padx=5, pady=5)
	
	mostrar_cambios()
	
	

