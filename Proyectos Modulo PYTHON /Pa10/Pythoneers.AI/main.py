#codigo de prueba estandar 
""""from adm_tareas import TaskManager 

tm = TaskManager()  # TaskManager usa DB internamente

# Crear tareas
tm.create_task("Example", "Luis")

# Listar tareas
print(tm.list_tasks())

# Actualizar tarea
tm.update_task(0, status=0, progress=50)

# Obtener tarea específica
print(tm.get_task(0)['uid'])

# Eliminar tarea
tm.delete_task(0)

# Limpiar todas las tareas desde la DB directamente
tm.db.clear()
print(tm.list_tasks()) """

# Interfaz gráfica para el gestor de tareas usando tkinter

from gui_tareas import TaskManagerGUI
import tkinter as tk
from adm_tareas import TaskManager


def main():
    # Crear la ventana principal
    root = tk.Tk()
    
    # Crear e inicializar la aplicación GUI
    app = TaskManagerGUI(root)
    
    # Iniciar el bucle principal de la interfaz gráfica
    root.mainloop()


if __name__ == "__main__":
    main()


