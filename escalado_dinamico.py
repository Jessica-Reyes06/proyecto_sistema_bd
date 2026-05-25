# -*- coding: utf-8 -*-
"""
Módulo de utilidades para escalado dinámico de componentes UI
Soporta resoluciones desde 1920x1080 hasta 5K Ultra Wide
"""
import tkinter as tk


class EscaladorDinamico:
    """Gestiona el escalado dinámico de componentes UI según la resolución"""

    def __init__(self, ventana):
        """
        Inicializa el escalador con la ventana principal
        :param ventana: Ventana principal de customtkinter
        """
        self.ventana = ventana
        self.screen_width = ventana.winfo_screenwidth()
        self.screen_height = ventana.winfo_screenheight()

        # Configurar resolución base (1920x1080)
        self.base_width = 1920
        self.base_height = 1080

        # Calcular factores de escala
        self.scale_x = self.screen_width / self.base_width
        self.scale_y = self.screen_height / self.base_height

        # Usar el menor factor para mantener proporción
        self.scale_factor = min(self.scale_x, self.scale_y)

    def get_escalado_ancho(self, base_width):
        """Calcula ancho escalado"""
        return int(base_width * self.scale_factor)

    def get_escalado_alto(self, base_height):
        """Calcula alto escalado"""
        return int(base_height * self.scale_factor)

    def get_tamano_fuente(self, base_size):
        """Calcula tamaño de fuente escalado"""
        # Limitar el crecimiento de fuente para que no sea demasiado grande
        scale_limitado = min(self.scale_factor, 1.5)  # Máximo 1.5x
        return max(10, int(base_size * scale_limitado))

    def get_padding(self, base_padding):
        """Calcula padding escalado"""
        return int(base_padding * self.scale_factor)

    def configurar_boton_dinamico(self, boton, ancho_min=200, ancho_max=400):
        """
        Configura un botón para que se expanda dinámicamente
        :param boton: CTkButton a configurar
        :param ancho_min: Ancho mínimo en píxeles (base 1920x1080)
        :param ancho_max: Ancho máximo en píxeles (base 1920x1080)
        """
        ancho_calculado = self.get_escalado_ancho(ancho_min)

        # Limitar el ancho máximo para pantallas ultra wide
        ancho_final = min(ancho_calculado, self.get_escalado_ancho(ancho_max))

        # Configurar el botón
        boton.configure(
            width=ancho_final,
            height=self.get_escalado_alto(40),
            font=("Arial", self.get_tamano_fuente(14))
        )

    def configurar_sidebar_dinamico(self, sidebar, ancho_base=280):
        """
        Configura el sidebar con ancho dinámico
        :param sidebar: CTkFrame del sidebar
        :param ancho_base: Ancho base del sidebar
        """
        ancho_escalado = self.get_escalado_ancho(ancho_base)
        # Limitar el ancho máximo del sidebar
        ancho_final = min(ancho_escalado, self.get_escalado_ancho(350))

        sidebar.configure(width=ancho_final)

    def crear_boton_menu(self, parent, texto, icono, comando,
                        ancho_base=200, alto_base=40,
                        fg_color="transparent", hover_color="#1c669f",
                        text_color="white"):
        """
        Crea un botón de menú con escalado dinámico
        :param parent: Frame padre
        :param texto: Texto del botón
        :param icono: Imagen del icono (CTkImage)
        :param comando: Función callback
        :param ancho_base: Ancho base
        :param alto_base: Alto base
        :param fg_color: Color de fondo
        :param hover_color: Color al pasar el mouse
        :param text_color: Color del texto
        :return: CTkButton configurado
        """
        import customtkinter as ctk

        # Frame contenedor para el botón
        frame_boton = ctk.CTkFrame(parent, fg_color="transparent")

        # Calcular dimensiones escaladas
        ancho_escalado = self.get_escalado_ancho(ancho_base)
        alto_escalado = self.get_escalado_alto(alto_base)

        # Limitar ancho máximo para botones muy largos
        ancho_final = min(ancho_escalado, self.get_escalado_ancho(350))

        # Crear el botón con dimensiones dinámicas
        boton = ctk.CTkButton(
            frame_boton,
            text=f"   {texto}",  # Espacio para el icono
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            width=ancho_final,
            height=alto_escalado,
            image=icono,
            anchor="w",  # Alineación a la izquierda
            font=("Arial", self.get_tamano_fuente(14)),
            command=comando
        )

        boton.pack(fill="x")

        # Hacer el frame clickeable también
        frame_boton.bind("<Button-1>", lambda event: comando())

        return frame_boton, boton

    def get_info_resolucion(self):
        """Retorna información sobre la resolución actual"""
        return {
            "screen_width": self.screen_width,
            "screen_height": self.screen_height,
            "scale_factor": self.scale_factor,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "categoria": self._get_categoria_resolucion()
        }

    def _get_categoria_resolucion(self):
        """Retorna la categoría de resolución"""
        if self.screen_width >= 5120:
            return "5K Ultra Wide"
        elif self.screen_width >= 3840:
            return "4K"
        elif self.screen_width >= 2560:
            return "2K / QHD"
        elif self.screen_width >= 1920:
            return "Full HD"
        else:
            return "HD"


def crear_escalador(ventana):
    """
    Función de conveniencia para crear un escalador dinámico
    :param ventana: Ventana principal de customtkinter
    :return: Instancia de EscaladorDinamico
    """
    return EscaladorDinamico(ventana)
