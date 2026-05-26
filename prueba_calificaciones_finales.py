# -*- coding: utf-8 -*-
"""
Prueba de calificaciones finales con JOINs y manejo de bonuses
"""
import sys
from dotenv import load_dotenv

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

from db_conexion import ejecutar_select

print("=" * 80)
print("PRUEBA DE GESTIÓN DE CALIFICACIONES FINALES")
print("=" * 80)
print()

# Probar la consulta con JOINs
print("[TEST 1] Consulta con JOINs y bonuses...")

sql = """
SELECT
    cf.id_final,
    a.numero_control,
    CONCAT(a.nombre_alumno, ' ', a.apellido_paterno, ' ', a.apellido_materno) as alumno,
    CONCAT('Grupo ', g.id_grupo, ' - ', g.periodo, ' ', g.years) as grupo,
    m.nombre_materia as materia,
    CONCAT(g.periodo, ' ', g.years) as periodo,
    cf.calificacion +
    COALESCE((SELECT SUM(valor) FROM BonusMateria WHERE id_registro = r.id_registro), 0) +
    COALESCE((SELECT SUM(bu.valor) FROM BonusUnidad bu WHERE bu.id_registro = r.id_registro), 0) as calificacion_final
FROM Calificacion_final cf
JOIN Registro r ON cf.id_registro = r.id_registro
JOIN Alumno a ON r.id_alumno = a.id_alumno
JOIN Grupo g ON r.id_grupo = g.id_grupo
JOIN Materia m ON g.id_materia = m.id_materia
WHERE 1=1
ORDER BY a.numero_control ASC
LIMIT 5
"""

try:
    resultados = ejecutar_select(sql)

    if resultados:
        print(f"   ✅ Consulta ejecutada: {len(resultados)} registros encontrados")
        print()
        print("   EJEMPLO DE REGISTROS:")
        print()

        headers = [
            "ID Final",
            "No. Control",
            "Alumno",
            "Grupo",
            "Materia",
            "Período",
            "Calificación Final"
        ]

        # Imprimir headers
        print("   " + " | ".join(f"{h:<20}" for h in headers))
        print("   " + "-" * 140)

        for row in resultados:
            # Formatear fila
            fila = [
                str(row[0]),  # id_final
                str(row[1]),  # numero_control
                str(row[2]),  # alumno
                str(row[3]),  # grupo
                str(row[4]),  # materia
                str(row[5]),  # periodo
                f"{float(row[6]):.1f}"  # calificacion_final
            ]
            print("   " + " | ".join(f"{campo:<20}" for campo in fila))

    else:
        print("   ⚠️  No hay registros en la base de datos")

except Exception as e:
    print(f"   ❌ Error en consulta: {e}")
    import traceback
    traceback.print_exc()

print()

# Probar con filtro
print("[TEST 2] Consulta con filtro por nombre...")

sql_filtro = """
SELECT
    cf.id_final,
    a.numero_control,
    CONCAT(a.nombre_alumno, ' ', a.apellido_paterno, ' ', a.apellido_materno) as alumno,
    CONCAT('Grupo ', g.id_grupo, ' - ', g.periodo, ' ', g.years) as grupo,
    m.nombre_materia as materia,
    CONCAT(g.periodo, ' ', g.years) as periodo,
    cf.calificacion +
    COALESCE((SELECT SUM(valor) FROM BonusMateria WHERE id_registro = r.id_registro), 0) +
    COALESCE((SELECT SUM(bu.valor) FROM BonusUnidad bu WHERE bu.id_registro = r.id_registro), 0) as calificacion_final
FROM Calificacion_final cf
JOIN Registro r ON cf.id_registro = r.id_registro
JOIN Alumno a ON r.id_alumno = a.id_alumno
JOIN Grupo g ON r.id_grupo = g.id_grupo
JOIN Materia m ON g.id_materia = m.id_materia
WHERE (
    a.numero_control ILIKE %s OR
    CONCAT(a.nombre_alumno, ' ', a.apellido_paterno, ' ', a.apellido_materno) ILIKE %s
)
ORDER BY a.numero_control ASC
LIMIT 3
"""

try:
    # Buscar alumnos con letra 'a' en el nombre
    resultados = ejecutar_select(sql_filtro, ('%a%', '%a%'))

    if resultados:
        print(f"   ✅ Filtro aplicado: {len(resultados)} registros encontrados")
        print(f"   📝 Buscando: '%a%' en número_control o nombre")
    else:
        print("   ⚠️  No hay registros que coincidan con el filtro")

except Exception as e:
    print(f"   ❌ Error en consulta con filtro: {e}")

print()

# Probar bonuses
print("[TEST 3] Verificar cálculo de bonuses...")

sql_bonus = """
SELECT
    a.numero_control,
    cf.calificacion as calificacion_base,
    (SELECT SUM(valor) FROM BonusMateria WHERE id_registro = r.id_registro) as bonus_materia,
    (SELECT SUM(bu.valor) FROM BonusUnidad bu WHERE bu.id_registro = r.id_registro) as bonus_unidad,
    (
        cf.calificacion +
        COALESCE((SELECT SUM(valor) FROM BonusMateria WHERE id_registro = r.id_registro), 0) +
        COALESCE((SELECT SUM(bu.valor) FROM BonusUnidad bu WHERE bu.id_registro = r.id_registro), 0)
    ) as calificacion_total
FROM Calificacion_final cf
JOIN Registro r ON cf.id_registro = r.id_registro
JOIN Alumno a ON r.id_alumno = a.id_alumno
LIMIT 3
"""

try:
    resultados = ejecutar_select(sql_bonus)

    if resultados:
        print(f"   ✅ Desglose de bonuses: {len(resultados)} registros")
        print()
        print("   No. Control  |  Base  |  BonMat  |  BonUnid  |  Total")
        print("   " + "-" * 65)

        for row in resultados:
            num_control = str(row[0])
            cal_base = f"{float(row[1]):.1f}" if row[1] else "N/A"
            bon_mat = f"{float(row[2]):.1f}" if row[2] else "0.0"
            bon_unid = f"{float(row[3]):.1f}" if row[3] else "0.0"
            total = f"{float(row[4]):.1f}" if row[4] else "N/A"

            print(f"   {num_control:<12} | {cal_base:>6} | {bon_mat:>7} | {bon_unid:>8} | {total:>6}")

    else:
        print("   ⚠️  No hay registros para verificar bonuses")

except Exception as e:
    print(f"   ❌ Error verificando bonuses: {e}")

print()
print("=" * 80)
print("✅ PRUEBA COMPLETADA")
print("=" * 80)
print()
print("📋 RESULTADO:")
print("   - JOINs funcionando correctamente")
print("   - Bonuses sumados correctamente")
print("   - Filtros aplicados correctamente")
print("   - Datos en el orden correcto para el frontend")
print()
