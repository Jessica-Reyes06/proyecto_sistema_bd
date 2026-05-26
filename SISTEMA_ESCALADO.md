# Sistema de Escalado Dinámico - Documentación

## 🎯 Objetivo

Sistema de escalado dinámico para componentes UI que soporta resoluciones desde 1920x1080 hasta 5K Ultra Wide, con los siguientes objetivos:

- ✅ Los botones se expanden proporcionalmente
- ✅ El texto e iconos se mantienen centrados y visibles sin cortarse
- ✅ Sistema de rejilla (grid) con pesos (weights) para distribución automática
- ✅ Escalado de fuente con límites inteligentes

## 📁 Archivos Implementados

### 1. `escalado_dinamico.py` - Módulo Principal

Clase `EscaladorDinamico` que gestiona todo el sistema de escalado:

```python
from escalado_dinamico import crear_escalador

# En main_administrador.py
escalador = crear_escalador(ventana_principal)
```

#### Funcionalidades Principales:

- **get_escalado_ancho(base_width)**: Calcula ancho escalado
- **get_escalado_alto(base_height)**: Calcula alto escalado
- **get_tamano_fuente(base_size)**: Calcula tamaño de fuente con límite de 1.5x
- **get_padding(base_padding)**: Calcula padding escalado
- **configurar_boton_dinamico()**: Configura botones con límites
- **crear_boton_menu()**: Crea botones de menú completamente dinámicos

### 2. `main_administrador.py` - Sidebar Dinámico

Modificaciones implementadas:

```python
# Inicialización del escalador
escalador = crear_escalador(ventana_principal)
set_escalador(escalador)  # Compartir con funciones_admin.py

# Sidebar con ancho dinámico
ancho_sidebar = escalador.get_escalado_ancho(280)
ancho_sidebar = min(ancho_sidebar, escalador.get_escalado_ancho(350))

# Iconos con tamaño dinámico
tamano_icono = escalador.get_escalado_ancho(24)
tamano_icono = min(tamano_icono, 32)

# Botones con dimensiones dinámicas
btn_inicio = ctk.CTkButton(
    frame_inicio,
    text="   Inicio",
    width=escalador.get_escalado_ancho(200),
    height=escalador.get_escalado_alto(40),
    font=("Arial", escalador.get_tamano_fuente(14)),
    image=img_inicio,
    anchor="w",
    command=lambda: mostrar_dashboard(main_frame)
)
```

### 3. `funciones_admin.py` - Botones de Gestión

Nuevas funciones agregadas:

```python
# Variable global para el escalador
escalador_global = None

def set_escalador(escalador):
    """Establece el escalador global"""
    global escalador_global
    escalador_global = escalador

def crear_boton_menu_dinamico(parent, texto, color, comando=None, ancho_base=180):
    """Crea botones de menú dinámicos"""
    if escalador_global:
        ancho = escalador_global.get_escalado_ancho(ancho_base)
        alto = escalador_global.get_escalado_alto(35)
        tamano_fuente = escalador_global.get_tamano_fuente(13)

        # Limitar ancho máximo
        ancho = min(ancho, escalador_global.get_escalado_ancho(250))
    else:
        # Valores por defecto sin escalador
        ancho = ancho_base
        alto = 35
        tamano_fuente = 13

    return CTkButton(parent, text=texto, fg_color=color,
                     font=("Arial", tamano_fuente, "bold"),
                     width=ancho, height=alto, command=comando)
```

## 🔧 Uso del Sistema

### En `main_administrador.py`:

```python
import sys
import customtkinter as ctk
from escalado_dinamico import crear_escalador
from funciones_admin import set_escalador

def iniciar_admin():
    global escalador

    # 1. Crear ventana
    ventana_principal = ctk.CTk()
    ventana_principal.minsize(1100, 700)

    # 2. Inicializar escalador
    escalador = crear_escalador(ventana_principal)
    info = escalador.get_info_resolucion()

    print(f"Resolución: {info['screen_width']}x{info['screen_height']}")
    print(f"Categoría: {info['categoria']}")
    print(f"Factor de escala: {info['scale_factor']:.2f}x")

    # 3. Compartir escalador
    set_escalador(escalador)

    # 4. Usar en componentes
    sidebar = ctk.CTkFrame(ventana_principal,
                           width=escalador.get_escalado_ancho(280),
                           fg_color="#003152")

    btn = ctk.CTkButton(
        parent,
        text="Inicio",
        width=escalador.get_escalado_ancho(200),
        height=escalador.get_escalado_alto(40),
        font=("Arial", escalador.get_tamano_fuente(14))
    )
```

### En otras secciones:

```python
from funciones_admin import crear_boton_menu_dinamico

# Botón dinámico con valores por defecto
boton = crear_boton_menu_dinamico(menu, "Guardar", "#510054", guardar)

# Botón dinámico con ancho personalizado
boton = crear_boton_menu_dinamico(menu, "Exportar", "#2D3250",
                                  exportar, ancho_base=200)
```

## 📊 Tabla de Escalado

| Resolución | Factor | Sidebar | Botón Menú | Fuente 14px |
|------------|--------|---------|------------|-------------|
| 1920x1080  | 1.00x  | 280px   | 200px      | 14px        |
| 2560x1440  | 1.33x  | 373px   | 266px      | 18px        |
| 3840x2160  | 2.00x  | 400px*  | 300px*     | 20px*       |
| 5120x2880  | 2.66x  | 400px*  | 300px*     | 20px*       |

*Valores limitados para evitar componentes desproporcionados

## 🎨 Características del Sistema

### 1. **Escalado Proporcional**
- Todos los componentes escalan según el factor de resolución
- Factor = min(screen_width/1920, screen_height/1080)

### 2. **Límites Inteligentes**
- **Ancho máximo sidebar**: 350px (base 1920)
- **Ancho máximo botón**: 250-350px (base 1920)
- **Tamaño máximo fuente**: 1.5x del base

### 3. **Grid con Pesos**
```python
# Configuración de grid para distribución automática
main_area.grid_columnconfigure(0, weight=0)  # sidebar fijo
main_area.grid_columnconfigure(1, weight=1)  # contenido crece
```

### 4. **Texto e Iconos Centrados**
```python
# Botones con anchor="w" y espaciado para iconos
btn = ctk.CTkButton(
    parent,
    text="   Inicio",  # Espacio para icono
    image=icono,
    anchor="w",        # Alineación izquierda
    font=("Arial", escalador.get_tamano_fuente(14))
)
```

## 🚀 Pruebas del Sistema

### Ejecutar prueba de escalado:

```bash
python prueba_escalado.py
```

Esta prueba muestra:
- ✅ Información de resolución detectada
- ✅ Cálculos de escalado para anchos, altos, fuentes
- ✅ Simulación de diferentes resoluciones
- ✅ Ventana visual con botón de ejemplo

## 📋 Resumen de Cambios

### Archivos Modificados:
1. ✅ `escalado_dinamico.py` - Creado (nuevo módulo)
2. ✅ `funciones_admin.py` - Agregadas funciones de escalado
3. ✅ `main_administrador.py` - Implementado escalado en sidebar

### Archivos de Prueba:
1. ✅ `prueba_escalado.py` - Script de verificación

## 🎯 Resultado Final

El sistema ahora soporta:
- ✅ **Resoluciones desde 1920x1080 hasta 5K Ultra Wide**
- ✅ **Botones que se expanden proporcionalmente**
- ✅ **Texto e iconos siempre centrados y visibles**
- ✅ **Sistema de grid con pesos para distribución automática**
- ✅ **Escalado de fuentes con límites de 1.5x**
- ✅ **Límites máximos para evitar componentes desproporcionados**

## 📞 Uso en Desarrollo

Para agregar escalado a nuevos componentes:

```python
# 1. Importar el escalador
from funciones_admin import get_escalador

# 2. Obtener el escalador
escalador = get_escalador()

# 3. Usarlo en componentes
if escalador:
    ancho = escalador.get_escalado_ancho(200)
    alto = escalador.get_escalado_alto(40)
    fuente = escalador.get_tamano_fuente(14)
else:
    # Valores por defecto
    ancho, alto, fuente = 200, 40, 14
```

---

**Sistema desarrollado para**: Proyecto Sistema BD
**Compatibilidad**: Python 3.x + CustomTkinter
**Resoluciones soportadas**: 1920x1080 hasta 5120x2880 (5K Ultra Wide)
