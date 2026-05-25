from db_conexion import conexion
import customtkinter

def cambiar_modo():
    modo_actual = customtkinter.get_appearance_mode()
    if modo_actual == "Light":
        customtkinter.set_appearance_mode("dark")
    else:
        customtkinter.set_appearance_mode("light")

def buscar_usuario(usuario):
    cursor = conexion.cursor()
    
    query = "SELECT usuario, contrasena, rol FROM usuarios WHERE usuario = %s"
    cursor.execute(query, (usuario,))
    resultado = cursor.fetchone() 
    cursor.close()  
    return resultado


def validar_contrasena(contrasena_ingresada, contrasena_guardada):
    return contrasena_ingresada == contrasena_guardada


def autenticar_usuario(usuario, contrasena):
    usuario_db = buscar_usuario(usuario)

    if usuario_db is None:
        return False, None, None

    usuario_guardado, contrasena_guardada, rol = usuario_db

    if validar_contrasena(contrasena, contrasena_guardada):
        return True, rol, usuario_guardado
    else:
        return False, None, None


def generar_mensaje_login(usuario, contrasena):
    usuario_limpio = usuario.strip()
    contra_limpia = contrasena.strip()

    # Campos vacíos
    if usuario_limpio == "" or contra_limpia == "":
        return {
            "texto": "Por favor, complete ambos campos.",
            "fg_color": ("#FFF4CC", "#5A4B00"),
            "text_color": ("#9A6B00", "#FFE8A3"),
            "exitoso": False,
            "rol": None,
            "usuario": None,
        }

    # Autenticación contra base de datos
    ok, rol, usuario_db = autenticar_usuario(usuario_limpio, contra_limpia)
    if ok == True:
        return {
            "texto": "¡Inicio de sesión exitoso!",
            "fg_color": ("#DDF7E3", "#1F6F3C"),
            "text_color": ("#1F6F3C", "#9EF0B0"),
            "exitoso": True,
            "rol": rol,
            "usuario": usuario_db,
        }
    else:
    # Credenciales incorrectas
        return {
        "texto": "Usuario o contraseña incorrectos.",
        "fg_color": ("#FCE1E1", "#8A1F1F"),
        "text_color": ("#B00020", "#FFB3B3"),
        "exitoso": False,
        "rol": None,
        "usuario": None,
        }


def mostrar_ocultar(entry_widget, button_widget):

    actual = entry_widget.cget("show")
    if actual == "":
        # Actualmente visible 
        entry_widget.configure(show="*")
        button_widget.configure(text="Mostrar Contraseña")
    else:
        # Actualmente oculta 
        entry_widget.configure(show="")
        button_widget.configure(text="Ocultar Contraseña")