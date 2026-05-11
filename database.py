# -*- coding: utf-8 -*-
"""
Configuracion de SQLAlchemy para PostgreSQL
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuracion de PostgreSQL
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Crear el motor de conexion
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para ver las queries SQL en consola
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_size=5,
    max_overflow=10
)

# Base declarativa para los modelos
Base = declarative_base()

# Sesion factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Obtener una sesion de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializar la base de datos creando todas las tablas"""
    from models import *  # Importar todos los modelos
    Base.metadata.create_all(bind=engine)
    print("[OK] Base de datos inicializada correctamente")

def drop_db():
    """Eliminar todas las tablas (CUIDADO: borra todo)"""
    from models import *  # Importar todos los modelos
    Base.metadata.drop_all(bind=engine)
    print("[OK] Todas las tablas han sido eliminadas")
