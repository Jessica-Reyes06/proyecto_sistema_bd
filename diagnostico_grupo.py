#!/usr/bin/env python3
"""
Script de diagnóstico para la tabla Grupo
"""

from db_conexion import ejecutar_select

print("="*70)
print("DIAGNÓSTICO DE LA TABLA GRUPO")
print("="*70)

# 1. Verificar si la tabla existe y qué registros tiene
print("\n1. Contando registros en tabla Grupo:")
try:
    resultado = ejecutar_select("SELECT COUNT(*) FROM grupo")
    print(f"   ✅ Tabla 'Grupo' existe con {resultado[0][0]} registros")
except Exception as e:
    print(f"   ❌ Error accediendo a 'Grupo': {e}")
    try:
        resultado = ejecutar_select("SELECT COUNT(*) FROM grupos")
        print(f"   ⚠️  Pero 'grupos' (minúscula) existe con {resultado[0][0]} registros")
    except:
        print(f"   ❌ Tampoco existe 'grupos' (minúscula)")

# 2. Ver la estructura de la tabla Grupo
print("\n2. Estructura de la tabla Grupo:")
try:
    # PostgreSQL usa information_schema en lugar de DESCRIBE
    resultado = ejecutar_select("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'grupo'
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    for col in resultado:
        print(f"   - {col[0]:<25} {col[1]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Probar la consulta de obtener_grupos_ordenadas()
print("\n3. Prueba de obtener_grupos_ordenadas():")
try:
    sql = """
    SELECT g.id_grupo, m.nombre_maestro, mat.nombre_materia, g.cupo_maximo, g.periodo, g.anio, g.inscritos, g.horario, g.estado
    FROM grupo g
    JOIN maestro m ON g.matricula_maestro = m.matricula_maestro
    JOIN materia mat ON g.id_materia = mat.id_materia
    ORDER BY g.id_grupo ASC
    """
    resultado = ejecutar_select(sql)
    print(f"   ✅ Consulta ejecutada: {len(resultado)} registros obtenidos")
    if resultado:
        print(f"   Primer registro: {resultado[0]}")
except Exception as e:
    print(f"   ❌ Error en consulta: {e}")

# 4. Probar consultas individuales
print("\n4. Verificando tablas relacionadas:")
try:
    m_count = ejecutar_select("SELECT COUNT(*) FROM maestro")
    print(f"   ✅ Tabla 'Maestro': {m_count[0][0]} registros")
except Exception as e:
    print(f"   ❌ Error con Maestro: {e}")

try:
    mat_count = ejecutar_select("SELECT COUNT(*) FROM materia")
    print(f"   ✅ Tabla 'Materia': {mat_count[0][0]} registros")
except Exception as e:
    print(f"   ❌ Error con Materia: {e}")

# 5. Ver un registro de ejemplo
print("\n5. Ejemplo de registro en Grupo (sin JOIN):")
try:
    resultado = ejecutar_select("SELECT * FROM grupo LIMIT 1")
    if resultado:
        print(f"   Registro: {resultado[0]}")
    else:
        print("   ⚠️  No hay registros en la tabla")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)
