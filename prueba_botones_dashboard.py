# -*- coding: utf-8 -*-
"""
Prueba rápida de las tarjetas de catálogos con texto largo
"""
import sys
import customtkinter as ctk
from PIL import Image

# Configurar codificación para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def crear_icono_prueba(color_hex, size=(64, 64)):
    """Crea un icono de prueba con color sólido"""
    from PIL import Image
    img = Image.new("RGBA", size, color_hex)
    return ctk.CTkImage(light_image=img, size=size)

def probar_tarjetas_catologos():
    """Prueba las tarjetas de catálogos con diferentes anchos"""

    print("=" * 70)
    print("PRUEBA DE TARJETAS DE CATÁLOGOS")
    print("=" * 70)
    print()

    # Crear ventana de prueba
    ventana = ctk.CTk()
    ventana.title("Prueba de Tarjetas de Catálogos")
    ventana.geometry("1400x800")

    # Frame principal
    main_frame = ctk.CTkFrame(ventana, fg_color="#f0f0f0")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Título
    ctk.CTkLabel(
        main_frame,
        text="Prueba de Tarjetas de Catálogos - Texto Largo",
        font=("Arial", 20, "bold"),
        text_color="#000000"
    ).pack(pady=(0, 20))

    # Grid frame para tarjetas
    grid_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    grid_frame.pack(fill="both", expand=True)

    # Configurar grid
    for col in range(3):
        grid_frame.grid_columnconfigure(col, weight=1, minsize=380)

    # Datos de catálogos con texto largo
    catalogos = [
        ("Alumnos", "Gestión de estudiantes", "#510054"),
        ("Maestros", "Gestión de docentes", "#004235"),
        ("Administradores", "Gestión de administradores", "#1A3A8F"),
        ("Materias", "Catálogo de materias", "#2D3250"),
        ("Grupos", "Gestión de grupos", "#2D3250"),
        ("Carreras", "Catálogo de carreras", "#2D3250"),
        ("Actividades", "Gestión de actividades", "#2D3250"),
        ("Inscripciones", "Registro de inscripciones", "#2D3250"),
        ("Reportes", "Generación de reportes", "#2D3250"),
        ("Calificaciones", "Gestión de calificaciones", "#2D3250"),
        ("Usuarios", "Gestión de las cuentas de usuarios", "#2D3250"),
    ]

    # Pruebas con diferentes anchos
    anchos_prueba = [300, 350, 380, 400]

    print("📏 PRUEBAS CON DIFERENTES ANCHOS DE TARJETA:")
    print()

    for ancho_tarjeta in anchos_prueba:
        print(f"   Ancho tarjeta: {ancho_tarjeta}px")
        print(f"   - Wraplength subtítulo: {ancho_tarjeta - 40}px")

        # Verificar si el texto más largo cabe
        texto_largo = "Gestión de las cuentas de usuarios"
        caracteres_estimados = (ancho_tarjeta - 40) // 7  # ~7px por caracter
        print(f"   - Caracteres por línea estimados: ~{caracteres_estimados}")

        if len(texto_largo) > caracteres_estimados:
            lineas_necesarias = (len(texto_largo) // caracteres_estimados) + 1
            print(f"   - ⚠️  Texto '{texto_largo}' necesita ~{lineas_necesarias} líneas")
        else:
            print(f"   - ✅ Texto '{texto_largo}' cabe en 1 línea")
        print()

    # Crear tarjetas visuales con ancho de 380px (el recomendado)
    ancho_recomendado = 380
    wraplength_recomendado = ancho_recomendado - 40

    print("=" * 70)
    print(f"CREANDO TARJETAS VISUALES (ANCHO: {ancho_recomendado}px)")
    print("=" * 70)
    print()

    for idx, (titulo, subtitulo, color) in enumerate(catalogos):
        r = idx // 3
        c = idx % 3
        grid_frame.grid_rowconfigure(r, weight=1)

        # Crear tarjeta
        card = ctk.CTkFrame(
            grid_frame,
            fg_color=color,
            corner_radius=12,
            cursor="hand2",
            width=ancho_recomendado
        )
        card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
        card.grid_propagate(False)

        # Icono de prueba
        icono = crear_icono_prueba(color)
        ctk.CTkLabel(card, text="", image=icono).pack(pady=(16, 4))

        # Título
        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 15, "bold"),
            text_color="white",
            anchor="center"
        ).pack(pady=(0, 2))

        # Subtítulo con wraplength
        lbl_sub = ctk.CTkLabel(
            card,
            text=subtitulo,
            font=("Arial", 11),
            text_color="#cccccc",
            anchor="center",
            justify="center",
            wraplength=wraplength_recomendado
        )
        lbl_sub.pack(pady=(0, 16))

        print(f"✅ Tarjeta '{titulo}':")
        print(f"   - Subtítulo: '{subtitulo}'")
        print(f"   - Longitud: {len(subtitulo)} caracteres")

        # Calcular líneas necesarias
        chars_per_line = wraplength_recomendado // 7
        if len(subtitulo) > chars_per_line:
            lines = (len(subtitulo) // chars_per_line) + 1
            print(f"   - Líneas estimadas: ~{lines}")
        else:
            print(f"   - Líneas estimadas: 1")
        print()

    print("=" * 70)
    print("✅ VENTANA CREADA - REVISAR VISUALMENTE")
    print("=" * 70)
    print()
    print("🎯 RESULTADO:")
    print(f"   - Ancho de tarjeta: {ancho_recomendado}px")
    print(f"   - Wraplength subtítulo: {wraplength_recomendado}px")
    print(f"   - Minsize columnas grid: {ancho_recomendado}px")
    print()
    print("✅ Verificar que TODO el texto sea visible sin cortes")
    print()

    ventana.mainloop()


if __name__ == "__main__":
    probar_tarjetas_catologos()
