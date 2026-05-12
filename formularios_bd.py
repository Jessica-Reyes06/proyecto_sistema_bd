# Tabla editable genérica con doble clic y edición
def crear_tabla_editable_con_doble_click(parent, headers, registros, tipo_tabla, campos_sql, campo_id, volver_a_lista=None):

    from customtkinter import CTkFrame, CTkLabel, CTkScrollableFrame, CTkEntry, CTkButton
    from config_principal import limpiar_frame
    from db_conexion import ejecutar_update

    tabla = CTkFrame(parent)
    tabla.pack(fill="both", expand=True)

    encabezado = CTkFrame(tabla, fg_color="#e0e0e0")
    encabezado.pack(fill="x")

    for i, h in enumerate(headers):
        encabezado.grid_columnconfigure(i, weight=1)

        CTkLabel(
            encabezado,
            text=h,
            text_color="black",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).grid(row=0, column=i, padx=10, pady=10, sticky="w")

    cuerpo = CTkScrollableFrame(tabla, fg_color="#ffffff")
    cuerpo.pack(fill="both", expand=True)

    # ---------- FORMULARIO DE EDICIÓN ----------
    def abrir_form_edicion(parent_frame, valores):

        limpiar_frame(parent_frame)

        entradas = {}

        frame_form = CTkFrame(parent_frame)
        frame_form.pack(padx=20, pady=20)

        for i, campo in enumerate(headers):

            CTkLabel(
                frame_form,
                text=campo,
                font=("Arial", 13)
            ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

            entrada = CTkEntry(frame_form, width=260)
            entrada.grid(row=i, column=1, padx=10, pady=5, sticky="w")

            entrada.insert(0, str(valores[i]))

            entradas[campo] = entrada

        estado_label = CTkLabel(parent_frame, text="")
        estado_label.pack()

        # ---------- GUARDAR ----------
        def guardar():

            nuevos = [entradas[c].get() for c in headers]

            set_sql = ", ".join(
                [f"{campo}=%s" for campo in campos_sql if campo != campo_id]
            )
            sql = f"UPDATE {tipo_tabla} SET {set_sql} WHERE {campo_id}=%s"

            try:

                ejecutar_update(
                    sql,
                    tuple(nuevos[1:]) + (valores[0],)
                )

                estado_label.configure(
                    text="Registro actualizado",
                    text_color="green"
                )

                if volver_a_lista:
                    volver_a_lista()

            except Exception as e:

                estado_label.configure(
                    text=str(e),
                    text_color="red"
                )

        CTkButton(
            parent_frame,
            text="Guardar",
            command=guardar
        ).pack(pady=10)

        CTkButton(
            parent_frame,
            text="Cancelar",
            command=lambda: volver_a_lista() if volver_a_lista else None
        ).pack(pady=5)

    # ---------- TABLA ----------
    for fila_idx, fila in enumerate(registros):

        for col_idx, valor in enumerate(fila):

            cuerpo.grid_columnconfigure(col_idx, weight=1)

            label = CTkLabel(
                cuerpo,
                text=str(valor),
                font=("Arial", 13),
                anchor="w",
                text_color="#000000"
            )

            label.grid(
                row=fila_idx,
                column=col_idx,
                padx=10,
                pady=6,
                sticky="ew"
            )

            label.bind(
                "<Double-Button-1>",
                lambda event, idx=fila_idx:
                abrir_form_edicion(parent, registros[idx])
            )

    return tabla 
import random, datetime, csv, customtkinter
from config_principal import limpiar_frame
from db_conexion import ejecutar_insert, ejecutar_select, conexion

# OBTENER VALORES DE UNA TABLA
def obtener_lista(tabla, campo):
    try:
        registros = ejecutar_select(f"SELECT {campo} FROM {tabla}")
        lista = [str(r[0]) for r in registros]
        if not lista:
            lista = ["No hay datos"]
        return lista
    except Exception as e:
        print("Error obteniendo lista:", e)
        return ["Error"]

# -------------------------------

CARRERAS_ITVER = [
    "Ingeniería en Sistemas Computacionales",
    "Ingeniería Industrial",
    "Ingeniería Electromecánica",
    "Ingeniería Eléctrica",
    "Ingeniería Electrónica",
    "Ingeniería Civil",
    "Ingeniería Química",
    "Ingeniería Bioquímica",
    "Ingeniería en Gestión Empresarial",
    "Licenciatura en Administración",
]

SEMESTRES_ITVER = [str(i) for i in range(1,13)]
ESTADOS_ALUMNO = ["Activo","Baja temporal","Baja definitiva","Egresado", "Reingreso" ]

def formatear_etiqueta_campo(texto):
    texto = texto.replace("_", " ").strip()
    return texto[:1].upper() + texto[1:] if texto else texto

def generar_numero_control_unico():
    year = datetime.date.today().year % 100
    prefijo = f"A{year:02d}"

    while True:
        sufijo = "".join(str(random.randint(0,9)) for _ in range(5))
        numero = prefijo + sufijo

        existe = ejecutar_select(
            "SELECT numero_control FROM alumno WHERE numero_control=%s",
            (numero,)
        )

        if not existe:
            return numero


def generar_matricula_maestro_unica():
    year = datetime.date.today().year % 100
    prefijo = f"M{year:02d}"

    while True:
        sufijo = "".join(str(random.randint(0,9)) for _ in range(5))
        matricula = prefijo + sufijo

        existe = ejecutar_select(
            "SELECT matricula FROM maestro WHERE matricula=%s",
            (matricula,)
        )

        if not existe:
            return matricula


def generar_matricula_administrador_unica():
    year = datetime.date.today().year % 100
    prefijo = f"ADM{year:02d}"

    while True:
        sufijo = "".join(str(random.randint(0,9)) for _ in range(5))
        matricula = prefijo + sufijo

        existe = ejecutar_select(
            "SELECT matricula FROM administrador WHERE matricula=%s",
            (matricula,)
        )

        if not existe:
            return matricula

# CAMPOS

def crear_campo(frame,fila,texto):
    label = customtkinter.CTkLabel(frame,text=formatear_etiqueta_campo(texto),font=("Arial",14))
    label.grid(row=fila,column=0,padx=10,pady=5,sticky="w")

    entry = customtkinter.CTkEntry(frame,width=260)
    entry.grid(row=fila,column=1,padx=10,pady=5,sticky="w")

    return entry


def crear_combo(frame,fila,texto,opciones):

    label = customtkinter.CTkLabel(frame,text=formatear_etiqueta_campo(texto),font=("Arial",14))
    label.grid(row=fila,column=0,padx=10,pady=5,sticky="w")

    combo = customtkinter.CTkComboBox(
        frame,
        values=opciones,
        width=260,
        state="readonly"
    )

    combo.set(opciones[0])
    combo.grid(row=fila,column=1,padx=10,pady=5,sticky="w")

    return combo

# FORMULARIO GENERICO

def crear_formulario_generico(frame_contenido,titulo,campos,sql_insert,volver_a_lista=None):

    limpiar_frame(frame_contenido)

    titulo_label = customtkinter.CTkLabel(
        frame_contenido,
        text=titulo,
        font=("Arial",22,"bold")
    )
    titulo_label.pack(pady=(10,20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20,pady=10,fill="x")


    entradas = {}
    for i, campo in enumerate(campos):
        campo_normalizado = campo.strip().lower()
        # Si el campo es 'estatus' y es para maestro, usar combo
        if campo_normalizado == "estatus" and "maestro" in titulo.lower():
            opciones_estatus = ["Activo", "Inactivo", "Licencia", "Jubilado"]
            entradas[campo] = crear_combo(cuerpo, i, campo, opciones_estatus)

        elif campo_normalizado in ("tipo", "tipo de carrera") and "carrera" in titulo.lower():
            opciones_tipo_carrera = ["Ingeniería", "Licenciatura"]
            entradas[campo] = crear_combo(cuerpo, i, "Tipo de carrera", opciones_tipo_carrera)

        elif campo_normalizado == "estatus" and "grupo" in titulo.lower():
            opciones_estatus = ["Activo","Cerrado","Cancelado"]
            entradas[campo] = crear_combo(cuerpo, i, campo, opciones_estatus)

        else:
            entradas[campo] = crear_campo(cuerpo, i, campo)

    estado_label = customtkinter.CTkLabel(frame_contenido,text="")
    estado_label.pack()

    def guardar():

        valores = [entradas[c].get() for c in campos]

        if "" in valores:
            estado_label.configure(text="Todos los campos deben llenarse",text_color="red")
            return

        try:
            ejecutar_insert(sql_insert,tuple(valores))
            estado_label.configure(text="Registro guardado correctamente",text_color="green")

            if volver_a_lista:
                volver_a_lista()

        except Exception as e:
            estado_label.configure(text=str(e),text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido,fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(
        botones,
        text="Guardar",
        command=guardar
    ).grid(row=0,column=0,padx=10)

    customtkinter.CTkButton(
        botones,
        text="Cancelar",
        command=lambda: volver_a_lista() if volver_a_lista else None
    ).grid(row=0,column=1,padx=10)

# FORMULARIO ALUMNOS

def mostrar_form_registro_alumno(frame_contenido,volver_a_lista=None):

    limpiar_frame(frame_contenido)

    titulo = customtkinter.CTkLabel(frame_contenido,text="Registrar alumno",font=("Arial",22,"bold"))
    titulo.pack(pady=(10,20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20,pady=10,fill="x")

    entradas = {}

    entradas["numero_control"] = crear_campo(cuerpo,0,"Número de control")
    entradas["Nombre"] = crear_campo(cuerpo,1,"Nombre")
    entradas["ApellidoPaterno"] = crear_campo(cuerpo,2,"Apellido paterno")
    entradas["ApellidoMaterno"] = crear_campo(cuerpo,3,"Apellido materno")
    entradas["correo_alumno"] = crear_campo(cuerpo,4,"Correo")
    entradas["Carrera"] = crear_combo(cuerpo,5,"Carrera",CARRERAS_ITVER)
    entradas["Semestre"] = crear_combo(cuerpo,6,"Semestre",SEMESTRES_ITVER)
    entradas["Estado"] = crear_combo(cuerpo,7,"Estado",ESTADOS_ALUMNO)

    entradas["numero_control"].configure(state="readonly")
    entradas["correo_alumno"].configure(state="readonly")

    estado_label = customtkinter.CTkLabel(frame_contenido,text="")
    estado_label.pack()

    valores_generados = {"numero":"","correo":""}

    def escribir_en_entrada(entrada, valor):
        entrada.configure(state="normal")
        entrada.delete(0, "end")
        entrada.insert(0, valor)
        entrada.configure(state="readonly")

    def generar():

        try:
            numero = generar_numero_control_unico()
        except Exception:
            numero = f"L{datetime.date.today().year % 100:02d}{random.randint(0, 99999):05d}"

        correo = f"{numero}@veracruz.tecnm.mx"

        valores_generados["numero"]=numero
        valores_generados["correo"]=correo

        escribir_en_entrada(entradas["numero_control"], numero)
        escribir_en_entrada(entradas["correo_alumno"], correo)

    generar()

    def guardar():

        if valores_generados["numero"]=="":
            estado_label.configure(text="Primero genera número de control",text_color="red")
            return

        from funciones_datos import obtener_id_carrera_por_nombre

        id_carrera = obtener_id_carrera_por_nombre(entradas["Carrera"].get())
        if id_carrera is None:
            estado_label.configure(text="No se encontró la carrera seleccionada", text_color="red")
            return

        datos = (
            valores_generados["numero"],
            entradas["Nombre"].get(),
            entradas["ApellidoPaterno"].get(),
            entradas["ApellidoMaterno"].get(),
            valores_generados["correo"],
            id_carrera,
            entradas["Semestre"].get(),
            entradas["Estado"].get()
        )

        sql = """
        INSERT INTO alumno
        (numero_control,nombre_alumno,apellido_paterno,apellido_materno,
        correo_alumno,id_carrera,semestre,estatus_alumno)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        try:
            ejecutar_insert(sql,datos)
            estado_label.configure(text="Alumno guardado",text_color="green")
        except Exception as e:
            estado_label.configure(text=str(e), text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido,fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(botones,text="Guardar",command=guardar).grid(row=0,column=0,padx=10)
    customtkinter.CTkButton(botones,text="Cancelar",command=lambda: volver_a_lista() if volver_a_lista else None).grid(row=0,column=1,padx=10)

# MAESTROS
def mostrar_form_registro_maestro(frame_contenido,volver_a_lista=None):
    limpiar_frame(frame_contenido)

    titulo = customtkinter.CTkLabel(frame_contenido,text="Registrar maestro",font=("Arial",22,"bold"))
    titulo.pack(pady=(10,20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20,pady=10,fill="x")

    entradas = {}

    entradas["matricula_maestro"] = crear_campo(cuerpo,0,"Matricula")
    entradas["nombre_maestro"] = crear_campo(cuerpo,1,"Nombre")
    entradas["apellido_paterno"] = crear_campo(cuerpo,2,"Apellido Paterno")
    entradas["apellido_materno"] = crear_campo(cuerpo,3,"Apellido Materno")
    entradas["correo"] = crear_campo(cuerpo,4,"Correo")
    entradas["estatus"] = crear_combo(cuerpo,5,"Estatus",["Activo", "Inactivo", "Licencia", "Jubilado"])
    entradas["perfil_docente"] = crear_campo(cuerpo,7,"Perfil del docente")
    
    entradas["cedula_profesional"] = crear_campo(cuerpo,10,"Cédula profesional")

    entradas["matricula_maestro"].configure(state="readonly")
    entradas["correo"].configure(state="readonly")

    estado_label = customtkinter.CTkLabel(frame_contenido,text="")
    estado_label.pack()

    valores_generados = {"matricula":"", "correo":""}

    def escribir_en_entrada(entrada, valor):
        entrada.configure(state="normal")
        entrada.delete(0, "end")
        entrada.insert(0, valor)
        entrada.configure(state="readonly")

    def generar_datos_maestro():
        matricula = generar_matricula_maestro_unica()
        correo = f"{matricula}@veracruz.tecnm.mx"

        valores_generados["matricula"] = matricula
        valores_generados["correo"] = correo

        escribir_en_entrada(entradas["matricula_maestro"], matricula)
        escribir_en_entrada(entradas["correo"], correo)

    generar_datos_maestro()

    def guardar():

        valores = (
            valores_generados["matricula"],
            entradas["nombre_maestro"].get(),
            entradas["apellido_paterno"].get(),
            entradas["apellido_materno"].get(),
            valores_generados["correo"],
            entradas["estatus"].get(),
            entradas["perfil_docente"].get(),
            entradas["cedula_profesional"].get()
        )
        

        if "" in valores:
            estado_label.configure(text="Todos los campos deben llenarse",text_color="red")
            return

        sql = """
        INSERT INTO maestro
        (matricula,nombre_maestro,apellido_paterno,apellido_materno,
        correo,estatus,perfil_docente,cedula_profesional)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        try:
            ejecutar_insert(sql,valores)
            estado_label.configure(text="Registro guardado correctamente",text_color="green")

            if volver_a_lista:
                volver_a_lista()

        except Exception as e:
            estado_label.configure(text=str(e),text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido,fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(botones,text="Guardar",command=guardar).grid(row=0,column=0,padx=10)
    customtkinter.CTkButton(botones,text="Cancelar",command=lambda: volver_a_lista() if volver_a_lista else None).grid(row=0,column=1,padx=10)


# ADMINISTRADORES
def mostrar_form_registro_administrador(frame_contenido, volver_a_lista=None):
    limpiar_frame(frame_contenido)

    titulo = customtkinter.CTkLabel(frame_contenido, text="Registrar administrador", font=("Arial", 22, "bold"))
    titulo.pack(pady=(10, 20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20, pady=10, fill="x")

    entradas = {}

    entradas["matricula"] = crear_campo(cuerpo, 0, "Matrícula")
    entradas["nombre"] = crear_campo(cuerpo, 1, "Nombre")
    entradas["apellido_paterno"] = crear_campo(cuerpo, 2, "Apellido paterno")
    entradas["apellido_materno"] = crear_campo(cuerpo, 3, "Apellido materno")

    entradas["matricula"].configure(state="readonly")

    estado_label = customtkinter.CTkLabel(frame_contenido, text="")
    estado_label.pack()

    valores_generados = {"matricula": ""}

    def escribir_en_entrada(entrada, valor):
        entrada.configure(state="normal")
        entrada.delete(0, "end")
        entrada.insert(0, valor)
        entrada.configure(state="readonly")

    def generar_matricula():
        try:
            matricula = generar_matricula_administrador_unica()
        except Exception as e:
            matricula = f"ADM{datetime.date.today().year % 100:02d}{random.randint(0, 99999):05d}"
            print(f"Error generando matrícula de administrador: {e}")

        valores_generados["matricula"] = matricula
        escribir_en_entrada(entradas["matricula"], matricula)

    generar_matricula()

    def guardar():

        valores = (
            valores_generados["matricula"],
            entradas["nombre"].get(),
            entradas["apellido_paterno"].get(),
            entradas["apellido_materno"].get(),
        )

        if "" in valores:
            estado_label.configure(text="Todos los campos deben llenarse", text_color="red")
            return

        sql = """
        INSERT INTO administrador
        (matricula,nombre,apellido_paterno,apellido_materno)
        VALUES (%s,%s,%s,%s)
        """

        try:
            ejecutar_insert(sql, valores)
            estado_label.configure(text="Registro guardado correctamente", text_color="green")

            if volver_a_lista:
                volver_a_lista()

        except Exception as e:
            estado_label.configure(text=str(e), text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido, fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(botones, text="Guardar", command=guardar).grid(row=0, column=0, padx=10)
    customtkinter.CTkButton(botones, text="Cancelar", command=lambda: volver_a_lista() if volver_a_lista else None).grid(row=0, column=1, padx=10)


# CARRERAS
def mostrar_form_registro_carrera(frame_contenido, volver_a_lista=None):

    # id_carrera se omite por ser AUTO_INCREMENT (AI)
    campos = [
        "Nombre de la Carrera",
        "Tipo de carrera",
        "Semestres",
        "Clave",
    ]

    sql = """
    INSERT INTO carreras
    (nombre_carrera,tipo_carrera,numero_semestres,clave_carrera)
    VALUES (%s,%s,%s,%s)
    """

    crear_formulario_generico(frame_contenido, "Registrar carrera", campos, sql, volver_a_lista)

# TIPOS DE ACTIVIDADES
def mostrar_form_registro_tipo_actividad(frame_contenido, volver_a_lista=None):

    # id_tipo se maneja como entero (AI PK) según especificación
    campos = [
        "nombre"
    ]

    sql = """
    INSERT INTO tipos_actividades
    (nombre)
    VALUES (%s)
    """

    crear_formulario_generico(frame_contenido, "Registrar tipo de actividad", campos, sql, volver_a_lista)

#  ACTIVIDADES
def mostrar_form_actividad(frame_contenido, volver_a_lista=None):

    limpiar_frame(frame_contenido)

    titulo = customtkinter.CTkLabel(
        frame_contenido,
        text="Registrar Actividad",
        font=("Arial", 22, "bold")
    )
    titulo.pack(pady=(10, 20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20, pady=10, fill="x")

    # Materia
    materias = obtener_lista("materia", "nombre_materia")
    combo_materia = crear_combo(cuerpo, 0, "Materia", materias)

    # Grupo dinámico
    combo_grupo = crear_combo(cuerpo, 1, "Grupo", ["Selecciona materia"])

    # Unidad dinámica (combo)
    label_unidad = customtkinter.CTkLabel(cuerpo, text=formatear_etiqueta_campo("Unidad"), font=("Arial", 14))
    label_unidad.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    combo_unidad = customtkinter.CTkComboBox(cuerpo, width=260, values=["Selecciona materia"], state="readonly")
    combo_unidad.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    combo_unidad._unidad_map = {}

    # Tipo de actividad
    tipos_actividades = obtener_lista("tipos_actividades", "nombre")
    combo_tipo_actividad = crear_combo(cuerpo, 3, "Tipo de actividad", tipos_actividades)

    # Detalles
    detalles_field = crear_campo(cuerpo, 4, "Detalles")

    estado_label = customtkinter.CTkLabel(frame_contenido, text="")
    estado_label.pack()

    def actualizar_grupo_y_unidad(materia_nombre):
        # Grupos
        try:
            grupos_result = ejecutar_select(
                "SELECT clave_grupo FROM grupo WHERE id_materia = (SELECT id_materia FROM materia WHERE nombre_materia = %s)",
                (materia_nombre,)
            )
            grupos = [str(g[0]) for g in grupos_result] if grupos_result else ["No hay grupos"]
            combo_grupo.configure(values=grupos)
            combo_grupo.set(grupos[0])
        except Exception as e:
            print(f"Error obteniendo grupos: {e}")

        # Unidades
        try:
            unidades_result = ejecutar_select(
                "SELECT id_unidad, numero_unidad, tema_unidad FROM unidad WHERE id_materia = (SELECT id_materia FROM materia WHERE nombre_materia = %s) ORDER BY numero_unidad",
                (materia_nombre,)
            )
            if unidades_result:
                combo_unidad._unidad_map = {f"Unidad {u[1]} - {u[2]}": u[0] for u in unidades_result}
                combo_unidad.configure(values=list(combo_unidad._unidad_map.keys()))
                combo_unidad.set(list(combo_unidad._unidad_map.keys())[0])
            else:
                combo_unidad._unidad_map = {}
                combo_unidad.configure(values=["No hay unidades"])
                combo_unidad.set("No hay unidades")
        except Exception as e:
            print(f"Error obteniendo unidades: {e}")

    def on_materia_change(event=None):
        actualizar_grupo_y_unidad(combo_materia.get())

    combo_materia.bind("<<ComboboxChanged>>", on_materia_change)

    if materias and materias[0] != "No hay datos":
        actualizar_grupo_y_unidad(materias[0])

    def guardar():
        tipo_nombre   = combo_tipo_actividad.get()
        unidad_texto  = combo_unidad.get()
        detalles      = detalles_field.get()

        if not all([tipo_nombre, unidad_texto, detalles]) or "No hay" in unidad_texto:
            estado_label.configure(text="Todos los campos deben llenarse correctamente", text_color="red")
            return

        tipo_result = ejecutar_select(
            "SELECT id_tipo FROM tipos_actividades WHERE nombre = %s", (tipo_nombre,)
        )
        id_unidad = combo_unidad._unidad_map.get(unidad_texto)

        if not tipo_result or not id_unidad:
            estado_label.configure(text="Error obteniendo datos, intenta de nuevo", text_color="red")
            return

        id_tipo = tipo_result[0][0]

        sql = """
        INSERT INTO actividad (id_tipo, id_unidad, ponderacion, detalles)
        VALUES (%s, %s, NULL, %s)
        """
        try:
            ejecutar_insert(sql, (id_tipo, id_unidad, detalles))
            estado_label.configure(text="Actividad registrada correctamente", text_color="green")
            if volver_a_lista:
                volver_a_lista()
        except Exception as e:
            estado_label.configure(text=str(e), text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido, fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(botones, text="Guardar", command=guardar).grid(row=0, column=0, padx=10)
    customtkinter.CTkButton(botones, text="Cancelar", command=lambda: volver_a_lista() if volver_a_lista else None).grid(row=0, column=1, padx=10)
# MATERIAS

def mostrar_form_registro_materia(frame_contenido, volver_a_lista=None):
    from db_conexion import ejecutar_select
    from funciones_datos import obtener_id_carrera_por_nombre
    
    limpiar_frame(frame_contenido)

    titulo = customtkinter.CTkLabel(
        frame_contenido,
        text="Registrar Materia",
        font=("Arial", 22, "bold")
    )
    titulo.pack(pady=(10, 20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20, pady=10, fill="x")

    entradas = {}

    # Campo Clave
    entradas["Clave"] = crear_campo(cuerpo, 0, "Clave")
    
    # Campo Nombre Materia
    entradas["Nombre Materia"] = crear_campo(cuerpo, 1, "Nombre de la Materia")
    
    # Combo de Carreras - Obtener nombres de carreras directamente
    try:
        resultado = ejecutar_select("SELECT nombre_carrera FROM carreras ORDER BY nombre_carrera ASC")
        carreras_lista = [row[0] for row in resultado] if resultado else ["No hay carreras"]
    except Exception as e:
        print(f"Error cargando carreras: {e}")
        carreras_lista = ["Error al cargar carreras"]
    
    entradas["Carrera"] = crear_combo(cuerpo, 2, "Carrera", carreras_lista)
    
    # Campo Horas a la semana
    entradas["Horas"] = crear_campo(cuerpo, 3, "Horas a la semana")
    
    # Campo Unidades

    estado_label = customtkinter.CTkLabel(frame_contenido, text="")
    estado_label.pack()

    def guardar():
        # Obtener valores
        clave = entradas["Clave"].get()
        nombre_materia = entradas["Nombre Materia"].get()
        nombre_carrera = entradas["Carrera"].get()
        horas_semana = entradas["Horas"].get()

        # Validar campos vacíos
        if "" in [clave, nombre_materia, nombre_carrera, horas_semana]:
            estado_label.configure(text="Todos los campos deben llenarse", text_color="red")
            return

        # Buscar el ID de la carrera por nombre
        id_carrera = obtener_id_carrera_por_nombre(nombre_carrera)
        
        if id_carrera is None:
            estado_label.configure(text="No se pudo completar el registro: Carrera no encontrada", text_color="red")
            return

        try:
            sql = """
            INSERT INTO materia
            (clave, nombre_materia, horas_semana, id_carrera)
            VALUES (%s, %s, %s, %s)
            """
            valores = (clave, nombre_materia, horas_semana, id_carrera)
            ejecutar_insert(sql, valores)
            
            estado_label.configure(text="Materia registrada correctamente", text_color="green")

            if volver_a_lista:
                volver_a_lista()

        except Exception as e:
            estado_label.configure(text=f"Error al guardar: {str(e)}", text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido, fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(botones, text="Guardar", command=guardar).grid(row=0, column=0, padx=10)
    customtkinter.CTkButton(botones, text="Cancelar", command=lambda: volver_a_lista() if volver_a_lista else None).grid(row=0, column=1, padx=10)

# GRUPOS

def mostrar_form_registro_grupo(frame_contenido,volver_a_lista=None):

    limpiar_frame(frame_contenido)

    titulo = customtkinter.CTkLabel(
        frame_contenido,
        text="Crear grupo",
        font=("Arial",22,"bold")
    )
    titulo.pack(pady=(10,20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20,pady=10,fill="x")

    # Obtener maestros directamente
    try:
        maestros_result = ejecutar_select("SELECT nombre_maestro FROM maestro ORDER BY nombre_maestro ASC")
        maestros = [str(m[0]) for m in maestros_result] if maestros_result else ["No hay maestros"]
    except Exception as e:
        print(f"Error obteniendo maestros: {e}")
        maestros = ["Error cargando maestros"]
    
    # Obtener materias directamente
    try:
        materias_result = ejecutar_select("SELECT nombre_materia FROM materia ORDER BY nombre_materia ASC")
        materias = [str(mat[0]) for mat in materias_result] if materias_result else ["No hay materias"]
    except Exception as e:
        print(f"Error obteniendo materias: {e}")
        materias = ["Error cargando materias"]

    combo_maestro = crear_combo(cuerpo, 0, "Maestro", maestros)
    combo_materia = crear_combo(cuerpo, 1, "Materia", materias)

    clave_grupo = crear_campo(cuerpo, 2, "Clave Grupo")
    cupo = crear_campo(cuerpo, 3, "Cupo máximo")

    periodos = ["Enero-Junio", "Agosto-Diciembre", "Verano"]
    entrada_periodo = crear_combo(cuerpo, 4, "Periodo", periodos)

    # Año: lista desplegable pequeña desde año actual hasta 1990
    label_anio = customtkinter.CTkLabel(cuerpo, text=formatear_etiqueta_campo("Año"), font=("Arial",14))
    label_anio.grid(row=5, column=0, padx=10, pady=5, sticky="w")
    anos = [str(y) for y in range(datetime.date.today().year, 1989, -1)]
    entrada_anio = customtkinter.CTkComboBox(cuerpo, values=anos, width=120, state="readonly")
    entrada_anio.set(anos[0])
    entrada_anio.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    combo_estado = crear_combo(
        cuerpo,
        8,
        "Estado",
        ["Activo", "Cerrado", "Cancelado"]
    )

    estado_label = customtkinter.CTkLabel(frame_contenido,text="")
    estado_label.pack()

    def guardar():
        from funciones_datos import obtener_id_maestro_por_nombre, obtener_id_materia_por_nombre

        nombre_maestro = combo_maestro.get()
        nombre_materia = combo_materia.get()

        # Obtener id del maestro por nombre
        id_maestro = obtener_id_maestro_por_nombre(nombre_maestro)
        if not id_maestro:
            estado_label.configure(
                text="No se pudo completar el registro: Maestro no encontrado",
                text_color="red"
            )
            return

        # VALIDAR ESTADO DEL MAESTRO
        estado_maestro = ejecutar_select(
            "SELECT estatus FROM maestro WHERE id_maestro=%s",
            (id_maestro,)
        )

        if not estado_maestro:
            estado_label.configure(
                text="El maestro no existe",
                text_color="red"
            )
            return

        if estado_maestro[0][0] != "Activo":
            estado_label.configure(
                text="No se puede asignar grupo a un maestro que no esté activo",
                text_color="red"
            )
            return

        # Obtener id_materia por nombre de materia
        id_materia = obtener_id_materia_por_nombre(nombre_materia)
        if not id_materia:
            estado_label.configure(
                text="No se pudo completar el registro: Materia no encontrada",
                text_color="red"
            )
            return

        valores = (
            clave_grupo.get(),
            id_maestro,
            id_materia,
            cupo.get(),
            entrada_periodo.get(),
            entrada_anio.get(),
            combo_estado.get()
        )

        sql = """
        INSERT INTO grupo
        (clave_grupo,id_maestro,id_materia,cupo_maximo,periodo,years,estado)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """

        try:
            ejecutar_insert(sql,valores)

            estado_label.configure(
                text="Grupo creado correctamente",
                text_color="green"
            )

            if volver_a_lista:
                volver_a_lista()

        except Exception as e:
            estado_label.configure(
                text=str(e),
                text_color="red"
            )

    botones = customtkinter.CTkFrame(frame_contenido,fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(
        botones,
        text="Guardar",
        command=guardar
    ).grid(row=0,column=0,padx=10)

    customtkinter.CTkButton(
        botones,
        text="Cancelar",
        command=lambda: volver_a_lista() if volver_a_lista else None
    ).grid(row=0,column=1,padx=10)
# INSCRIPCIONES

def mostrar_form_registro_inscripcion(frame_contenido, volver_a_lista=None):

    limpiar_frame(frame_contenido)

    titulo = customtkinter.CTkLabel(
        frame_contenido,
        text="Registrar inscripción",
        font=("Arial",22,"bold")
    )
    titulo.pack(pady=(10,20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20,pady=10,fill="x")

    alumnos = obtener_lista("alumno", "numero_control")
    grupos = obtener_lista("grupo", "clave_grupo")

    combo_alumno = crear_combo(cuerpo, 0, "Número de control", alumnos)
    combo_grupo = crear_combo(cuerpo, 1, "Clave grupo", grupos)
    combo_estatus = crear_combo(cuerpo, 2, "Estatus materia", ["Cursando", "Baja", "Concluido"])
    tipo_registro = crear_campo(cuerpo, 3, "Tipo registro")

    estado_label = customtkinter.CTkLabel(frame_contenido,text="")
    estado_label.pack()

    def guardar():

        numero_control = combo_alumno.get().strip()
        clave_grupo = combo_grupo.get().strip()

        alumno_info = ejecutar_select(
            "SELECT id_alumno, estatus_alumno FROM alumno WHERE numero_control=%s",
            (numero_control,)
        )

        if not alumno_info:
            estado_label.configure(
                text="No se encontró el alumno seleccionado",
                text_color="red"
            )
            return

        id_alumno = alumno_info[0][0]
        estatus_alumno = alumno_info[0][1]

        # VALIDAR ESTADO ALUMNO
        if estatus_alumno != "Activo":

            estado_label.configure(
                text="Solo alumnos activos pueden inscribirse",
                text_color="red"
            )
            return

        # VALIDAR ESTADO GRUPO
        grupo_info = ejecutar_select(
            "SELECT id_grupo, estatus FROM grupo WHERE clave_grupo=%s OR CAST(id_grupo AS TEXT)=%s LIMIT 1",
            (clave_grupo, clave_grupo)
        )

        if not grupo_info:
            estado_label.configure(
                text="No se encontró el grupo seleccionado",
                text_color="red"
            )
            return

        id_grupo = grupo_info[0][0]
        estado_grupo = grupo_info

        if estado_grupo and estado_grupo[0][0] in ["Cerrado","Cancelado"]:

            estado_label.configure(
                text="No se pueden inscribir alumnos en este grupo",
                text_color="red"
            )
            return

        valores = (
            id_alumno,
            id_grupo,
            combo_estatus.get(),
            tipo_registro.get()
        )

        sql = """
        INSERT INTO registro
        (id_alumno,id_grupo,estatus_materia,tipo_registro)
        VALUES (%s,%s,%s,%s)
        """

        try:

            ejecutar_insert(sql,valores)

            estado_label.configure(
                text="Inscripción guardada",
                text_color="green"
            )

            if volver_a_lista:
                volver_a_lista()

        except Exception as e:

            estado_label.configure(
                text=str(e),
                text_color="red"
            )

    botones = customtkinter.CTkFrame(frame_contenido,fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(botones,text="Guardar",command=guardar).grid(row=0,column=0,padx=10)
    customtkinter.CTkButton(botones,text="Cancelar",command=lambda: volver_a_lista() if volver_a_lista else None).grid(row=0,column=1,padx=10)

# USUARIOS
def importar_csv(tabla, ruta_csv):

        with open(ruta_csv, newline="", encoding="utf-8") as archivo:

            lector = csv.reader(archivo)
            encabezados = next(lector)

            placeholders = ",".join(["%s"] * len(encabezados))
            columnas = ",".join(encabezados)

            sql = f"INSERT IGNORE INTO {tabla} ({columnas}) VALUES ({placeholders})"

            cursor = conexion.cursor()

            for fila in lector:
                cursor.execute(sql, fila)

            conexion.commit()
            cursor.close()
    
def exportar_csv(tabla, ruta_destino):

    cursor = conexion.cursor()

    cursor.execute(f"SELECT * FROM {tabla}")

    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]

    with open(ruta_destino, "w", newline="", encoding="utf-8") as archivo:

        escritor = csv.writer(archivo)

        escritor.writerow(columnas)

        for fila in filas:
            escritor.writerow(fila)

    cursor.close()

def mostrar_form_registro_calificacion_final(frame_contenido, volver_a_lista=None):
    """Formulario para registrar calificación final"""
    limpiar_frame(frame_contenido)

    titulo = customtkinter.CTkLabel(
        frame_contenido,
        text="Registrar Calificación Final",
        font=("Arial", 22, "bold")
    )
    titulo.pack(pady=(10, 20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20, pady=10, fill="x")

    # COMBOS PARA ALUMNO Y GRUPO
    alumnos = obtener_lista("Alumno", "numero_control")
    grupos = obtener_lista("Grupo", "clave_grupo")

    combo_alumno = crear_combo(cuerpo, 0, "Alumno", alumnos)
    combo_grupo = crear_combo(cuerpo, 1, "Grupo", grupos)
    entrada_calif = crear_campo(cuerpo, 2, "Calificación Final (0-100)")
    entrada_periodo = crear_campo(cuerpo, 3, "Periodo (ej: Enero-Junio 2024)")

    estado_label = customtkinter.CTkLabel(frame_contenido, text="")
    estado_label.pack()

    def guardar():
        alumno = combo_alumno.get()
        grupo = combo_grupo.get()
        calif = entrada_calif.get()

        # VALIDAR CALIFICACIÓN
        try:
            calif_float = float(calif)
            if calif_float < 0 or calif_float > 100:
                estado_label.configure(
                    text="La calificación debe estar entre 0 y 100",
                    text_color="red"
                )
                return
        except ValueError:
            estado_label.configure(text="Ingrese una calificación válida", text_color="red")
            return

        valores = (alumno, grupo, calif, entrada_periodo.get())

        sql = """
        INSERT INTO calificaciones_finales
        (numero_control, id_grupo, calificacion_final, periodo)
        VALUES (%s, %s, %s, %s)
        """

        try:
            ejecutar_insert(sql, valores)
            estado_label.configure(text="Calificación registrada", text_color="green")
            if volver_a_lista:
                volver_a_lista()
        except Exception as e:
            estado_label.configure(text=str(e), text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido, fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(botones, text="Guardar", command=guardar).grid(row=0, column=0, padx=10)
    customtkinter.CTkButton(botones, text="Cancelar",
                           command=lambda: volver_a_lista() if volver_a_lista else None
                           ).grid(row=0, column=1, padx=10)


def mostrar_form_registro_calificacion_actividad(frame_contenido, volver_a_lista=None):
    """Formulario para registrar calificación de actividad"""
    limpiar_frame(frame_contenido)

    titulo = customtkinter.CTkLabel(
        frame_contenido,
        text="Registrar Calificación de Actividad",
        font=("Arial", 22, "bold")
    )
    titulo.pack(pady=(10, 20))

    cuerpo = customtkinter.CTkFrame(frame_contenido)
    cuerpo.pack(padx=20, pady=10, fill="x")

    # COMBOS PARA ALUMNO Y ACTIVIDAD
    alumnos = obtener_lista("Alumno", "numero_control")
    actividades = obtener_lista("Tipos_actividades", "nombre")

    combo_alumno = crear_combo(cuerpo, 0, "Alumno", alumnos)
    combo_actividad = crear_combo(cuerpo, 1, "Actividad", actividades)
    entrada_calif = crear_campo(cuerpo, 2, "Calificación (0-100)")

    # Fecha actual por defecto
    import datetime
    fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
    entrada_fecha = crear_campo(cuerpo, 3, "Fecha (YYYY-MM-DD)")

    entrada_observaciones = customtkinter.CTkEntry(cuerpo, width=260, placeholder_text="Observaciones (opcional)")
    entrada_observaciones.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    customtkinter.CTkLabel(cuerpo, text="Observaciones", font=("Arial", 14)
                          ).grid(row=4, column=0, padx=10, pady=5, sticky="w")

    estado_label = customtkinter.CTkLabel(frame_contenido, text="")
    estado_label.pack()

    def guardar():
        alumno = combo_alumno.get()
        actividad = combo_actividad.get()
        calif = entrada_calif.get()

        # VALIDAR CALIFICACIÓN
        try:
            calif_float = float(calif)
            if calif_float < 0 or calif_float > 100:
                estado_label.configure(
                    text="La calificación debe estar entre 0 y 100",
                    text_color="red"
                )
                return
        except ValueError:
            estado_label.configure(text="Ingrese una calificación válida", text_color="red")
            return

        valores = (
            alumno,
            actividad,
            calif,
            entrada_fecha.get() or fecha_actual,
            entrada_observaciones.get() or ""
        )

        sql = """
        INSERT INTO calificaciones_actividades
        (numero_control, id_actividad, calificacion, fecha_registro, observaciones)
        VALUES (%s, %s, %s, %s, %s)
        """

        try:
            ejecutar_insert(sql, valores)
            estado_label.configure(text="Calificación registrada", text_color="green")
            if volver_a_lista:
                volver_a_lista()
        except Exception as e:
            estado_label.configure(text=str(e), text_color="red")

    botones = customtkinter.CTkFrame(frame_contenido, fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(botones, text="Guardar", command=guardar).grid(row=0, column=0, padx=10)
    customtkinter.CTkButton(botones, text="Cancelar",
                           command=lambda: volver_a_lista() if volver_a_lista else None
                           ).grid(row=0, column=1, padx=10)


def mostrar_form_registro_salon(frame_contenido, volver_a_lista=None):
    """Formulario para registrar un nuevo salón"""
    campos = ["id_salon", "nombre_salon", "capacidad", "tipo", "edificio", "piso", "estatus"]

    sql = """
    INSERT INTO salones
    (id_salon, nombre_salon, capacidad, tipo, edificio, piso, estatus)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    crear_formulario_generico(frame_contenido, "Registrar Salón", campos, sql, volver_a_lista)
