# -*- coding: utf-8 -*-
"""
Modelos de SQLAlchemy basados en la estructura de la base de datos MySQL
18 tablas mapeadas exactamente a la estructura existente
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# ================== TABLAS PRINCIPALES ==================


class Rol(Base):
    __tablename__ = 'Roles'

    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50))

    # Relaciones
    cuentas = relationship("Cuenta", back_populates="rol")


class Cuenta(Base):
    __tablename__ = 'Cuentas'

    id_cuenta = Column(Integer, primary_key=True, autoincrement=True)
    id_rol = Column(Integer, ForeignKey('Roles.id_rol'))
    password = Column(String(255))

    # Relaciones
    rol = relationship("Rol", back_populates="cuentas")
    alumno = relationship("Alumno", back_populates="cuenta", uselist=False)
    maestro = relationship("Maestro", back_populates="cuenta", uselist=False)
    administrador = relationship(
        "Administrador", back_populates="cuenta", uselist=False)
    solicitudes = relationship("Solicitud", back_populates="cuenta")


class Alumno(Base):
    __tablename__ = 'Alumno'

    id_alumno = Column(Integer, primary_key=True, autoincrement=True)
    id_cuenta = Column(Integer, ForeignKey('Cuentas.id_cuenta'))
    numero_control = Column(String(20))
    nombre_alumno = Column(String(100))
    apellido_paterno = Column(String(100))
    apellido_materno = Column(String(100))
    correo_alumno = Column(String(150))
    id_carrera = Column(Integer, ForeignKey('Carreras.id_carrera'))
    semestre = Column(Integer)
    estatus_alumno = Column(String(50))

    # Relaciones
    cuenta = relationship("Cuenta", back_populates="alumno")
    carrera = relationship("Carrera", back_populates="alumnos")
    registros = relationship("Registro", back_populates="alumno")


class Maestro(Base):
    __tablename__ = 'Maestro'

    id_maestro = Column(Integer, primary_key=True, autoincrement=True)
    id_cuenta = Column(Integer, ForeignKey('Cuentas.id_cuenta'))
    matricula = Column(String(20))
    nombre_maestro = Column(String(100))
    apellido_paterno = Column(String(100))
    apellido_materno = Column(String(100))
    correo = Column(String(150))
    estatus = Column(String(50))
    grado_estudios = Column(String(100))
    perfil_docente = Column(String(200))
    carga_academica = Column(Integer)
    tipo_contrato = Column(String(50))
    cedula_profesional = Column(String(50))

    # Relaciones
    cuenta = relationship("Cuenta", back_populates="maestro")
    grupos = relationship("Grupo", back_populates="maestro")


class Administrador(Base):
    __tablename__ = 'Administrador'

    id_administrador = Column(Integer, primary_key=True, autoincrement=True)
    id_cuenta = Column(Integer, ForeignKey('Cuentas.id_cuenta'))
    matricula = Column(String(20))
    nombre = Column(String(100))
    apellido_paterno = Column(String(100))
    apellido_materno = Column(String(100))

    # Relaciones
    cuenta = relationship("Cuenta", back_populates="administrador")
    solicitudes = relationship("Solicitud", back_populates="administrador")


class Carrera(Base):
    __tablename__ = 'Carreras'

    id_carrera = Column(Integer, primary_key=True, autoincrement=True)
    nombre_carrera = Column(String(100))
    tipo_carrera = Column(String(50))
    numero_semestres = Column(Integer)
    clave_carrera = Column(String(20))

    # Relaciones
    alumnos = relationship("Alumno", back_populates="carrera")
    materias = relationship("Materia", back_populates="carrera")


class Materia(Base):
    __tablename__ = 'Materia'

    id_materia = Column(Integer, primary_key=True, autoincrement=True)
    clave = Column(String(20))
    nombre_materia = Column(String(100))
    horas_semana = Column(Integer)
    id_carrera = Column(Integer, ForeignKey('Carreras.id_carrera'))
    unidades = Column(Integer)

    # Relaciones
    carrera = relationship("Carrera", back_populates="materias")
    grupos = relationship("Grupo", back_populates="materia")
    unidades = relationship("Unidad", back_populates="materia")


class Unidad(Base):
    __tablename__ = 'Unidad'

    id_unidad = Column(Integer, primary_key=True, autoincrement=True)
    id_materia = Column(Integer, ForeignKey('Materia.id_materia'))
    numero_unidad = Column(Integer)
    tema_unidad = Column(String(150))
    descripcion = Column(Text)

    # Relaciones
    materia = relationship("Materia", back_populates="unidades")
    actividades = relationship("Actividad", back_populates="unidad")
    calificaciones_unidad = relationship(
        "CalificacionesUnidad", back_populates="unidad")
    bonus_unidad = relationship("BonusUnidad", back_populates="unidad")


class Grupo(Base):
    __tablename__ = 'Grupo'

    id_grupo = Column(Integer, primary_key=True, autoincrement=True)
    id_maestro = Column(Integer, ForeignKey('Maestro.id_maestro'))
    id_materia = Column(Integer, ForeignKey('Materia.id_materia'))
    cupo_maximo = Column(Integer)
    periodo = Column(String(50))
    horario = Column(Text)
    alumnos_inscritos = Column(Integer)
    years = Column(Integer)  # MySQL YEAR → PostgreSQL INTEGER
    estado = Column(String(50))

    # Relaciones
    maestro = relationship("Maestro", back_populates="grupos")
    materia = relationship("Materia", back_populates="grupos")
    registros = relationship("Registro", back_populates="grupo")


class Registro(Base):
    __tablename__ = 'Registro'

    id_registro = Column(Integer, primary_key=True, autoincrement=True)
    id_alumno = Column(Integer, ForeignKey('Alumno.id_alumno'))
    id_grupo = Column(Integer, ForeignKey('Grupo.id_grupo'))
    estatus_materia = Column(String(50))
    tipo_registro = Column(String(50))

    # Relaciones
    alumno = relationship("Alumno", back_populates="registros")
    grupo = relationship("Grupo", back_populates="registros")
    actividades = relationship("Actividad", back_populates="registro")
    calificaciones_unidad = relationship(
        "CalificacionesUnidad", back_populates="registro")
    bonus_materia = relationship("BonusMateria", back_populates="registro")
    bonus_unidad = relationship("BonusUnidad", back_populates="registro")
    calificacion_final = relationship(
        "CalificacionFinal", back_populates="registro")
    resultados = relationship("Resultado", back_populates="registro")


class TipoActividad(Base):
    __tablename__ = 'Tipos_actividades'

    id_tipo = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100))
    descripcion = Column(Text)

    # Relaciones
    actividades = relationship("Actividad", back_populates="tipo_actividad")


class Actividad(Base):
    __tablename__ = 'Actividad'

    id_actividad = Column(Integer, primary_key=True, autoincrement=True)
    id_tipo = Column(Integer, ForeignKey('Tipos_actividades.id_tipo'))
    id_unidad = Column(Integer, ForeignKey('Unidad.id_unidad'))
    ponderacion = Column(Numeric(5, 2))
    detalles = Column(Text)

    # Relaciones
    tipo_actividad = relationship(
        "TipoActividad", back_populates="actividades")
    unidad = relationship("Unidad", back_populates="actividades")
    registro = relationship("Registro", back_populates="actividades")
    resultados = relationship("Resultado", back_populates="actividad")


class CalificacionesUnidad(Base):
    __tablename__ = 'Calificaciones_unidad'

    id_calificacion_unidad = Column(
        Integer, primary_key=True, autoincrement=True)
    id_registro = Column(Integer, ForeignKey('Registro.id_registro'))
    id_unidad = Column(Integer, ForeignKey('Unidad.id_unidad'))
    calificacion = Column(Numeric(5, 2))
    intentos = Column(Integer)
    fecha_modificacion = Column(DateTime)

    # Relaciones
    registro = relationship("Registro", back_populates="calificaciones_unidad")
    unidad = relationship("Unidad", back_populates="calificaciones_unidad")


class BonusUnidad(Base):
    __tablename__ = 'BonusUnidad'

    id_bonusUnidad = Column(Integer, primary_key=True, autoincrement=True)
    id_registro = Column(Integer, ForeignKey('Registro.id_registro'))
    id_unidad = Column(Integer, ForeignKey('Unidad.id_unidad'))
    valor = Column(Numeric(5, 2))
    justificacion = Column(Text)

    # Relaciones
    registro = relationship("Registro", back_populates="bonus_unidad")
    unidad = relationship("Unidad", back_populates="bonus_unidad")


class BonusMateria(Base):
    __tablename__ = 'BonusMateria'

    id_bonusMateria = Column(Integer, primary_key=True, autoincrement=True)
    id_registro = Column(Integer, ForeignKey('Registro.id_registro'))
    valor = Column(Numeric(5, 2))
    justificacion = Column(Text)

    # Relaciones
    registro = relationship("Registro", back_populates="bonus_materia")


class CalificacionFinal(Base):
    __tablename__ = 'Calificacion_final'

    id_final = Column(Integer, primary_key=True, autoincrement=True)
    id_registro = Column(Integer, ForeignKey('Registro.id_registro'))
    calificacion = Column(Numeric(5, 2))
    fecha_modificacion = Column(DateTime)

    # Relaciones
    registro = relationship("Registro", back_populates="calificacion_final")


class Resultado(Base):
    __tablename__ = 'Resultado'

    id_resultado = Column(Integer, primary_key=True, autoincrement=True)
    id_registro = Column(Integer, ForeignKey('Registro.id_registro'))
    id_actividad = Column(Integer, ForeignKey('Actividad.id_actividad'))
    calificacion = Column(Numeric(5, 2))
    fecha_registro = Column(Date)
    fecha_modificacion = Column(DateTime)
    observaciones = Column(Text)

    # Relaciones
    registro = relationship("Registro", back_populates="resultados")
    actividad = relationship("Actividad", back_populates="resultados")


class Solicitud(Base):
    __tablename__ = 'Solicitudes'

    id_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    id_cuenta = Column(Integer, ForeignKey('Cuentas.id_cuenta'))
    motivo = Column(Text)
    estado = Column(String(50))
    id_administrador = Column(Integer, ForeignKey(
        'Administrador.id_administrador'))

    # Relaciones
    cuenta = relationship("Cuenta", back_populates="solicitudes")
    administrador = relationship("Administrador", back_populates="solicitudes")


# ================== METAINFO ==================
"""
Total de tablas: 18
- Roles (3)
- Cuentas (7)
- Alumno (4)
- Maestro (2)
- Administrador (2)
- Carreras (11)
- Materia (3)
- Unidad (3)
- Grupo (3)
- Registro (3)
- Tipos_actividades (8)
- Actividad (3)
- Calificaciones_unidad (0)
- BonusUnidad (0)
- BonusMateria (0)
- Calificacion_final (3)
- Resultado (0)
- Solicitudes (0)

Total de registros: 55
"""
