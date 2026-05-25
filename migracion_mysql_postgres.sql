-- ==================================================
-- MIGRACION MYSQL → POSTGRESQL
-- Base de datos: db_escolar
-- Fecha: 2026-05-10 19:55:44
-- Total tablas: 18
-- ==================================================

-- ==================================================
-- ESTRUCTURA DE TABLAS
-- ==================================================

-- Tabla: Carreras
DROP TABLE IF EXISTS "carreras" CASCADE;
CREATE TABLE "carreras" (
    "id_carrera" SERIAL PRIMARY KEY,
    "nombre_carrera" VARCHAR(100),
    "tipo_carrera" VARCHAR(50),
    "numero_semestres" INTEGER,
    "clave_carrera" VARCHAR(20)
);

-- Tabla: Materia
DROP TABLE IF EXISTS "materia" CASCADE;
CREATE TABLE "materia" (
    "id_materia" SERIAL PRIMARY KEY,
    "clave" VARCHAR(20),
    "nombre_materia" VARCHAR(100),
    "horas_semana" INTEGER,
    "id_carrera" INTEGER,
    "unidades" INTEGER,
    FOREIGN KEY ("id_carrera") REFERENCES "carreras" ("id_carrera")
);

-- Tabla: Roles
DROP TABLE IF EXISTS "roles" CASCADE;
CREATE TABLE "roles" (
    "id_rol" SERIAL PRIMARY KEY,
    "nombre" VARCHAR(50)
);

-- Tabla: Cuentas
DROP TABLE IF EXISTS "cuentas" CASCADE;
CREATE TABLE "cuentas" (
    "id_cuenta" SERIAL PRIMARY KEY,
    "id_rol" INTEGER,
    "password" VARCHAR(255),
    FOREIGN KEY ("id_rol") REFERENCES "roles" ("id_rol")
);

-- Tabla: Administrador
DROP TABLE IF EXISTS "administrador" CASCADE;
CREATE TABLE "administrador" (
    "id_administrador" SERIAL PRIMARY KEY,
    "matricula" VARCHAR(20),
    "nombre" VARCHAR(100),
    "apellido_paterno" VARCHAR(100),
    "apellido_materno" VARCHAR(100),
    "id_cuenta" INTEGER,
    FOREIGN KEY ("id_cuenta") REFERENCES "cuentas" ("id_cuenta")
);

-- Tabla: Alumno
DROP TABLE IF EXISTS "alumno" CASCADE;
CREATE TABLE "alumno" (
    "id_alumno" SERIAL PRIMARY KEY,
    "id_cuenta" INTEGER,
    "numero_control" VARCHAR(20),
    "nombre_alumno" VARCHAR(100),
    "apellido_paterno" VARCHAR(100),
    "apellido_materno" VARCHAR(100),
    "correo_alumno" VARCHAR(150),
    "id_carrera" INTEGER,
    "semestre" INTEGER,
    "estatus_alumno" VARCHAR(50),
    FOREIGN KEY ("id_cuenta") REFERENCES "cuentas" ("id_cuenta"),
    FOREIGN KEY ("id_carrera") REFERENCES "carreras" ("id_carrera")
);

-- Tabla: Maestro
DROP TABLE IF EXISTS "maestro" CASCADE;
CREATE TABLE "maestro" (
    "id_maestro" SERIAL PRIMARY KEY,
    "id_cuenta" INTEGER,
    "matricula" VARCHAR(20),
    "nombre_maestro" VARCHAR(100),
    "apellido_paterno" VARCHAR(100),
    "apellido_materno" VARCHAR(100),
    "correo" VARCHAR(150),
    "estatus" VARCHAR(50),
    "grado_estudios" VARCHAR(100),
    "perfil_docente" VARCHAR(200),
    "carga_academica" INTEGER,
    "tipo_contrato" VARCHAR(50),
    "cedula_profesional" VARCHAR(50),
    FOREIGN KEY ("id_cuenta") REFERENCES "cuentas" ("id_cuenta")
);

-- Tabla: Grupo
DROP TABLE IF EXISTS "grupo" CASCADE;
CREATE TABLE "grupo" (
    "id_grupo" SERIAL PRIMARY KEY,
    "id_maestro" INTEGER,
    "id_materia" INTEGER,
    "cupo_maximo" INTEGER,
    "periodo" VARCHAR(50),
    "horario" TEXT,
    "alumnos_inscritos" INTEGER,
    "years" INTEGER,
    "estado" VARCHAR(50),
    FOREIGN KEY ("id_maestro") REFERENCES "maestro" ("id_maestro"),
    FOREIGN KEY ("id_materia") REFERENCES "materia" ("id_materia")
);

-- Tabla: Registro
DROP TABLE IF EXISTS "registro" CASCADE;
CREATE TABLE "registro" (
    "id_registro" SERIAL PRIMARY KEY,
    "id_alumno" INTEGER,
    "id_grupo" INTEGER,
    "estatus_materia" VARCHAR(50),
    "tipo_registro" VARCHAR(50),
    FOREIGN KEY ("id_alumno") REFERENCES "alumno" ("id_alumno"),
    FOREIGN KEY ("id_grupo") REFERENCES "grupo" ("id_grupo")
);

-- Tabla: BonusMateria
DROP TABLE IF EXISTS "bonusmateria" CASCADE;
CREATE TABLE "bonusmateria" (
    "id_bonusMateria" SERIAL PRIMARY KEY,
    "id_registro" INTEGER,
    "valor" NUMERIC(5,2),
    "justificacion" TEXT,
    FOREIGN KEY ("id_registro") REFERENCES "registro" ("id_registro")
);

-- Tabla: Calificacion_final
DROP TABLE IF EXISTS "calificacion_final" CASCADE;
CREATE TABLE "calificacion_final" (
    "id_final" SERIAL PRIMARY KEY,
    "id_registro" INTEGER,
    "calificacion" NUMERIC(5,2),
    "fecha_modificacion" TIMESTAMP,
    FOREIGN KEY ("id_registro") REFERENCES "registro" ("id_registro")
);

-- Tabla: Solicitudes
DROP TABLE IF EXISTS "solicitudes" CASCADE;
CREATE TABLE "solicitudes" (
    "id_solicitud" SERIAL PRIMARY KEY,
    "id_cuenta" INTEGER,
    "motivo" TEXT,
    "estado" VARCHAR(50),
    "id_administrador" INTEGER,
    FOREIGN KEY ("id_cuenta") REFERENCES "cuentas" ("id_cuenta"),
    FOREIGN KEY ("id_administrador") REFERENCES "administrador" ("id_administrador")
);

-- Tabla: Tipos_actividades
DROP TABLE IF EXISTS "tipos_actividades" CASCADE;
CREATE TABLE "tipos_actividades" (
    "id_tipo" SERIAL PRIMARY KEY,
    "nombre" VARCHAR(100)
);

-- Tabla: Unidad
DROP TABLE IF EXISTS "unidad" CASCADE;
CREATE TABLE "unidad" (
    "id_unidad" SERIAL PRIMARY KEY,
    "id_materia" INTEGER,
    "numero_unidad" INTEGER,
    "tema_unidad" VARCHAR(150),
    "descripcion" TEXT,
    FOREIGN KEY ("id_materia") REFERENCES "materia" ("id_materia")
);

-- Tabla: Actividad
DROP TABLE IF EXISTS "actividad" CASCADE;
CREATE TABLE "actividad" (
    "id_actividad" SERIAL PRIMARY KEY,
    "id_tipo" INTEGER,
    "id_unidad" INTEGER,
    "ponderacion" NUMERIC(5,2),
    "detalles" TEXT,
    FOREIGN KEY ("id_tipo") REFERENCES "tipos_actividades" ("id_tipo"),
    FOREIGN KEY ("id_unidad") REFERENCES "unidad" ("id_unidad")
);

-- Tabla: BonusUnidad
DROP TABLE IF EXISTS "bonusunidad" CASCADE;
CREATE TABLE "bonusunidad" (
    "id_bonusUnidad" SERIAL PRIMARY KEY,
    "id_registro" INTEGER,
    "id_unidad" INTEGER,
    "valor" NUMERIC(5,2),
    "justificacion" TEXT,
    FOREIGN KEY ("id_registro") REFERENCES "registro" ("id_registro"),
    FOREIGN KEY ("id_unidad") REFERENCES "unidad" ("id_unidad")
);

-- Tabla: Calificaciones_unidad
DROP TABLE IF EXISTS "calificaciones_unidad" CASCADE;
CREATE TABLE "calificaciones_unidad" (
    "id_calificacion_unidad" SERIAL PRIMARY KEY,
    "id_registro" INTEGER,
    "id_unidad" INTEGER,
    "calificacion" NUMERIC(5,2),
    "intentos" INTEGER,
    "fecha_modificacion" TIMESTAMP,
    FOREIGN KEY ("id_registro") REFERENCES "registro" ("id_registro"),
    FOREIGN KEY ("id_unidad") REFERENCES "unidad" ("id_unidad")
);

-- Tabla: Resultado
DROP TABLE IF EXISTS "resultado" CASCADE;
CREATE TABLE "resultado" (
    "id_resultado" SERIAL PRIMARY KEY,
    "id_registro" INTEGER,
    "id_actividad" INTEGER,
    "calificacion" NUMERIC(5,2),
    "fecha_registro" DATE,
    "fecha_modificacion" TIMESTAMP,
    "observaciones" TEXT,
    FOREIGN KEY ("id_registro") REFERENCES "registro" ("id_registro"),
    FOREIGN KEY ("id_actividad") REFERENCES "actividad" ("id_actividad")
);


-- ==================================================
-- MIGRACION DE DATOS
-- ==================================================

-- Datos para tabla: Carreras
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (1, 'Ingeniería en Sistemas Computacionales', 'Ingeniería', 9, 'ISIC-2010-224');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (2, 'Ingeniería Industrial', 'Ingeniería', 9, 'II');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (3, 'Ingeniería Electromecánica', 'Ingeniería', 9, 'IEM');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (4, 'Ingeniería Eléctrica', 'Ingeniería', 9, 'IE');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (5, 'Ingeniería Electrónica', 'Ingeniería', 9, 'IELEC');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (6, 'Ingeniería Civil', 'Ingeniería', 9, 'IC');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (7, 'Ingeniería Química', 'Ingeniería', 9, 'IQ');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (8, 'Ingeniería Bioquímica', 'Ingeniería', 9, 'IBQ');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (9, 'Ingeniería en Gestión Empresarial', 'Ingeniería', 9, 'IGE');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (10, 'Licenciatura en Administración', 'Licenciatura', 8, 'LA');
INSERT INTO "carreras" ("id_carrera", "nombre_carrera", "tipo_carrera", "numero_semestres", "clave_carrera") VALUES (11, 'Ingeniería en Inteligencia Artificial', 'Ingeniería', 10, 'AI-2026-CPU');

-- Datos para tabla: Materia
INSERT INTO "materia" ("id_materia", "clave", "nombre_materia", "horas_semana", "id_carrera", "unidades") VALUES (1, 'ISC101', 'Programación I', 4, 1, 2);
INSERT INTO "materia" ("id_materia", "clave", "nombre_materia", "horas_semana", "id_carrera", "unidades") VALUES (2, 'FDB', 'Fundamentos de Bases de Datos', 5, 1, 6);
INSERT INTO "materia" ("id_materia", "clave", "nombre_materia", "horas_semana", "id_carrera", "unidades") VALUES (3, 'IND101', 'Cálculo Industrial', 3, 2, 2);

-- Datos para tabla: Roles
INSERT INTO "roles" ("id_rol", "nombre") VALUES (1, 'Administrador');
INSERT INTO "roles" ("id_rol", "nombre") VALUES (2, 'Maestro');
INSERT INTO "roles" ("id_rol", "nombre") VALUES (3, 'Alumno');

-- Datos para tabla: Cuentas
INSERT INTO "cuentas" ("id_cuenta", "id_rol", "password") VALUES (1, 3, 'alumno123');
INSERT INTO "cuentas" ("id_cuenta", "id_rol", "password") VALUES (2, 3, 'password123');
INSERT INTO "cuentas" ("id_cuenta", "id_rol", "password") VALUES (3, 3, 'password123');
INSERT INTO "cuentas" ("id_cuenta", "id_rol", "password") VALUES (4, 3, 'password123');
INSERT INTO "cuentas" ("id_cuenta", "id_rol", "password") VALUES (5, 2, 'password123');
INSERT INTO "cuentas" ("id_cuenta", "id_rol", "password") VALUES (6, 2, 'password123');
INSERT INTO "cuentas" ("id_cuenta", "id_rol", "password") VALUES (7, 1, 'admin123');

-- Datos para tabla: Administrador
INSERT INTO "administrador" ("id_administrador", "matricula", "nombre", "apellido_paterno", "apellido_materno", "id_cuenta") VALUES (1, 'ADM001', 'Laura', 'Hernández', 'Soto', 7);
INSERT INTO "administrador" ("id_administrador", "matricula", "nombre", "apellido_paterno", "apellido_materno", "id_cuenta") VALUES (2, 'ADM2610935', 'Ximena', 'Torres', 'Galvan', NULL);

-- Datos para tabla: Alumno
INSERT INTO "alumno" ("id_alumno", "id_cuenta", "numero_control", "nombre_alumno", "apellido_paterno", "apellido_materno", "correo_alumno", "id_carrera", "semestre", "estatus_alumno") VALUES (1, 1, 'A2600001', 'Juan', 'Pérez', 'Ramírez', 'A2600001@veracruz.tecnm.mx', 1, 3, 'Activo');
INSERT INTO "alumno" ("id_alumno", "id_cuenta", "numero_control", "nombre_alumno", "apellido_paterno", "apellido_materno", "correo_alumno", "id_carrera", "semestre", "estatus_alumno") VALUES (2, 2, 'A2600002', 'María', 'García', 'López', 'A2600002@veracruz.tecnm.mx', 1, 2, 'Activo');
INSERT INTO "alumno" ("id_alumno", "id_cuenta", "numero_control", "nombre_alumno", "apellido_paterno", "apellido_materno", "correo_alumno", "id_carrera", "semestre", "estatus_alumno") VALUES (3, 3, 'A2600003', 'Carlos', 'Rodríguez', 'Martínez', 'A2600003@veracruz.tecnm.mx', 2, 1, 'Activo');
INSERT INTO "alumno" ("id_alumno", "id_cuenta", "numero_control", "nombre_alumno", "apellido_paterno", "apellido_materno", "correo_alumno", "id_carrera", "semestre", "estatus_alumno") VALUES (4, 4, 'A2600004', 'Ana', 'Flores', 'Jiménez', 'A2600004@veracruz.tecnm.mx', 1, 3, 'Activo');

-- Datos para tabla: Maestro
INSERT INTO "maestro" ("id_maestro", "id_cuenta", "matricula", "nombre_maestro", "apellido_paterno", "apellido_materno", "correo", "estatus", "grado_estudios", "perfil_docente", "carga_academica", "tipo_contrato", "cedula_profesional") VALUES (1, 5, 'M001', 'Dr. Juan', 'Hernández', 'García', 'juan.hernandez@tecnm.mx', 'Activo', 'Maestría', 'Investigador', 25, 'Tiempo Completo', '12345678');
INSERT INTO "maestro" ("id_maestro", "id_cuenta", "matricula", "nombre_maestro", "apellido_paterno", "apellido_materno", "correo", "estatus", "grado_estudios", "perfil_docente", "carga_academica", "tipo_contrato", "cedula_profesional") VALUES (2, 6, 'M002', 'Lic. María', 'Sánchez', 'Ruiz', 'maria.sanchez@tecnm.mx', 'Activo', 'Licenciatura', 'Docente', 20, 'Tiempo Parcial', '87654321');

-- Datos para tabla: Grupo
INSERT INTO "grupo" ("id_grupo", "id_maestro", "id_materia", "cupo_maximo", "periodo", "horario", "alumnos_inscritos", "years", "estado") VALUES (1, 1, 1, 30, '2026-1', '8:00-10:00', 0, 2026, 'Activo');
INSERT INTO "grupo" ("id_grupo", "id_maestro", "id_materia", "cupo_maximo", "periodo", "horario", "alumnos_inscritos", "years", "estado") VALUES (2, 2, 2, 25, '2026-1', '10:00-12:00', 0, 2026, 'Activo');
INSERT INTO "grupo" ("id_grupo", "id_maestro", "id_materia", "cupo_maximo", "periodo", "horario", "alumnos_inscritos", "years", "estado") VALUES (3, 1, 3, 20, '2026-1', '14:00-16:00', 0, 2026, 'Activo');

-- Datos para tabla: Registro
INSERT INTO "registro" ("id_registro", "id_alumno", "id_grupo", "estatus_materia", "tipo_registro") VALUES (1, 1, 1, 'Aprobado', 'Regular');
INSERT INTO "registro" ("id_registro", "id_alumno", "id_grupo", "estatus_materia", "tipo_registro") VALUES (2, 2, 2, 'En Curso', 'Regular');
INSERT INTO "registro" ("id_registro", "id_alumno", "id_grupo", "estatus_materia", "tipo_registro") VALUES (3, 3, 1, 'Aprobado', 'Regular');

-- Datos para tabla: Calificacion_final
INSERT INTO "calificacion_final" ("id_final", "id_registro", "calificacion", "fecha_modificacion") VALUES (1, 1, 95.00, NULL);
INSERT INTO "calificacion_final" ("id_final", "id_registro", "calificacion", "fecha_modificacion") VALUES (2, 2, 88.50, NULL);
INSERT INTO "calificacion_final" ("id_final", "id_registro", "calificacion", "fecha_modificacion") VALUES (3, 3, 91.00, NULL);

-- Datos para tabla: Tipos_actividades
INSERT INTO "tipos_actividades" ("id_tipo", "nombre") VALUES (1, 'Exposición');
INSERT INTO "tipos_actividades" ("id_tipo", "nombre") VALUES (2, 'Proyecto Final');
INSERT INTO "tipos_actividades" ("id_tipo", "nombre") VALUES (3, 'Trabajo de Investigación');
INSERT INTO "tipos_actividades" ("id_tipo", "nombre") VALUES (4, 'Práctica de Laboratorio');
INSERT INTO "tipos_actividades" ("id_tipo", "nombre") VALUES (5, 'Problemario');
INSERT INTO "tipos_actividades" ("id_tipo", "nombre") VALUES (6, 'Ensayo');
INSERT INTO "tipos_actividades" ("id_tipo", "nombre") VALUES (7, 'Portafolio de Evidencias');
INSERT INTO "tipos_actividades" ("id_tipo", "nombre") VALUES (8, 'Examen');

-- Datos para tabla: Unidad
INSERT INTO "unidad" ("id_unidad", "id_materia", "numero_unidad", "tema_unidad", "descripcion") VALUES (1, 1, 1, 'Introducci?n', 'Unidad introductoria');
INSERT INTO "unidad" ("id_unidad", "id_materia", "numero_unidad", "tema_unidad", "descripcion") VALUES (2, 2, 2, 'Desarrollo', 'Unidad de desarrollo');
INSERT INTO "unidad" ("id_unidad", "id_materia", "numero_unidad", "tema_unidad", "descripcion") VALUES (3, 3, 3, 'Aplicaci?n', 'Unidad de aplicaci?n');

-- Datos para tabla: Actividad
INSERT INTO "actividad" ("id_actividad", "id_tipo", "id_unidad", "ponderacion", "detalles") VALUES (1, 1, 1, 1.00, 'Programación I');
INSERT INTO "actividad" ("id_actividad", "id_tipo", "id_unidad", "ponderacion", "detalles") VALUES (2, 2, 2, 30.00, 'Proyecto final de la unidad 2');
INSERT INTO "actividad" ("id_actividad", "id_tipo", "id_unidad", "ponderacion", "detalles") VALUES (3, 3, 3, 3.00, 'Cálculo Industrial');

-- ==================================================
-- RESET SECUENCIAS (SERIAL)
-- ==================================================

SELECT setval('"actividad_id_actividad_seq"', (SELECT COALESCE(MAX("id_actividad"), 1) FROM "actividad"));
SELECT setval('"administrador_id_administrador_seq"', (SELECT COALESCE(MAX("id_administrador"), 1) FROM "administrador"));
SELECT setval('"alumno_id_alumno_seq"', (SELECT COALESCE(MAX("id_alumno"), 1) FROM "alumno"));
SELECT setval('"bonusmateria_id_bonusMateria_seq"', (SELECT COALESCE(MAX("id_bonusMateria"), 1) FROM "bonusmateria"));
SELECT setval('"bonusunidad_id_bonusUnidad_seq"', (SELECT COALESCE(MAX("id_bonusUnidad"), 1) FROM "bonusunidad"));
SELECT setval('"calificacion_final_id_final_seq"', (SELECT COALESCE(MAX("id_final"), 1) FROM "calificacion_final"));
SELECT setval('"calificaciones_unidad_id_calificacion_unidad_seq"', (SELECT COALESCE(MAX("id_calificacion_unidad"), 1) FROM "calificaciones_unidad"));
SELECT setval('"carreras_id_carrera_seq"', (SELECT COALESCE(MAX("id_carrera"), 1) FROM "carreras"));
SELECT setval('"cuentas_id_cuenta_seq"', (SELECT COALESCE(MAX("id_cuenta"), 1) FROM "cuentas"));
SELECT setval('"grupo_id_grupo_seq"', (SELECT COALESCE(MAX("id_grupo"), 1) FROM "grupo"));
SELECT setval('"maestro_id_maestro_seq"', (SELECT COALESCE(MAX("id_maestro"), 1) FROM "maestro"));
SELECT setval('"materia_id_materia_seq"', (SELECT COALESCE(MAX("id_materia"), 1) FROM "materia"));
SELECT setval('"registro_id_registro_seq"', (SELECT COALESCE(MAX("id_registro"), 1) FROM "registro"));
SELECT setval('"resultado_id_resultado_seq"', (SELECT COALESCE(MAX("id_resultado"), 1) FROM "resultado"));
SELECT setval('"roles_id_rol_seq"', (SELECT COALESCE(MAX("id_rol"), 1) FROM "roles"));
SELECT setval('"solicitudes_id_solicitud_seq"', (SELECT COALESCE(MAX("id_solicitud"), 1) FROM "solicitudes"));
SELECT setval('"tipos_actividades_id_tipo_seq"', (SELECT COALESCE(MAX("id_tipo"), 1) FROM "tipos_actividades"));
SELECT setval('"unidad_id_unidad_seq"', (SELECT COALESCE(MAX("id_unidad"), 1) FROM "unidad"));

-- ==================================================
-- MIGRACION COMPLETADA
-- Total tablas: 18
-- Total filas migradas: 55
-- ==================================================
