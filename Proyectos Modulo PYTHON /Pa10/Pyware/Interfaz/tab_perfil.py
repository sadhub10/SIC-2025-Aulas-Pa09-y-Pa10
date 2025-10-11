
import json
import tkinter as tk
from tkinter import messagebox
from .state import get_usuario_actual, ruta_usuarios_json

def _cargar_usuarios():
    ruta = ruta_usuarios_json()
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _guardar_usuarios(usuarios: dict):
    ruta = ruta_usuarios_json()
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar usuarios: {e}")

def mostrar_perfil(panel_contenedor: tk.Frame):
    for w in panel_contenedor.winfo_children():
        w.destroy()

    usuario = get_usuario_actual()
    usuarios = _cargar_usuarios()
    datos = usuarios.get(usuario, {
        "contrasena": "",
        "nombre": "",
        "apellido": "",
        "email": "",
        "edad": "",
        "genero": "",
    })

    cont = tk.Frame(panel_contenedor, bg="white")
    cont.place(relx=0.5, rely=0.1, anchor="n")

    tk.Label(cont, text="Información de Mi Perfil",
             font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    form = tk.Frame(cont, bg="white", padx=20, pady=10)
    form.pack()

    # Vars
    nombre_var   = tk.StringVar(value=datos.get("nombre", ""))
    apellido_var = tk.StringVar(value=datos.get("apellido", ""))
    email_var    = tk.StringVar(value=datos.get("email", ""))
    edad_var     = tk.StringVar(value=str(datos.get("edad", "")))
    genero_var   = tk.StringVar(value=datos.get("genero", ""))

    campos = [
        ("Nombre:", nombre_var),
        ("Apellido:", apellido_var),
        ("Email:", email_var),
        ("Edad:", edad_var),
        ("Género:", genero_var),
    ]
    for i, (txt, var) in enumerate(campos):
        tk.Label(form, text=txt, bg="white", anchor="e", width=20)\
          .grid(row=i, column=0, padx=5, pady=5)
        tk.Entry(form, textvariable=var, width=40)\
          .grid(row=i, column=1, padx=5, pady=5)

    def guardar():
        try:
            if not all(v.get().strip() for _, v in campos):
                raise ValueError("Ningún campo puede estar vacío.")
            if "@" not in email_var.get() or "." not in email_var.get():
                raise ValueError("El formato del email no es válido.")
            edad = int(edad_var.get())

            usuarios.setdefault(usuario, {})
            usuarios[usuario].update({
                "nombre": nombre_var.get().strip(),
                "apellido": apellido_var.get().strip(),
                "email": email_var.get().strip(),
                "edad": edad,
                "genero": genero_var.get().strip(),
            })
            _guardar_usuarios(usuarios)
            messagebox.showinfo("Actualización Exitosa",
                                "La información de tu perfil ha sido guardada.",
                                parent=panel_contenedor)
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e), parent=panel_contenedor)

    tk.Button(cont, text="Actualizar Información",
              bg="#1976D2", fg="white", font=("Arial", 12, "bold"),
              width=25, command=guardar).pack(pady=20)
