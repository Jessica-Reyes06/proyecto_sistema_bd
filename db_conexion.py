import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Intentar importar psycopg2 pero no fallar en el import: fallaremos sólo al pedir conexión
try:
    import psycopg2
    from psycopg2 import OperationalError
except Exception:
    psycopg2 = None
    OperationalError = Exception

_conexion = None


def get_conexion():
    """Devuelve una conexión a PostgreSQL (creada la primera vez que se solicita).

    Si `psycopg2` no está instalado, levanta `ImportError` con instrucciones.
    Si falla la conexión, propaga la excepción original para que el llamador la maneje.
    """
    global _conexion
    if psycopg2 is None:
        raise ImportError(
            "La librería 'psycopg2' no está instalada. Instálala con: python -m pip install psycopg2-binary")

    if _conexion is None:
        try:
            _conexion = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            print(
                f"Conectado a PostgreSQL - Base de datos: {os.getenv('DB_NAME')}")
        except OperationalError:
            # Propagar para que el llamador pueda manejar (y evitar crash al importar)
            raise
    return _conexion


class _ProxyConexion:
    """Proxy ligero que obtiene la conexión real al primer uso.

    Permite mantener compatibilidad con módulos que hacen
    `from db_conexion import conexion` y usan `.cursor()` directamente.
    """

    def __getattr__(self, name):
        real = get_conexion()
        return getattr(real, name)

    def cursor(self, *args, **kwargs):
        return get_conexion().cursor(*args, **kwargs)

    def close(self):
        if _conexion is not None:
            try:
                _conexion.close()
            finally:
                pass


# Instancia proxy exportada para compatibilidad con código existente
conexion = _ProxyConexion()


def ejecutar_insert(sql, datos):
    """Ejecuta una consulta INSERT con parámetros"""
    conn = get_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def ejecutar_select(sql, params=None):
    """Ejecuta una consulta SELECT con parámetros"""
    conn = get_conexion()
    cursor = conn.cursor()
    try:
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        return cursor.fetchall()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def ejecutar_update(sql, valores):
    """Ejecuta una consulta UPDATE con parámetros"""
    conn = get_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, valores)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def ejecutar_delete(sql, valores):
    """Ejecuta una consulta DELETE con parámetros"""
    conn = get_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, valores)
        conn.commit()
        filas_afectadas = cursor.rowcount
        return filas_afectadas > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def ejecutar_select_todo(tabla):
    """Obtiene todos los registros de una tabla"""
    return ejecutar_select(f"SELECT * FROM {tabla}")


def obtener_registro_por_id(tabla, campo_id, valor_id):
    """Obtiene un registro específico por su ID"""
    return ejecutar_select(f"SELECT * FROM {tabla} WHERE {campo_id}=%s", (valor_id,))
