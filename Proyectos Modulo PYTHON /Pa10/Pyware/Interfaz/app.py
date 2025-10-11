
import os, sys, json
import tkinter as tk
from tkinter import messagebox, ttk
RAIZ = os.path.dirname(os.path.dirname(__file__))
if RAIZ not in sys.path:
    sys.path.append(RAIZ)

from Interfaz.state import set_usuario_actual, get_usuario_actual, ruta_usuarios_json
from Interfaz.menu import construir_menu
from Interfaz.tab_registro import mostrar_registro_diario

# --- Usuarios predeterminados ---
USUARIOS_PREDETERMINADOS = {
    "andres": {"contrasena": "1234", "nombre": "Andres", "apellido": "Gómez", "email": "andres@mail.com", "edad": 35, "genero": "Masculino"},
    "ana":    {"contrasena": "5678", "nombre": "Ana",    "apellido": "Martínez", "email": "ana.martinez@corp.com", "edad": 42, "genero": "Femenino"},
}

def cargar_usuarios():
    ruta = ruta_usuarios_json()
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return USUARIOS_PREDETERMINADOS.copy()
    return USUARIOS_PREDETERMINADOS.copy()

def guardar_usuarios(usuarios: dict):
    ruta = ruta_usuarios_json()
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar usuarios: {e}")

USUARIOS = cargar_usuarios()

# ---------- Ventanas ----------
def abrir_ventana_principal():
    ventana = tk.Tk()
    ventana.title("MAC - Panel Principal")
    ventana.geometry("1100x650")
    ventana.configure(bg="white")

    encabezado = tk.Frame(ventana, height=50, bg="dark violet")
    encabezado.pack(side="top", fill="x")

    tk.Label(encabezado, text="Motor de Análisis de Correlación (MAC)",
             font=("Arial", 14, "bold"), bg="dark violet", fg="white").pack(side="left", padx=20, pady=10)

    cont_usuario = tk.Frame(encabezado, bg="dark violet")
    cont_usuario.pack(side="right", padx=10)
    tk.Label(cont_usuario, text=get_usuario_actual(), font=("Arial", 12),
             bg="dark violet", fg="white").pack(side="left", padx=10)
    tk.Button(cont_usuario, text="Cerrar Sesión 🚪", bg="#DC3545", fg="white", font=("Arial", 10),
              command=lambda: (ventana.destroy(), abrir_ventana_login())).pack(side="left", padx=10)

    menu_lateral = tk.Frame(ventana, width=220, bg="white")
    menu_lateral.pack(side="left", fill="y")
    tk.Frame(ventana, width=1, bg="#CCCCCC").pack(side="left", fill="y")
    panel_derecho = tk.Frame(ventana, bg="white")
    panel_derecho.pack(side="right", expand=True, fill="both")
    construir_menu(panel_derecho, menu_lateral)
    # Abrir por defecto el Registro Diario
    mostrar_registro_diario(panel_derecho)

    ventana.mainloop()

def abrir_ventana_registro(ventana_login, entry_usuario, entry_contrasena):
    ventana_reg = tk.Toplevel(ventana_login)
    ventana_reg.title("Registrar Usuario")
    ventana_reg.geometry("460x460")
    ventana_reg.transient(ventana_login)
    ventana_reg.grab_set()

    tk.Label(ventana_reg, text="Complete sus Datos de Registro",
             font=("Arial", 14, "bold"), pady=10).pack()

    marco = tk.Frame(ventana_reg, padx=10, pady=10)
    marco.pack(expand=True)

    entradas = {}
    campos = ["Nombre de Usuario:", "Contraseña:", "Nombre:", "Apellido:", "Email:", "Edad:", "Género:"]
    claves = ["usuario", "contrasena", "nombre", "apellido", "email", "edad", "genero"]
    genero_var = tk.StringVar(value="-- Seleccionar --")

    for i, (et, key) in enumerate(zip(campos, claves)):
        tk.Label(marco, text=et, anchor="w", width=20).grid(row=i, column=0, padx=5, pady=5)
        if key == "genero":
            entrada = ttk.Combobox(marco, textvariable=genero_var, values=["Femenino","Masculino","Otro"], state="readonly", width=28)
        else:
            entrada = tk.Entry(marco, width=30, show="*" if key=="contrasena" else "")
        entrada.grid(row=i, column=1, padx=5, pady=5)
        entradas[key] = entrada

    def guardar():
        datos = {k: entradas[k].get().strip() for k in claves if k != "genero"}
        datos["genero"] = genero_var.get()
        try:
            if any(not v for v in datos.values()) or datos['genero'] == "-- Seleccionar --":
                raise ValueError("Por favor, complete todos los campos.")
            if datos['usuario'] in USUARIOS:
                raise ValueError("El nombre de usuario ya existe.")
            if "@" not in datos['email'] or "." not in datos['email']:
                raise ValueError("Email inválido.")
            datos['edad'] = int(datos['edad'])
            usuario = datos.pop("usuario")
            USUARIOS[usuario] = datos
            guardar_usuarios(USUARIOS)
            messagebox.showinfo("Registro Exitoso", f"Usuario '{usuario}' registrado. Ya puedes iniciar sesión.", parent=ventana_reg)
            ventana_reg.destroy()
            entry_usuario.delete(0, tk.END); entry_usuario.insert(0, usuario)
            entry_contrasena.delete(0, tk.END); entry_contrasena.insert(0, datos["contrasena"])
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=ventana_reg)

    tk.Button(marco, text="Registrar y Volver", bg="#4CAF50", fg="white",
              font=("Arial", 10, "bold"), command=guardar)\
        .grid(row=len(campos), column=0, columnspan=2, pady=20)

def abrir_ventana_login():
    ventana = tk.Tk()
    ventana.title("MAC - Iniciar Sesión")
    ventana.geometry("800x420")
    ventana.resizable(False, False)

    izq = tk.Frame(ventana, width=400, bg="dark violet")
    izq.pack(side="left", fill="both", expand=True)
    tk.Label(izq, text="Motor de Análisis de Correlación\npara Artritis Reumatoide",
             font=("Arial", 16), bg="dark violet", fg="white", justify="center").pack(expand=True)

    der = tk.Frame(ventana, width=400, bg="white")
    der.pack(side="right", fill="both", expand=True)

    cont = tk.Frame(der, bg="white"); cont.pack(expand=True)

    tk.Label(cont, text="Usuario o Email", bg="white").pack(pady=(10,5))
    entry_usuario = tk.Entry(cont, width=30); entry_usuario.pack()
    entry_usuario.insert(0, "andres")

    tk.Label(cont, text="Contraseña", bg="white").pack(pady=(10,5))
    entry_contrasena = tk.Entry(cont, show="*", width=30); entry_contrasena.pack()
    entry_contrasena.insert(0, "1234")

    def verificar():
        usuario = entry_usuario.get().strip()
        contrasena = entry_contrasena.get().strip()
        if usuario in USUARIOS and USUARIOS[usuario]["contrasena"] == contrasena:
            set_usuario_actual(usuario)
            ventana.destroy()
            abrir_ventana_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos", parent=ventana)

    tk.Button(cont, text="Ingresar", bg="#1976D2", fg="white", width=20, command=verificar).pack(pady=20)
    tk.Button(cont, text="¿No tienes cuenta? Regístrate aquí", fg="blue", bg="white",
              cursor="hand2", borderwidth=0,
              command=lambda: abrir_ventana_registro(ventana, entry_usuario, entry_contrasena)).pack()

    ventana.mainloop()

if __name__ == "__main__":
    abrir_ventana_login()
