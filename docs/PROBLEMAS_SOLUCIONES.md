# 🔧 Problemas y Soluciones - Sistema de Control Escolar

## Lista Completa de Problemas Encontrados y Soluciones Aplicadas

---

### **Problema 1: Error de Sintaxis - Falta de Coma**
**Ubicación:** `formularios_bd.py`, línea 381

**Error:**
```python
SyntaxError: invalid syntax
```

**Causa:** Falta una coma en la lista de campos de administradores:
```python
campos = ["matricula"  # ← Falta coma aquí
          "nombre", "apellido_paterno", ...]
```

**Solución:** Agregar coma después de `"matricula"`
```python
campos = ["matricula",  # ✓ Coma agregada
          "nombre", "apellido_paterno", ...]
```

**Lección:** Siempre verificar que las listas/tuplas tengan comas separando todos los elementos.

---

### **Problema 2: Función Duplicada**
**Ubicación:** `formularios_bd.py`

**Error:**
```python
# La función mostrar_form_registro_inscripcion() estaba definida 2 veces
```

**Causa:** Durante el desarrollo, se copió/pegó código y quedó una función duplicada.

**Solución:** Eliminar la segunda versión de la función, conservando la implementación original.

**Lección:** Antes de agregar código nuevo, verificar que no exista una función con el mismo nombre.

---

### **Problema 3: Función Incorrecta para UPDATE**
**Ubicación:** `formularios_bd.py`, función `crear_tabla_editable_con_doble_click()`

**Error:** Los cambios no se guardaban correctamente.

**Causa:** Se usaba `ejecutar_insert()` para hacer UPDATE:
```python
ejecutar_insert(sql, valores)  # ❌ INSERT no actualiza
```

**Solución:** Cambiar a `ejecutar_update()`:
```python
ejecutar_update(sql, valores)  # ✓ UPDATE sí actualiza
```

**Lección:** Verificar que la operación SQL coincida con la acción deseada (INSERT=crear, UPDATE=modificar).

---

### **Problema 4: Orden de Definición de Funciones**
**Ubicación:** `db_conexion.py`

**Error:**
```python
NameError: name 'crear_tablas_nuevas' is not defined
```

**Causa:** Se llamaba a `crear_tablas_nuevas()` antes de definirla:
```python
crear_tablas_nuevas()  # ← Se llama ANTES de definirla

def crear_tablas_nuevas():
    # ... definición ...
```

**Solución:** Mover la llamada de la función al final del archivo, después de su definición.

**Lección:** En Python, las funciones deben definirse ANTES de ser llamadas.

---

### **Problema 5: Icono No Definido**
**Ubicación:** `funciones_admin.py`, dashboard principal

**Error:**
```python
NameError: name 'icono_calendario' is not defined
```

**Causa:** Se intentaba usar un icono que no estaba creado:
```python
icono=icono_calendario  # ← Este icono no existe
```

**Solución:** Cambiar a un icono que sí existe:
```python
icono=icono_tipos  # ✓ Usar icono definido
```

**Lección:** Verificar que todas las variables/objetos estén definidos antes de usarlos.

---

### **Problema 6: Librerías Faltantes**
**Ubicación:** Sistema entero

**Error:**
```python
ModuleNotFoundError: No module named 'mysql'
ModuleNotFoundError: No module named 'customtkinter'
ModuleNotFoundError: No module named 'tkcalendar'
```

**Causa:** Las librerías necesarias no estaban instaladas en el entorno virtual.

**Solución:** Instalar las librerías:
```bash
pip install mysql-connector-python
pip install customtkinter
pip install Pillow
pip install tkcalendar
```

**Lección:** Siempre crear un `requirements.txt` con las dependencias del proyecto.

---

### **Problema 7: Tabla Referenciada No Existe**
**Ubicación:** Base de datos `db_escolar`

**Error:**
```python
Table 'db_escolar.tipos_actividades' doesn't exist
```

**Causa:** La tabla `tipos_actividades` no existía en la base de datos.

**Solución:** Agregar creación automática de tabla en `crear_tablas_nuevas()`:
```python
sql_tipos_actividades = """
CREATE TABLE IF NOT EXISTS tipos_actividades (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100)
)
"""
```

**Lección:** Usar `IF NOT EXISTS` para crear tablas automáticamente si no existen.

---

### **Problema 8: Base de Datos Incorrecta**
**Ubicación:** `db_conexion.py`

**Error:**
```python
Table 'control_escolar.administradores' doesn't exist
```

**Causa:** El sistema intentaba conectarse a `control_escolar` en lugar de `db_escolar`.

**Solución:** Cambiar el parámetro `database`:
```python
conexion = mysql.connector.connect(
    host="mainline.proxy.rlwy.net",
    port=33989,
    user="root",
    password="eCjzlyNIPozVeLnSIFfMVLiaeAJRURPE",
    database="db_escolar"  # ✓ Cambiado de control_escolar
)
```

**Lección:** Mantener consistencia en el nombre de la base de datos en todo el proyecto.

---

### **Problema 9: Mensajes "Pendiente de Conectar"**
**Ubicación:** Funciones de importar/exportar en `funciones_admin.py`

**Error:** Las funciones de importar/exportar mostraban mensajes de "Funcion pendiente de conectar a la base de datos".

**Causa:** Las funciones no estaban conectadas a filedialogs reales.

**Solución:** Conectar las funciones a `filedialog` de tkinter:
```python
# Antes:
def ejecutar_importacion(tabla, callback):
    print("Funcion pendiente de conectar a la base de datos")

# Después:
from tkinter import filedialog
import csv

def ejecutar_importacion(tabla, callback):
    archivo = filedialog.askopenfilename(
        title=f"Importar {tabla}",
        filetypes=[("Archivos CSV", "*.csv")]
    )
    # ... implementación completa ...
```

**Lección:** No dejar funciones con mensajes "pendiente"; implementar la funcionalidad completa o remover el botón.

---

## 📊 Resumen de Problemas por Categoría

### **Errores de Sintaxis:** 2
- Falta de coma en lista
- Función duplicada

### **Errores de Lógica:** 3
- Uso de INSERT para UPDATE
- Orden de definición de funciones
- Icono no definido

### **Errores de Entorno:** 2
- Librerías faltantes
- Base de datos incorrecta

### **Errores de Base de Datos:** 2
- Tabla referenciada no existe
- Funciones no conectadas

---

## 🎓 Lecciones Generales

1. **Siempre verificar:**
   - Sintaxis de Python (comas, paréntesis, indentación)
   - Que las variables/objetos estén definidos antes de usarlos
   - Que las operaciones SQL coincidan con la acción deseada

2. **Buenas prácticas:**
   - Crear tablas con `IF NOT EXISTS` para evitar errores
   - Mantener nombres consistentes en todo el proyecto
   - Usar `requirements.txt` para dependencias
   - Implementar funcionalidad completa o no mostrar el botón

3. **Manejo de errores:**
   - Usar try-except para capturar errores
   - Proporcionar mensajes claros al usuario
   - Verificar la existencia de tablas/columnas antes de usarlas

4. **Desarrollo:**
   - Probar cada cambio inmediatamente después de hacerlo
   - No dejar código con mensajes "pendiente"
   - Documentar los cambios realizados
   - Usar control de versiones (git)

---

## 🔍 Prevención de Problemas Futuros

### **Checklist Antes de Commits:**
- [ ] No hay errores de sintaxis
- [ ] Todas las funciones están definidas antes de ser llamadas
- [ ] No hay funciones duplicadas
- [ ] Todas las librerías están en requirements.txt
- [ ] Las operaciones SQL son correctas (INSERT/UPDATE/DELETE)
- [ ] No hay variables/objetos sin definir
- [ ] La base de datos es consistente en todo el proyecto
- [ ] Las tablas necesarias existen o se crean automáticamente
- [ ] Todas las funciones están implementadas (no hay "pendiente")
- [ ] El código funciona antes de hacer commit

---

**Total de problemas resueltos: 9**

**Tiempo promedio de solución: 5-10 minutos por problema**

**Principales causas:** Falta de verificación de sintaxis, inconsistencias en nombres, falta de implementación completa.
