# 📖 Guía de Uso - Sistema de Control Escolar

## 🚀 Inicio Rápido

### **Requisitos Previos:**
1. Python 3.x instalado
2. Las librerías necesarias instaladas:
   ```bash
   pip install mysql-connector-python customtkinter Pillow tkcalendar
   ```
3. Acceso a base de datos MySQL (db_escolar)

---

## 📋 Paso 1: Iniciar el Sistema

### **Opción A: Desde Login (Recomendado)**
```bash
python interfaz_login.py
```

### **Opción B: Directamente al Dashboard**
```bash
python main_administrador.py
```

### **Verificar Estado de BD:**
```bash
python verificar_bd.py
```

---

## 🔑 Paso 2: Iniciar Sesión

1. **Ejecutar:** `python interfaz_login.py`
2. **Ingresar credenciales:**
   - Usuario: [tu usuario]
   - Contraseña: [tu contraseña]
3. **Click en "Iniciar Sesión"**
4. El sistema te llevará al Dashboard principal

---

## 🎯 Paso 3: Usar el Dashboard

### **Pantalla Principal:**
El dashboard muestra **13 módulos** disponibles:

1. 📚 **Alumnos** - Gestión de alumnos
2. 👨‍🏫 **Maestros** - Gestión de maestros
3. 👔 **Administradores** - Gestión de administradores
4. 👤 **Usuarios** - Gestión de usuarios del sistema
5. 📝 **Inscripciones** - Inscripción de alumnos a grupos
6. 🎓 **Carreras** - Catálogo de carreras
7. 📖 **Materias** - Catálogo de materias
8. 👥 **Grupos** - Gestión de grupos
9. 📊 **Calificaciones Finales** - Calificaciones por periodo
10. 📋 **Calif. Actividades** - Calificaciones parciales
11. 🏫 **Salones** - Gestión de aulas y laboratorios
12. 📅 **Tipos de Actividades** - Tipos de actividades académicas
13. ⏰ **Horarios** - Horarios de grupos

### **Navegación:**
- **Click en cualquier módulo** → Abre la vista de gestión
- **Click en "←"** → Regresa al dashboard

---

## 📝 Paso 4: Registrar Datos (CREATE)

### **Ejemplo: Registrar un Alumno**

1. **Click en "Alumnos"** en el dashboard
2. **Click en "Registrar alumno"** (botón azul)
3. **Llenar el formulario:**
   - Número de Control: [8 dígitos]
   - Nombre: [Nombre del alumno]
   - Apellido Paterno: [Apellido paterno]
   - Apellido Materno: [Apellido materno]
   - Correo: [correo electrónico]
   - Carrera: [Seleccionar del combo]
   - Semestre: [Número 1-10]
   - Estado: [Activo/Egresado/Baja]
4. **Click en "Guardar"**
5. **Ver mensaje de confirmación** ✅

### **Campos Obligatorios:**
Todos los campos son obligatorios. El sistema muestra error si faltan datos.

---

## 👀 Paso 5: Ver Datos (READ)

### **Ver Tabla de Datos:**
1. **Entrar a cualquier módulo** (ej: Alumnos)
2. **La tabla muestra automáticamente** todos los registros de la BD
3. **Columnas visibles:** Dependen del módulo (ej: Alumnos muestra número de control, nombre, apellidos, etc.)

### **Si la tabla está vacía:**
- Muestra mensaje "No hay registros"
- Debes registrar datos primero (CREATE)

---

## ✏️ Paso 6: Editar Datos (UPDATE)

### **Ejemplo: Editar un Alumno**

1. **Entrar al módulo "Alumnos"**
2. **Pasar el mouse sobre una fila** → Aparece botón "Editar" (morado)
3. **Click en "Editar"**
4. **Se abre formulario inline** con los datos actuales
5. **Modificar los campos necesarios**
6. **Click en "Guardar"**
7. **Ver mensaje de confirmación** ✅
8. **La tabla se actualiza automáticamente** 🔄

### **Validaciones:**
- Calificaciones: Deben estar entre 0 y 100
- Campos numéricos: Solo aceptan números
- Fechas: Formato YYYY-MM-DD

---

## 🗑️ Paso 7: Eliminar Datos (DELETE)

### **Ejemplo: Eliminar un Alumno**

1. **Entrar al módulo "Alumnos"**
2. **Pasar el mouse sobre una fila** → Aparece botón "Eliminar" (rojo)
3. **Click en "Eliminar"**

### **Casos Posibles:**

#### **Caso 1: Sin Dependencias**
- **Mensaje:** "¿Está seguro de eliminar el registro?"
- **Opciones:**
  - **Sí** → Elimina el registro
  - **No** → Cancela eliminación

#### **Caso 2: Con Dependencias**
Si el alumno tiene inscripciones o calificaciones:

- **Mensaje:** "El registro tiene X dependencias:
  • Y inscripciones
  • Z calificaciones finales

  ¿Qué desea hacer?"

- **Opciones:**
  - **Sí** → Elimina el alumno Y todas sus dependencias
  - **No** → Cancela eliminación
  - **Cancelar** → Cierra el diálogo

⚠️ **ADVERTENCIA:** La eliminación en cascada es irreversible. Verifica antes de confirmar.

---

## 💾 Paso 8: Crear Respaldo

### **Crear Respaldo Completo:**

1. **En el dashboard, buscar sección "Respaldo y Restauración"**
2. **Click en "Crear Respaldo Completo"**
3. **Seleccionar ubicación** donde guardar la carpeta
4. **El sistema crea carpeta** con formato: `Respaldo_DB_YYYYMMDD_HHMMSS/`
5. **Dentro de la carpeta:** 13 archivos CSV (uno por tabla)

### **Características:**
- ✅ Timestamp automático (fecha/hora real de tu computadora)
- ✅ 13 archivos CSV en la carpeta
- ✅ Compatible con Excel
- ✅ Puede seleccionar ubicación personalizada

---

## 📂 Paso 9: Restaurar Respaldo

### **Restaurar desde Respaldo:**

1. **En el dashboard, buscar sección "Respaldo y Restauración"**
2. **Click en "Restaurar desde Respaldo"**
3. **Seleccionar la carpeta** del respaldo (debe comenzar con `Respaldo_DB_`)
4. **Ver confirmación** con lista de tablas a restaurar
5. **Click en "Sí"** para confirmar restauración
6. **Los datos se restauran** en la base de datos

⚠️ **ADVERTENCIA:** La restauración sobrescribe los datos actuales. Haz un respaldo antes de restaurar.

---

## 📤 Paso 10: Exportar Datos

### **Exportar una Tabla a CSV:**

1. **Entrar al módulo** deseado (ej: Alumnos)
2. **Click en "Exportar CSV"**
3. **Seleccionar ubicación** y nombre del archivo
4. **Click en "Guardar"**
5. **El archivo CSV se crea** con todos los datos de la tabla

### **Uso del archivo CSV:**
- Abrir con Excel
- Abrir con Google Sheets
- Importar en otro sistema
- Análisis de datos

---

## 📥 Paso 11: Importar Datos

### **Importar una Tabla desde CSV:**

1. **Entrar al módulo** deseado (ej: Alumnos)
2. **Click en "Importar CSV"**
3. **Seleccionar el archivo CSV** a importar
4. **El sistema valida** el archivo
5. **Los datos se importan** a la base de datos

### **Formato de CSV Requerido:**
- **Primera fila:** Nombres de columnas
- **Separador:** Comas (,)
- **Codificación:** UTF-8
- **Columnas:** Deben coincidir con las de la BD

### **Ejemplo de CSV (alumnos.csv):**
```csv
numero_control,nombre_alumno,apellido_paterno,apellido_materno,correo_alumno,carrera,semestre,estatus_alumno
20240001,Juan,Pérez,López,juan@email.com,Ingeniería en Sistemas,1,Activo
20240002,María,García,Rodríguez,maria@email.com,Ingeniería Industrial,2,Activo
```

---

## 🎯 Tips de Uso

### **Eficiencia:**
- ✅ Usa el mouse hover para ver botones de editar/eliminar
- ✅ Usa importación CSV para carga masiva de datos
- ✅ Crea respaldos regularmente (antes de cambios importantes)
- ✅ Usa exportación CSV para análisis en Excel

### **Seguridad:**
- ⚠️ Siempre verifica antes de eliminar con dependencias
- ⚠️ Haz respaldo antes de importar datos masivos
- ⚠️ No cierres la aplicación mientras guarda datos
- ⚠️ Mantén copias de respaldo en lugares seguros

### **Mantenimiento:**
- 📅 Crea respaldo semanal
- 📅 Verifica integridad de datos mensualmente
- 📅 Limpia datos obsoletos periódicamente
- 📅 Actualiza catálogos (carreras, materias) cada periodo

---

## 🐛 Solución de Problemas

### **Problema: No se conecta a la base de datos**
**Solución:**
1. Verifica que MySQL esté corriendo
2. Verifica credenciales en `db_conexion.py`
3. Ejecuta `verificar_bd.py` para diagnosticar

### **Problema: La tabla aparece vacía**
**Solución:**
1. Verifica que hay datos en la BD
2. Ejecuta `SELECT COUNT(*) FROM nombre_tabla` en MySQL
3. Si está vacía, registra datos primero

### **Problema: Error al eliminar**
**Solución:**
1. Verifica si hay dependencias
2. Confirma que quieres eliminar en cascada
3. Si el error persiste, verifica foreign keys

### **Problema: No se guarda el cambio al editar**
**Solución:**
1. Verifica que todos los campos tengan datos válidos
2. Revisa mensajes de error en consola
3. Verifica que la tabla tenga la columna correcta

### **Problema: Error al importar CSV**
**Solución:**
1. Verifica formato del CSV (comas como separador)
2. Verifica que las columnas coincidan con la BD
3. Verifica que no haya IDs duplicados
4. Revisa que los datos tengan el formato correcto

---

## 📞 Soporte

### **Archivos de Ayuda:**
- `docs/RESUMEN_CONVERSACION.md` - Resumen completo
- `docs/PROBLEMAS_SOLUCIONES.md` - Problemas comunes
- `docs/ESTADO_FINAL.md` - Estado del sistema
- `docs/INSTRUCCIONES_USO.md` - Esta guía

### **Verificación del Sistema:**
```bash
python verificar_bd.py
```

Muestra:
- Tablas existentes
- Cantidad de registros por tabla
- Estado de conexión

---

## 🎓 Glosario

- **BD (Base de Datos):** db_escolar en MySQL
- **CRUD:** Create, Read, Update, Delete (Crear, Leer, Actualizar, Eliminar)
- **CSV:** Comma-Separated Values (formato de archivo)
- **Dashboard:** Pantalla principal del sistema
- **Foreign Key:** Clave foránea (relación entre tablas)
- **Inline:** En la misma ventana/pantalla
- **Mouse hover:** Pasar el mouse sobre un elemento
- **Timestamp:** Marca de tiempo (fecha/hora)
- **Validación:** Verificación de datos antes de guardar

---

## ✅ Checklist de Operaciones

### **Operaciones CRUD:**
- [ ] Registrar alumno (CREATE)
- [ ] Ver tabla de alumnos (READ)
- [ ] Editar alumno (UPDATE)
- [ ] Eliminar alumno (DELETE)
- [ ] Exportar alumnos a CSV
- [ ] Importar alumnos desde CSV

### **Operaciones de Respaldo:**
- [ ] Crear respaldo completo
- [ ] Verificar que se crearon los 13 archivos
- [ ] Restaurar respaldo
- [ ] Verificar que se restauraron los datos

### **Operaciones de Otras Entidades:**
- [ ] Registrar maestro
- [ ] Registrar inscripción
- [ ] Registrar calificación final
- [ ] Registrar salón
- [ ] Verificar todas las tablas

---

## 🚀 Flujo Completo de Trabajo

### **Ejemplo: Inscribir Alumno en un Semestre**

1. **Entrar a "Alumnos"**
   - Registrar alumno nuevo (si no existe)
   - Verificar que aparezca en la tabla

2. **Entrar a "Carreras"**
   - Verificar que la carrera existe
   - Si no, registrarla

3. **Entrar a "Materias"**
   - Verificar que las materias existen
   - Si no, registrarlas

4. **Entrar a "Maestros"**
   - Verificar que el maestro existe
   - Si no, registrarlo

5. **Entrar a "Grupos"**
   - Crear grupo para la materia y maestro
   - Asignar cupo máximo

6. **Entrar a "Inscripciones"**
   - Inscribir alumno en el grupo
   - Verificar que aparezca en la tabla

7. **Entrar a "Salones"**
   - Asignar salón al horario del grupo

8. **(Opcional) Calificaciones Finales**
   - Registrar calificación final del alumno

9. **(Opcional) Calif. Actividades**
   - Registrar calificaciones parciales

10. **Crear Respaldo**
    - Hacer respaldo completo del sistema

---

**¡Listo! Ahora sabes cómo usar todas las funcionalidades del sistema.** 🎉

Para más información, consulta los otros archivos de documentación en la carpeta `docs/`.
