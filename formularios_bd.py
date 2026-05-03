# Tabla editable genérica con doble clic y edición
def crear_tabla_editable_con_doble_click(parent, headers, registros, tipo_tabla, campos_sql, campo_id, volver_a_lista=None):

    from customtkinter import CTkFrame, CTkLabel, CTkScrollableFrame, CTkEntry, CTkButton
    from config_principal import limpiar_frame
    from db_conexion import ejecutar_insert

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

                ejecutar_insert(
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
ESTADOS_ALUMNO = ["Activo","Baja temporal","Baja definitiva","Egresado"]


def generar_numero_control_unico():
    year = datetime.date.today().year % 100
    prefijo = f"A{year:02d}"

    while True:
        sufijo = "".join(str(random.randint(0,9)) for _ in range(5))
        numero = prefijo + sufijo

        existe = ejecutar_select(
            "SELECT numero_control FROM alumnos WHERE numero_control=%s",
            (numero,)
        )

        if not existe:
            return numero

# CAMPOS

def crear_campo(frame,fila,texto):
    label = customtkinter.CTkLabel(frame,text=texto,font=("Arial",14))
    label.grid(row=fila,column=0,padx=10,pady=5,sticky="w")

    entry = customtkinter.CTkEntry(frame,width=260)
    entry.grid(row=fila,column=1,padx=10,pady=5,sticky="w")

    return entry


def crear_combo(frame,fila,texto,opciones):

    label = customtkinter.CTkLabel(frame,text=texto,font=("Arial",14))
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
        # Si el campo es 'estatus' y es para maestro, usar combo
        if campo == "estatus" and "maestro" in titulo.lower():
            opciones_estatus = ["Activo", "Inactivo", "Licencia", "Jubilado"]
            entradas[campo] = crear_combo(cuerpo, i, campo, opciones_estatus)

        elif campo == "estatus" and "grupo" in titulo.lower():
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

    entradas["Nombre"] = crear_campo(cuerpo,0,"Nombre")
    entradas["ApellidoPaterno"] = crear_campo(cuerpo,1,"Apellido paterno")
    entradas["ApellidoMaterno"] = crear_campo(cuerpo,2,"Apellido materno")

    entradas["Carrera"] = crear_combo(cuerpo,3,"Carrera",CARRERAS_ITVER)
    entradas["Semestre"] = crear_combo(cuerpo,4,"Semestre",SEMESTRES_ITVER)
    entradas["Estado"] = crear_combo(cuerpo,5,"Estado",ESTADOS_ALUMNO)

    estado_label = customtkinter.CTkLabel(frame_contenido,text="")
    estado_label.pack()

    valores_generados = {"numero":"","correo":""}

    def generar():

        numero = generar_numero_control_unico()
        correo = f"{numero}@tecnm.mx"

        valores_generados["numero"]=numero
        valores_generados["correo"]=correo

        estado_label.configure(text=f"Número generado: {numero}",text_color="green")

    def guardar():

        if valores_generados["numero"]=="":
            estado_label.configure(text="Primero genera número de control",text_color="red")
            return

        datos = (
            valores_generados["numero"],
            entradas["Nombre"].get(),
            entradas["ApellidoPaterno"].get(),
            entradas["ApellidoMaterno"].get(),
            valores_generados["correo"],
            entradas["Carrera"].get(),
            entradas["Semestre"].get(),
            entradas["Estado"].get()
        )

        sql = """
        INSERT INTO alumnos
        (numero_control,nombre_alumno,apellido_paterno,apellido_materno,
        correo_alumno,carrera,semestre,estatus_alumno)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        ejecutar_insert(sql,datos)

        estado_label.configure(text="Alumno guardado",text_color="green")

    botones = customtkinter.CTkFrame(frame_contenido,fg_color="transparent")
    botones.pack(pady=20)

    customtkinter.CTkButton(botones,text="Generar número",command=generar).grid(row=0,column=0,padx=10)
    customtkinter.CTkButton(botones,text="Guardar",command=guardar).grid(row=0,column=1,padx=10)
    customtkinter.CTkButton(botones,text="Cancelar",command=lambda: volver_a_lista() if volver_a_lista else None).grid(row=0,column=2,padx=10)

# MAESTROS

def mostrar_form_registro_maestro(frame_contenido,volver_a_lista=None):

    campos = [
        "matricula_maestro",
        "nombre_maestro",
        "apellido_paterno",
        "apellido_materno",
        "correo",
        "estatus",
        "grado_estudios",
        "perfil_docente",
        "carga_academica",
        "tipo_contrato",
        "cedula_profesional"
    ]

    sql = """
    INSERT INTO maestros
    (matricula_maestro,nombre_maestro,apellido_paterno,apellido_materno,
    correo,estatus,grado_estudios,perfil_docente,carga_academica,tipo_contrato,cedula_profesional)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    crear_formulario_generico(frame_contenido,"Registrar maestro",campos,sql,volver_a_lista)

# MATERIAS

def mostrar_form_registro_materia(frame_contenido,volver_a_lista=None):

    campos = ["id_materia","nombre_materia","horas_semana","creditos","tipo"]

    sql = """
    INSERT INTO materias
    (id_materia,nombre_materia,horas_semana,creditos,tipo)
    VALUES (%s,%s,%s,%s,%s)
    """

    crear_formulario_generico(frame_contenido,"Registrar materia",campos,sql,volver_a_lista)

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

    maestros = obtener_lista("maestros","matricula_maestro")
    materias = obtener_lista("materias","id_materia")

    combo_maestro = crear_combo(cuerpo,0,"Maestro",maestros)
    combo_materia = crear_combo(cuerpo,1,"Materia",materias)

    id_grupo = crear_campo(cuerpo,2,"ID Grupo")
    cupo = crear_campo(cuerpo,3,"Cupo máximo")

    combo_estado = crear_combo(
        cuerpo,
        4,
        "Estado",
        ["Activo","Cerrado","Cancelado"]
    )

    estado_label = customtkinter.CTkLabel(frame_contenido,text="")
    estado_label.pack()

    def guardar():

        maestro = combo_maestro.get()

        # VALIDAR ESTADO DEL MAESTRO
        estado_maestro = ejecutar_select(
            "SELECT estatus FROM maestros WHERE matricula_maestro=%s",
            (maestro,)
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

        valores = (
            id_grupo.get(),
            maestro,
            combo_materia.get(),
            cupo.get(),
            combo_estado.get()
        )

        sql = """
        INSERT INTO grupos
        (id_grupo,matricula_maestro,id_materia,cupo_maximo,estado)
        VALUES (%s,%s,%s,%s,%s)
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

    alumnos = obtener_lista("alumnos","numero_control")
    grupos = obtener_lista("grupos","id_grupo")

    combo_alumno = crear_combo(cuerpo,0,"Alumno",alumnos)
    combo_grupo = crear_combo(cuerpo,1,"Grupo",grupos)

    fecha_registro = crear_campo(cuerpo,2,"Fecha registro")

    combo_estatus = crear_combo(
        cuerpo,
        3,
        "Estatus",
        ["Cursando","Baja","Concluido"]
    )

    tipo_registro = crear_campo(cuerpo,4,"Tipo registro")

    estado_label = customtkinter.CTkLabel(frame_contenido,text="")
    estado_label.pack()

    def guardar():

        alumno = combo_alumno.get()
        grupo = combo_grupo.get()

        # VALIDAR ESTADO ALUMNO
        estado_alumno = ejecutar_select(
            "SELECT estatus_alumno FROM alumnos WHERE numero_control=%s",
            (alumno,)
        )

        if estado_alumno and estado_alumno[0][0] != "Activo":

            estado_label.configure(
                text="Solo alumnos activos pueden inscribirse",
                text_color="red"
            )
            return

        # VALIDAR ESTADO GRUPO
        estado_grupo = ejecutar_select(
            "SELECT estatus FROM grupos WHERE id_grupo=%s",
            (grupo,)
        )

        if estado_grupo and estado_grupo[0][0] in ["Cerrado","Cancelado"]:

            estado_label.configure(
                text="No se pueden inscribir alumnos en este grupo",
                text_color="red"
            )
            return

        valores = (
            alumno,
            grupo,
            fecha_registro.get(),
            combo_estatus.get(),
            tipo_registro.get()
        )

        sql = """
        INSERT INTO registros
        (numero_control,id_grupo,fecha_registro,estatus_materia,tipo_registro)
        VALUES (%s,%s,%s,%s,%s)
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

def mostrar_form_registro_usuario(frame_contenido,volver_a_lista=None):

    campos = ["usuario","contrasena","rol"]

    sql = """
    INSERT INTO usuarios
    (usuario,contrasena,rol)
    VALUES (%s,%s,%s)
    """

    crear_formulario_generico(frame_contenido,"Registrar usuario",campos,sql,volver_a_lista)
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

    # LISTA DE ALUMNOS
    alumnos = obtener_lista("alumnos","numero_control")

    combo_alumno = crear_combo(
        cuerpo,
        0,
        "Alumno",
        alumnos
    )

    # LISTA DE GRUPOS
    grupos = obtener_lista("grupos","id_grupo")

    combo_grupo = crear_combo(
        cuerpo,
        1,
        "Grupo",
        grupos
    )

    # FECHA
    fecha_registro = crear_campo(
        cuerpo,
        2,
        "Fecha registro"
    )

    # ESTATUS
    estatus_opciones = ["Cursando","Baja","Concluido"]

    combo_estatus = crear_combo(
        cuerpo,
        3,
        "Estatus",
        estatus_opciones
    )

    # TIPO
    tipo_registro = crear_campo(
        cuerpo,
        4,
        "Tipo registro"
    )

    estado_label = customtkinter.CTkLabel(frame_contenido,text="")
    estado_label.pack()

    # -------------------------
    # FUNCIÓN GUARDAR
    # -------------------------

    def guardar():

        alumno = combo_alumno.get()
        grupo = combo_grupo.get()

        # VALIDAR ESTADO DEL ALUMNO
        estado_alumno = ejecutar_select(
            "SELECT estatus_alumno FROM alumnos WHERE numero_control=%s",
            (alumno,)
        )

        if estado_alumno and estado_alumno[0][0] != "Activo":

            estado_label.configure(
                text="Solo alumnos activos pueden inscribirse",
                text_color="red"
            )
            return


        # VALIDAR ESTADO DEL GRUPO
        estado_grupo = ejecutar_select(
            "SELECT estado FROM grupos WHERE id_grupo=%s",
            (grupo,)
        )

        if estado_grupo and estado_grupo[0][0] in ["Cerrado","Cancelado"]:

            estado_label.configure(
                text="No se pueden inscribir alumnos en este grupo",
                text_color="red"
            )
            return


        valores = (
            alumno,
            grupo,
            fecha_registro.get(),
            combo_estatus.get(),
            tipo_registro.get()
        )

        sql = """
        INSERT INTO registros
        (numero_control,id_grupo,fecha_registro,estatus_materia,tipo_registro)
        VALUES (%s,%s,%s,%s,%s)
        """

        try:

            ejecutar_insert(sql,valores)

            estado_label.configure(
                text="Inscripción guardada correctamente",
                text_color="green"
            )

            if volver_a_lista:
                volver_a_lista()

        except Exception as e:

            estado_label.configure(
                text=str(e),
                text_color="red"
            )

    # BOTONES
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

def mostrar_form_registro_horario(frame_contenido, volver_a_lista=None):
    campos = ["id_horario", "id_grupo", "dia", "hora_inicio", "hora_fin", "id_salon"]
    sql = """
    INSERT INTO horario
    (id_horario, id_grupo, dia, hora_inicio, hora_fin, id_salon)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    crear_formulario_generico(frame_contenido, "Registrar horario", campos, sql, volver_a_lista)
