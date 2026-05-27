#!/usr/bin/env python3
"""
Script para crear la tabla de auditoría en PostgreSQL
Ejecuta el archivo crear_auditoria.sql
"""

from db_conexion import conexion

def crear_tabla_auditoria():
    """Lee y ejecuta el script SQL para crear la tabla de auditoría"""
    try:
        with open('crear_auditoria.sql', 'r', encoding='utf-8') as f:
            script = f.read()
        
        cursor = conexion.cursor()
        cursor.execute(script)
        conexion.commit()
        cursor.close()
        
        print("✅ Tabla 'auditoria_cambios' creada exitosamente")
        return True
    
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'crear_auditoria.sql'")
        return False
    
    except Exception as e:
        print(f"❌ Error al crear la tabla: {e}")
        conexion.rollback()
        return False

if __name__ == "__main__":
    crear_tabla_auditoria()
