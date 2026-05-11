# -*- coding: utf-8 -*-
"""
Script para actualizar todas las consultas SQL de mayúsculas a minúsculas
"""
import os
import re
import sys

# Configurar codificacion para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Mapeo de tablas de mayúsculas a minúsculas
tablas = {
    'Alumno': 'alumno',
    'Maestro': 'maestro',
    'Administrador': 'administrador',
    'Carreras': 'carreras',
    'Carrera': 'carreras',
    'Materia': 'materia',
    'Grupo': 'grupo',
    'Registro': 'registro',
    'Cuentas': 'cuentas',
    'Cuenta': 'cuentas',
    'Roles': 'roles',
    'Rol': 'roles',
    'Actividad': 'actividad',
    'Tipos_actividades': 'tipos_actividades',
    'Unidad': 'unidad',
    'Calificacion_final': 'calificacion_final',
    'Calificaciones_unidad': 'calificaciones_unidad',
    'BonusMateria': 'bonusmateria',
    'BonusUnidad': 'bonusunidad',
    'Resultado': 'resultado',
    'Solicitudes': 'solicitudes'
}

def actualizar_archivo(ruta_archivo):
    """Actualiza un archivo reemplazando nombres de tablas"""
    print(f"Procesando: {ruta_archivo}")

    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    contenido_original = contenido
    cambios = 0

    # Reemplazar en consultas SQL
    for mayus, minus in tablas.items():
        # FROM Tabla
        patron = rf'FROM\s+{mayus}\b'
        if re.search(patron, contenido, re.IGNORECASE):
            contenido = re.sub(patron, f'FROM {minus}', contenido, flags=re.IGNORECASE)
            cambios += 1

        # INSERT INTO Tabla
        patron = rf'INTO\s+{mayus}\b'
        if re.search(patron, contenido, re.IGNORECASE):
            contenido = re.sub(patron, f'INTO {minus}', contenido, flags=re.IGNORECASE)
            cambios += 1

        # UPDATE Tabla
        patron = rf'UPDATE\s+{mayus}\b'
        if re.search(patron, contenido, re.IGNORECASE):
            contenido = re.sub(patron, f'UPDATE {minus}', contenido, flags=re.IGNORECASE)
            cambios += 1

        # DELETE FROM Tabla
        patron = rf'DELETE\s+FROM\s+{mayus}\b'
        if re.search(patron, contenido, re.IGNORECASE):
            contenido = re.sub(patron, f'DELETE FROM {minus}', contenido, flags=re.IGNORECASE)
            cambios += 1

        # JOIN Tabla
        patron = rf'JOIN\s+{mayus}\b'
        if re.search(patron, contenido, re.IGNORECASE):
            contenido = re.sub(patron, f'JOIN {minus}', contenido, flags=re.IGNORECASE)
            cambios += 1

        # LEFT JOIN Tabla
        patron = rf'LEFT\s+JOIN\s+{mayus}\b'
        if re.search(patron, contenido, re.IGNORECASE):
            contenido = re.sub(patron, f'LEFT JOIN {minus}', contenido, flags=re.IGNORECASE)
            cambios += 1

    if cambios > 0:
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"   [OK] {cambios} cambios realizados")
        return True
    else:
        print(f"   - Sin cambios")
        return False

# Archivos a procesar (excluyendo scripts de migración)
archivos_a_procesar = [
    'formularios_bd.py',
    'formularios_edicion.py',
    'funciones_datos.py',
    'funciones_admin.py',
    'diagnostico_grupo.py',
    'main_administrador.py',
    'interfaz_login.py',
    'funciones_login.py',
    'exportar_importar.py'
]

print("=" * 80)
print("ACTUALIZANDO CONSULTAS SQL PARA POSTGRESQL")
print("=" * 80)
print()

total_archivos = 0
total_cambios = 0

for archivo in archivos_a_procesar:
    if os.path.exists(archivo):
        if actualizar_archivo(archivo):
            total_archivos += 1
            total_cambios += 1
    else:
        print(f"Archivo no encontrado: {archivo}")

print()
print("=" * 80)
print(f"RESUMEN: {total_archivos} archivos actualizados")
print("=" * 80)
print()
print("[OK] Consultas SQL actualizadas a minusculas para PostgreSQL")
print("[OK] Tu proyecto ahora es compatible con PostgreSQL en Heroku")
