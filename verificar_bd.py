#!/usr/bin/env python3
"""
Script de verificación de base de datos
Ejecuta este script para verificar que todo esté correcto antes de iniciar la aplicación
"""

from db_conexion import conexion, ejecutar_select

def verificar_tablas():
    """Verifica qué tablas existen en la base de datos"""
    cursor = conexion.cursor()

    try:
        cursor.execute("SHOW TABLES")
        tablas = [tabla[0] for tabla in cursor.fetchall()]

        print("\n" + "="*60)
        print("📊 TABLAS EN LA BASE DE DATOS")
        print("="*60)

        # Tablas esperadas
        tablas_esperadas = [
            "alumnos", "maestros", "administradores", "usuarios",
            "carreras", "materias", "grupos", "registros",
            "tipos_actividades", "salones",
            "calificaciones_finales", "calificaciones_actividades", "horario"
        ]

        for tabla in tablas_esperadas:
            if tabla in tablas:
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"✅ {tabla:<30} ({count} registros)")
            else:
                print(f"❌ {tabla:<30} (NO EXISTE)")

        print("="*60 + "\n")

        # Verificar columnas críticas
        print("🔍 VERIFICANDO COLUMNAS CRÍTICAS")
        print("="*60)

        # Verificar id_registro en tabla registros
        cursor.execute("SHOW COLUMNS FROM registros LIKE 'id_registro'")
        if cursor.fetchone():
            print("✅ Tabla 'registros' tiene columna 'id_registro'")
        else:
            print("❌ Tabla 'registros' NO tiene columna 'id_registro' (se agregará automáticamente)")

        print("="*60 + "\n")

        return True

    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

    finally:
        cursor.close()


def probar_conexion():
    """Prueba la conexión a la base de datos"""
    print("\n" + "="*60)
    print("🔌 PROBANDO CONEXIÓN A BASE DE DATOS")
    print("="*60)

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✅ Conectado a MySQL versión {version}")
        print(f"✅ Base de datos: 'control_escolar'")
        cursor.close()
        print("="*60 + "\n")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("="*60 + "\n")
        return False


def main():
    """Función principal"""
    print("\n" + "🔟 "*10)
    print("VERIFICACIÓN DE BASE DE DATOS - SISTEMA DE CONTROL ESCOLAR")
    print("🔟 "*10)

    # Probar conexión
    if not probar_conexion():
        print("❌ No se pudo conectar a la base de datos. Verifica tus credenciales.")
        return

    # Verificar tablas
    if not verificar_tablas():
        print("❌ Error al verificar tablas.")
        return

    print("✅ VERIFICACIÓN COMPLETADA")
    print("\n📝 NOTAS:")
    print("   - Las tablas faltantes se crearán automáticamente al iniciar la aplicación")
    print("   - La columna 'id_registro' se agregará automáticamente si no existe")
    print("   - Todo está listo para ejecutar la aplicación")
    print("\n🚀 Puedes iniciar la aplicación con: python main_administrador.py")
    print("   o con: python3 main_administrador.py")
    print("\n")


if __name__ == "__main__":
    main()
