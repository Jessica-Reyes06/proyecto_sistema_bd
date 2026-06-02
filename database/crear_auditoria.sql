-- ==================================================
-- TABLA DE AUDITORIA DE CAMBIOS
-- Registra cambios hechos por administradores
-- ==================================================

DROP TABLE IF EXISTS "auditoria_cambios" CASCADE;
CREATE TABLE "auditoria_cambios" (
    "id_auditoria" SERIAL PRIMARY KEY,
    "id_admin" INTEGER,
    "tabla_afectada" VARCHAR(50),
    "tipo_operacion" VARCHAR(10),
    "id_registro" INTEGER,
    "descripcion" TEXT,
    "fecha_hora" TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY ("id_admin") REFERENCES "administrador" ("id_administrador")
);

-- Índices para búsquedas rápidas
CREATE INDEX idx_auditoria_admin ON "auditoria_cambios" ("id_admin");
CREATE INDEX idx_auditoria_tabla ON "auditoria_cambios" ("tabla_afectada");
CREATE INDEX idx_auditoria_fecha ON "auditoria_cambios" ("fecha_hora" DESC);

-- ==================================================
-- DATOS DE PRUEBA (Fake Data)
-- ==================================================
INSERT INTO "auditoria_cambios" (id_admin, tabla_afectada, tipo_operacion, id_registro, descripcion, fecha_hora) VALUES
(1, 'Alumno', 'INSERT', 21490, 'Administrador1 registró alumno 21490 - Juan Pérez López', NOW() - INTERVAL '5 days'),
(1, 'Alumno', 'UPDATE', 21490, 'Administrador1 actualizó alumno 21490 - Juan Pérez López', NOW() - INTERVAL '4 days'),
(1, 'Maestro', 'INSERT', 1001, 'Administrador1 registró maestro M001 - Carlos García Rodríguez', NOW() - INTERVAL '3 days'),
(1, 'Grupo', 'INSERT', 101, 'Administrador1 registró grupo ISC-101 - Programación I', NOW() - INTERVAL '2.5 days'),
(1, 'Materia', 'INSERT', 5, 'Administrador1 registró materia PROG-101 - Fundamentos de Programación', NOW() - INTERVAL '2 days'),
(1, 'Registro', 'INSERT', 501, 'Administrador1 registró inscripción 21490 - Programación I', NOW() - INTERVAL '1.5 days'),
(1, 'Alumno', 'INSERT', 21491, 'Administrador1 registró alumno 21491 - María Hernández Sánchez', NOW() - INTERVAL '1 day'),
(1, 'Alumno', 'INSERT', 21492, 'Administrador1 registró alumno 21492 - Roberto Martínez González', NOW() - INTERVAL '18 hours'),
(1, 'Grupo', 'UPDATE', 101, 'Administrador1 actualizó grupo ISC-101 - Cambio de horario', NOW() - INTERVAL '12 hours'),
(1, 'Registro', 'DELETE', 500, 'Administrador1 eliminó inscripción 21489 - Cancelación', NOW() - INTERVAL '8 hours'),
(1, 'Maestro', 'UPDATE', 1001, 'Administrador1 actualizó maestro M001 - Actualización de datos', NOW() - INTERVAL '6 hours'),
(1, 'Carreras', 'INSERT', 1, 'Administrador1 registró carrera ISC - Ingeniería en Sistemas Computacionales', NOW() - INTERVAL '4 hours'),
(1, 'Alumno', 'INSERT', 21493, 'Administrador1 registró alumnos por csv', NOW() - INTERVAL '2 hours'),
(1, 'Administrador', 'INSERT', 2, 'Administrador1 registró administrador A002 - Sofía Ramírez Torres', NOW() - INTERVAL '1 hour'),
(1, 'Grupo', 'INSERT', 102, 'Administrador1 registró grupo ISC-102 - Programación II', NOW() - INTERVAL '30 minutes');

SELECT 'Tabla auditoria_cambios creada exitosamente con datos de prueba' AS resultado;
