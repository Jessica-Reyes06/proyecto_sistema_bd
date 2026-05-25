import customtkinter
from db_conexion import ejecutar_update
from config_principal import limpiar_frame
from formularios_bd import crear_campo, crear_combo

# EDITAR CARRERAS
def editar_carreras(frame_contenido, id_carrera, nombre_carrera, tipo_carrera, numero_semestres, clave_carrera, volver_a_lista=None):
    """
    Formulario para editar una carrera existente
    Recibe los datos actuales del registro y permite modificarlos
    """
    limpiar_frame(frame_contenido)

    titulo_label = customtkinter.CTkLabel(
        frame_contenido,
        text="Editar Carrera",
        font=("Arial", 22, "bold")
    )
    titulo_label.pack(pady=(10, 20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20, pady=10, fill="x")
    
    # Configurar grid del cuerpo
    cuerpo.grid_columnconfigure(0, weight=0)
    cuerpo.grid_columnconfigure(1, weight=1)

    # Crear campos con datos precargados
    entrada_nombre = crear_campo(cuerpo, 0, "Nombre de la Carrera")
    entrada_nombre.insert(0, nombre_carrera)

    # Tipo de carrera - ComboBox
    opciones_tipo = ["Ingeniería", "Licenciatura"]
    entrada_tipo = crear_combo(cuerpo, 1, "Tipo de carrera", opciones_tipo)
    entrada_tipo.set(tipo_carrera)

    entrada_semestres = crear_campo(cuerpo, 2, "Semestres")
    entrada_semestres.insert(0, str(numero_semestres))

    entrada_clave = crear_campo(cuerpo, 3, "Clave")
    entrada_clave.insert(0, clave_carrera)

    estado_label = customtkinter.CTkLabel(frame_contenido, text="")
    estado_label.pack()

    def actualizar():
        """Ejecuta el UPDATE a la base de datos"""
        nuevo_nombre = entrada_nombre.get()
        nuevo_tipo = entrada_tipo.get()
        nuevo_semestres = entrada_semestres.get()
        nueva_clave = entrada_clave.get()

        # Validar que todos los campos estén llenos
        if "" in [nuevo_nombre, nuevo_tipo, nuevo_semestres, nueva_clave]:
            estado_label.configure(text="Todos los campos deben llenarse", text_color="red")
            return

        try:
            sql = """
            UPDATE carreras 
            SET nombre_carrera=%s, tipo_carrera=%s, numero_semestres=%s, clave_carrera=%s 
            WHERE id_carrera=%s
            """
            valores = (nuevo_nombre, nuevo_tipo, nuevo_semestres, nueva_clave, id_carrera)
            ejecutar_update(sql, valores)
            
            # Recarga la tabla inmediatamente después de actualizar
            if volver_a_lista:
                try:
                    volver_a_lista()
                except:
                    pass

        except Exception as e:
            estado_label.configure(text=f"Error al actualizar: {str(e)}", text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido, fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(
        botones,
        text="Actualizar",
        command=actualizar,
        fg_color="#007b3a"
    ).grid(row=0, column=0, padx=10)

    customtkinter.CTkButton(
        botones,
        text="Cancelar",
        command=lambda: volver_a_lista() if volver_a_lista else None,
        fg_color="#962d22"
    ).grid(row=0, column=1, padx=10)


# EDITAR MATERIAS
def editar_materias(frame_contenido, id_materia, clave, nombre_materia, horas_semana, id_carrera, unidades, volver_a_lista=None):
    """
    Formulario para editar una materia existente.
    Recibe los datos actuales del registro y permite modificarlos.
    """
    from db_conexion import ejecutar_select
    from funciones_datos import obtener_nombre_carrera_por_id, obtener_id_carrera_por_nombre
    
    limpiar_frame(frame_contenido)

    titulo_label = customtkinter.CTkLabel(
        frame_contenido,
        text="Editar Materia",
        font=("Arial", 22, "bold")
    )
    titulo_label.pack(pady=(10, 20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20, pady=10, fill="x")
    
    # Configurar grid del cuerpo
    cuerpo.grid_columnconfigure(0, weight=0)
    cuerpo.grid_columnconfigure(1, weight=1)

    # Crear campos con datos precargados
    entrada_clave = crear_campo(cuerpo, 0, "Clave")
    entrada_clave.insert(0, clave)

    entrada_nombre = crear_campo(cuerpo, 1, "Nombre de la Materia")
    entrada_nombre.insert(0, nombre_materia)

    # Combo de Carreras - Obtener nombres de carreras directamente
    try:
        resultado = ejecutar_select("SELECT nombre_carrera FROM carreras ORDER BY nombre_carrera ASC")
        carreras_lista = [row[0] for row in resultado] if resultado else ["No hay carreras"]
        nombre_carrera_actual = obtener_nombre_carrera_por_id(id_carrera)
    except Exception as e:
        print(f"Error cargando carreras: {e}")
        carreras_lista = ["Error al cargar carreras"]
        nombre_carrera_actual = "Carrera no encontrada"
    
    entrada_carrera = crear_combo(cuerpo, 2, "Carrera", carreras_lista)
    entrada_carrera.set(nombre_carrera_actual)

    entrada_horas = crear_campo(cuerpo, 3, "Horas a la semana")
    entrada_horas.insert(0, str(horas_semana))

    entrada_unidades = crear_campo(cuerpo, 4, "Unidades")
    entrada_unidades.insert(0, str(unidades))

    estado_label = customtkinter.CTkLabel(frame_contenido, text="")
    estado_label.pack()

    def actualizar():
        """Ejecuta el UPDATE a la base de datos"""
        nueva_clave = entrada_clave.get()
        nuevo_nombre = entrada_nombre.get()
        nombre_carrera_seleccionada = entrada_carrera.get()
        nuevas_horas = entrada_horas.get()
        nuevas_unidades = entrada_unidades.get()

        # Validar que todos los campos estén llenos
        if "" in [nueva_clave, nuevo_nombre, nombre_carrera_seleccionada, nuevas_horas, nuevas_unidades]:
            estado_label.configure(text="Todos los campos deben llenarse", text_color="red")
            return

        # Buscar el ID de la carrera por nombre
        nuevo_id_carrera = obtener_id_carrera_por_nombre(nombre_carrera_seleccionada)
        
        if nuevo_id_carrera is None:
            estado_label.configure(text="Error: Carrera no encontrada", text_color="red")
            return

        try:
            sql = """
            UPDATE materia 
            SET clave=%s, nombre_materia=%s, horas_semana=%s, id_carrera=%s, unidades=%s
            WHERE id_materia=%s
            """
            valores = (nueva_clave, nuevo_nombre, nuevas_horas, nuevo_id_carrera, nuevas_unidades, id_materia)
            ejecutar_update(sql, valores)
            
            # Recarga la tabla inmediatamente después de actualizar
            if volver_a_lista:
                try:
                    volver_a_lista()
                except:
                    pass

        except Exception as e:
            estado_label.configure(text=f"Error al actualizar: {str(e)}", text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido, fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(
        botones,
        text="Actualizar",
        command=actualizar,
        fg_color="#007b3a"
    ).grid(row=0, column=0, padx=10)

    customtkinter.CTkButton(
        botones,
        text="Cancelar",
        command=lambda: volver_a_lista() if volver_a_lista else None,
        fg_color="#962d22"
    ).grid(row=0, column=1, padx=10)


def editar_grupo(frame_contenido, id_grupo, nombre_maestro, nombre_materia, cupo_maximo, periodo, years, alumnos_inscritos, horario, estado, volver_a_lista=None):
    """
    Formulario para editar un grupo existente.
    Recibe los datos actuales del registro y permite modificarlos.
    """
    from db_conexion import ejecutar_select
    from funciones_datos import obtener_id_maestro_por_nombre, obtener_id_materia_por_nombre
    
    limpiar_frame(frame_contenido)

    titulo_label = customtkinter.CTkLabel(
        frame_contenido,
        text="Editar Grupo",
        font=("Arial", 22, "bold")
    )
    titulo_label.pack(pady=(10, 20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20, pady=10, fill="x")
    
    # Configurar grid del cuerpo
    cuerpo.grid_columnconfigure(0, weight=0)
    cuerpo.grid_columnconfigure(1, weight=1)

    # Crear campos con datos precargados
    entrada_id_grupo = crear_campo(cuerpo, 0, "ID Grupo")
    entrada_id_grupo.insert(0, str(id_grupo))
    entrada_id_grupo.configure(state="disabled")

    # Combo de Maestros - Obtener nombres de maestros directamente
    try:
        resultado = ejecutar_select("SELECT nombre_maestro FROM maestro ORDER BY nombre_maestro ASC")
        maestros_lista = [row[0] for row in resultado] if resultado else ["No hay maestros"]
    except Exception as e:
        print(f"Error cargando maestros: {e}")
        maestros_lista = ["Error al cargar maestros"]
    
    entrada_maestro = crear_combo(cuerpo, 1, "Maestro", maestros_lista)
    entrada_maestro.set(nombre_maestro)

    # Combo de Materias - Obtener nombres de materias directamente
    try:
        resultado = ejecutar_select("SELECT nombre_materia FROM materia ORDER BY nombre_materia ASC")
        materias_lista = [row[0] for row in resultado] if resultado else ["No hay materias"]
    except Exception as e:
        print(f"Error cargando materias: {e}")
        materias_lista = ["Error al cargar materias"]
    
    entrada_materia = crear_combo(cuerpo, 2, "Materia", materias_lista)
    entrada_materia.set(nombre_materia)

    entrada_cupo = crear_campo(cuerpo, 3, "Cupo máximo")
    entrada_cupo.insert(0, str(cupo_maximo))

    periodos = ["Enero-Junio", "Agosto-Diciembre", "Verano"]
    entrada_periodo = crear_combo(cuerpo, 4, "Periodo", periodos)
    entrada_periodo.set(periodo)

    # Año: lista desplegable pequeña desde año actual hasta 1990
    import datetime
    label_anio = customtkinter.CTkLabel(cuerpo, text="Año", font=("Arial",14))
    label_anio.grid(row=5, column=0, padx=10, pady=5, sticky="w")
    anos = [str(y) for y in range(datetime.date.today().year, 1989, -1)]
    entrada_anio = customtkinter.CTkComboBox(cuerpo, values=anos, width=120, state="readonly")
    entrada_anio.set(str(years))
    entrada_anio.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    entrada_inscritos = crear_campo(cuerpo, 6, "Inscritos")
    entrada_inscritos.insert(0, str(alumnos_inscritos))

    entrada_horario = crear_campo(cuerpo, 7, "Horario")
    entrada_horario.insert(0, horario)

    estado_combo = crear_combo(
        cuerpo,
        8,
        "Estado",
        ["Activo", "Cerrado", "Cancelado"]
    )
    estado_combo.set(estado)

    estado_label = customtkinter.CTkLabel(frame_contenido, text="")
    estado_label.pack()

    def actualizar():
        """Ejecuta el UPDATE a la base de datos"""
        nombre_maestro_seleccionado = entrada_maestro.get()
        nombre_materia_seleccionado = entrada_materia.get()
        nuevo_cupo = entrada_cupo.get()
        nuevo_periodo = entrada_periodo.get()
        nuevo_anio = entrada_anio.get()
        nuevos_inscritos = entrada_inscritos.get()
        nuevo_horario = entrada_horario.get()
        nuevo_estado = estado_combo.get()

        # Validar que todos los campos estén llenos
        if "" in [nombre_maestro_seleccionado, nombre_materia_seleccionado, nuevo_cupo, nuevo_periodo, nuevo_anio, nuevos_inscritos, nuevo_horario, nuevo_estado]:
            estado_label.configure(text="Todos los campos deben llenarse", text_color="red")
            return

        # Buscar el ID del maestro por nombre
        nuevo_id_maestro = obtener_id_maestro_por_nombre(nombre_maestro_seleccionado)
        
        if nuevo_id_maestro is None:
            estado_label.configure(text="Error: Maestro no encontrado", text_color="red")
            return

        # Buscar el ID de la materia por nombre
        nuevo_id_materia = obtener_id_materia_por_nombre(nombre_materia_seleccionado)
        
        if nuevo_id_materia is None:
            estado_label.configure(text="Error: Materia no encontrada", text_color="red")
            return

        try:
            sql = """
            UPDATE grupo 
            SET id_maestro=%s, id_materia=%s, cupo_maximo=%s, periodo=%s, years=%s, alumnos_inscritos=%s, horario=%s, estado=%s
            WHERE id_grupo=%s
            """
            valores = (nuevo_id_maestro, nuevo_id_materia, nuevo_cupo, nuevo_periodo, nuevo_anio, nuevos_inscritos, nuevo_horario, nuevo_estado, id_grupo)
            ejecutar_update(sql, valores)
            
            # Recarga la tabla inmediatamente después de actualizar
            if volver_a_lista:
                try:
                    volver_a_lista()
                except:
                    pass

        except Exception as e:
            estado_label.configure(text=f"Error al actualizar: {str(e)}", text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido, fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(
        botones,
        text="Actualizar",
        command=actualizar,
        fg_color="#007b3a"
    ).grid(row=0, column=0, padx=10)

    customtkinter.CTkButton(
        botones,
        text="Cancelar",
        command=lambda: volver_a_lista() if volver_a_lista else None,
        fg_color="#962d22"
    ).grid(row=0, column=1, padx=10)
