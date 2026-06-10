# Proyecto Sistema de Registro de Calificaciones

#### Este proyecto implementa un sistema académico para la gestión de alumnos, maestros y calificaciones, utilizando una base de datos relacional.  
Desarrollado como parte de la materia **Sistemas de Bases de Datos** en el Instituto Tecnológico de Veracruz.
---
## Instalación rápida
### 1. Clonar el repositorio
```bash
git clone https://github.com/Jessica-Reyes06/proyecto_sistema_bd.git
cd proyecto_sistema_bd 
```
---
### 2. Configurar variables de entorno

El proyecto incluye un archivo `.env` con la configuración necesaria para conectarse a la base de datos PostgreSQL utilizada durante el desarrollo.
Verifique que dicho archivo se encuentre en la raíz del proyecto antes de ejecutar la aplicación.

---
### 3. Crear entorno virtual (opcional pero recomendado)
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```
---
### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```
---
### 5. Ejecutar el proyecto 
Ejecute el archivo principal del sistema:
```bash
python main.py
```
Al iniciar la aplicación se mostrará la ventana de inicio de sesión, donde deberá ingresar las credenciales correspondientes al rol de usuario que desee utilizar.

---
### 6. Credenciales y Roles de Usuario
El sistema cuenta con inicio de sesión para tres tipos de usuario:

* Administrador
*  Maestro
*  Alumno

## Credenciales de prueba

### Administrador
* Usuario: ADM001
* Contraseña: admin123

### Maestro
* Usuario: M001
* Contraseña: password123

### Alumno
* Usuario: A2600001
* Contraseña: alumno123
--- 
## Flujo de autenticación

Según el rol, se accede a la interfaz correspondiente:

Administrador → gestión completa del sistema

Maestro → gestión de calificaciones y alumnos

Alumno → consulta de calificaciones y datos personales

## Nota

Las funcionalidades de los roles Administrador y Maestro se encuentran completamente implementadas y operativas.

La interfaz del rol Alumno no fue finalizada durante el desarrollo del proyecto, por lo que las pruebas y demostraciones del sistema deben realizarse utilizando las cuentas de Administrador o Maestro.
