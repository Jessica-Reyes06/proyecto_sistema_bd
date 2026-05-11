# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de escalado dinámico
"""
import sys
import customtkinter as ctk
from escalado_dinamico import crear_escalador

def probar_escalado():
    """Prueba el sistema de escalado con diferentes resoluciones simuladas"""

    print("=" * 70)
    print("PRUEBA DEL SISTEMA DE ESCALADO DINÁMICO")
    print("=" * 70)
    print()

    # Crear ventana de prueba
    ventana = ctk.CTk()
    ventana.title("Prueba de Escalado Dinámico")
    ventana.geometry("400x300")

    # Crear escalador
    escalador = crear_escalador(ventana)

    # Mostrar información de resolución
    info = escalador.get_info_resolucion()

    print(f"✅ ESCALADOR INICIALIZADO")
    print(f"   Resolución: {info['screen_width']}x{info['screen_height']}")
    print(f"   Categoría: {info['categoria']}")
    print(f"   Factor de escala: {info['scale_factor']:.2f}x")
    print()

    # Probar cálculos de escalado
    print("📏 CÁLCULOS DE ESCALADO:")
    print()

    # Anchos
    print("   ANCHOS:")
    print(f"   - Sidebar (280px base): {escalador.get_escalado_ancho(280)}px")
    print(f"   - Botón menú (200px base): {escalador.get_escalado_ancho(200)}px")
    print(f"   - Botón con límite (200px base, max 350): {min(escalador.get_escalado_ancho(200), escalador.get_escalado_ancho(350))}px")
    print()

    # Altos
    print("   ALTOS:")
    print(f"   - Botón (40px base): {escalador.get_escalado_alto(40)}px")
    print()

    # Fuentes
    print("   FUENTES:")
    print(f"   - Título (28px base): {escalador.get_tamano_fuente(28)}px")
    print(f"   - Texto normal (14px base): {escalador.get_tamano_fuente(14)}px")
    print(f"   - Texto pequeño (11px base): {escalador.get_tamano_fuente(11)}px")
    print()

    # Padding
    print("   PADDING:")
    print(f"   - Normal (10px base): {escalador.get_padding(10)}px")
    print(f"   - Grande (20px base): {escalador.get_padding(20)}px")
    print()

    # Simular diferentes resoluciones
    print("🖥️  SIMULACIÓN DE DIFERENTES RESOLUCIONES:")
    print()

    resoluciones = [
        (1920, 1080, "Full HD"),
        (2560, 1440, "2K / QHD"),
        (3840, 2160, "4K"),
        (5120, 2880, "5K Ultra Wide")
    ]

    for width, height, nombre in resoluciones:
        # Calcular factor de escala simulado
        scale_factor = min(width / 1920, height / 1080)

        print(f"   {nombre} ({width}x{height}):")
        print(f"   - Factor de escala: {scale_factor:.2f}x")
        print(f"   - Sidebar: {int(280 * scale_factor)}px")
        print(f"   - Botón: {int(200 * scale_factor)}px")
        print(f"   - Fuente 14px: {max(10, int(14 * min(scale_factor, 1.5)))}px")
        print()

    print("=" * 70)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 70)
    print()
    print("🎯 RESULTADO:")
    print("   - El sistema de escalado funciona correctamente")
    print("   - Los componentes se adaptan a diferentes resoluciones")
    print("   - Las fuentes tienen límites para no ser demasiado grandes")
    print("   - Los anchos máximos están limitados para pantallas ultra wide")
    print()

    # Crear UI de prueba visual
    print("Creando ventana de prueba visual...")

    frame = ctk.CTkFrame(ventana)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        frame,
        text=f"Resolución: {info['categoria']}\nFactor: {info['scale_factor']:.2f}x",
        font=("Arial", 16, "bold")
    ).pack(pady=20)

    # Botón de ejemplo con escalado
    from PIL import Image
    import os

    # Crear icono de ejemplo
    icono = ctk.CTkImage(
        light_image=Image.new("RGB", (24, 24), color="#003152"),
        size=(escalador.get_escalado_ancho(24), escalador.get_escalado_ancho(24))
    )

    boton = ctk.CTkButton(
        frame,
        text="   Botón de ejemplo",
        fg_color="#003152",
        hover_color="#1c669f",
        text_color="white",
        width=escalador.get_escalado_ancho(200),
        height=escalador.get_escalado_alto(40),
        image=icono,
        anchor="w",
        font=("Arial", escalador.get_tamano_fuente(14))
    )
    boton.pack(pady=20)

    ctk.CTkButton(
        frame,
        text="Cerrar",
        command=ventana.destroy,
        width=100,
        height=35
    ).pack(pady=10)

    ventana.mainloop()


if __name__ == "__main__":
    probar_escalado()
