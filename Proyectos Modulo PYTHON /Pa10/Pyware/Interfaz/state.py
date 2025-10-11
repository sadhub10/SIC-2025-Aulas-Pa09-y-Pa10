
import os

usuario_actual = ""
ruta_datos = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(ruta_datos, exist_ok=True)

def set_usuario_actual(nombre):
    global usuario_actual
    usuario_actual = nombre or ""

def get_usuario_actual():
    return usuario_actual

def ruta_csv_actual():
    u = get_usuario_actual() or "usuario"
    return os.path.join(ruta_datos, f"{u}_registros.csv")

def ruta_usuarios_json():
    return os.path.join(ruta_datos, "usuarios.json")
