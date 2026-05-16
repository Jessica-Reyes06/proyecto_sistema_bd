# Instrucciones para conectar con PostgreSQL en Heroku

## 1. Instalar dependencias necesarias

Abre la terminal de PyCharm o PowerShell y ejecuta:

```powershell
pip install psycopg2-binary python-dotenv
```

O instala todas las dependencias del proyecto:

```powershell
pip install -r requirements.txt
```

## 2. Verificar la conexión

Ejecuta el script de verificación:

```powershell
python verificar_conexion_postgres.py
```

Si ves "✅ Conexión exitosa a PostgreSQL", todo está funcionando correctamente.

## 3. Cambios realizados

### Archivos modificados:

1. **`db_conexion.py`** - Migrado de MySQL a PostgreSQL
   - Usa `psycopg2` en lugar de `mysql.connector`
   - Carga credenciales desde variables de entorno
   - Usa `RealDictCursor` para resultados tipo diccionario

2. **`.env`** - Archivo nuevo con credenciales (NO compartir este archivo)
3. **`.gitignore`** - Actualizado para ignorar `.env` y archivos de base de datos
4. **`requirements.txt`** - Actualizado con dependencias de PostgreSQL

## 4. Seguridad

⚠️ **IMPORTANTE:**

- El archivo `.env` contiene tus credenciales y está en `.gitignore`
- **NUNCA** subas el archivo `.env` a GitHub o lo compartas públicamente
- Si cambias de equipo, copia el archivo `.env` manualmente

## 5. Diferencias entre MySQL y PostgreSQL

### Sintaxis de consultas:

- MySQL usa `?` o `%s` para parámetros
- PostgreSQL usa `%s` (ya está actualizado en el código)

### Funciones:

- MySQL: `mysql.connector`
- PostgreSQL: `psycopg2` con `RealDictCursor` para resultados diccionario

## 6. Solución de problemas

### Error: "Module 'psycopg2' not found"

```powershell
pip install psycopg2-binary
```

### Error: "Module 'dotenv' not found"

```powershell
pip install python-dotenv
```

### Error de conexión:

- Verifica que las credenciales en `.env` sean correctas
- Verifica que tu IP tenga acceso a la base de datos de Heroku
- Verifica que la base de datos esté online

## 7. Probado con

✅ Python 3.8+
✅ PostgreSQL 13+
✅ psycopg2-binary 2.9+
✅ Heroku Postgres

## 8. Nota de mantenimiento (2026-05-15)

- Se ha refactorizado `db_conexion.py` para evitar que la aplicación falle al importar el módulo cuando faltan dependencias o la base de datos está inaccesible. Ahora la conexión se crea bajo demanda mediante `get_conexion()` y se exporta un `conexion` proxy para compatibilidad.
- Si experimentas el error `ModuleNotFoundError: No module named 'psycopg2'` o `No module named 'dotenv'`, instala las dependencias con:

```powershell
python -m pip install -r requirements.txt
```

Esto instalará `psycopg2-binary` y `python-dotenv` entre otras dependencias del proyecto.
