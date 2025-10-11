import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from adm_tareas import TaskManager
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Tareas")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Inicializar el TaskManager
        self.task_manager = TaskManager()

        # Configurar la interfaz
        self.setup_ui()

        # Cargar las tareas existentes
        self.refresh_task_list()

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar el grid para que se expanda
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Título
        title_label = ttk.Label(main_frame, text="GESTOR DE TAREAS", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.N, tk.W), padx=(0, 10))

        # Botones
        ttk.Button(button_frame, text="Crear Tarea", command=self.create_task_dialog).grid(row=0, column=0, pady=5, sticky=tk.W)
        ttk.Button(button_frame, text="Actualizar Tarea", command=self.update_task_dialog).grid(row=1, column=0, pady=5, sticky=tk.W)
        ttk.Button(button_frame, text="Eliminar Tarea", command=self.delete_task).grid(row=2, column=0, pady=5, sticky=tk.W)
        ttk.Button(button_frame, text="Limpiar Todas", command=self.clear_all_tasks).grid(row=3, column=0, pady=5, sticky=tk.W)
        ttk.Button(button_frame, text="Actualizar Lista", command=self.refresh_task_list).grid(row=4, column=0, pady=5, sticky=tk.W)
        ttk.Button(button_frame, text="Subtareas", command=self.manage_subtasks_dialog).grid(row=5, column=0, pady=5, sticky=tk.W)
        ttk.Button(button_frame, text="Ver Gráfico", command=self.show_task_graph).grid(row=6, column=0, pady=5, sticky=tk.W)
        ttk.Button(button_frame, text="Exportar CSV", command=self.export_csv).grid(row=7, column=0, pady=5, sticky=tk.W)
        # Frame para la lista de tareas
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview para mostrar las tareas
        columns = ("Índice", "Nombre", "Estado", "Progreso", "Creado por", "Fecha")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)


        # Configurar las columnas
        self.task_tree.heading("Índice", text="Índice")
        self.task_tree.heading("Nombre", text="Nombre de la Tarea")
        self.task_tree.heading("Estado", text="Estado")
        self.task_tree.heading("Progreso", text="Progreso (%)")
        self.task_tree.heading("Creado por", text="Creado por")
        self.task_tree.heading("Fecha", text="Fecha de Creación")

        # Configurar el ancho de las columnas
        self.task_tree.column("Índice", width=60, minwidth=50)
        self.task_tree.column("Nombre", width=260, minwidth=150)
        self.task_tree.column("Estado", width=110, minwidth=80)
        self.task_tree.column("Progreso", width=110, minwidth=80)
        self.task_tree.column("Creado por", width=140, minwidth=100)
        self.task_tree.column("Fecha", width=160, minwidth=120)

        # Scrollbar para el Treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        # Colocar el Treeview y scrollbar
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Frame de información
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, columnspan=3, pady=(20, 0), sticky=(tk.W, tk.E))
        info_frame.columnconfigure(0, weight=1)

        self.info_label = ttk.Label(info_frame, text="Seleccione una tarea para ver más opciones", font=("Arial", 10))
        self.info_label.grid(row=0, column=0, sticky=tk.W)

    def refresh_task_list(self):
        """Actualizar la lista de tareas en el Treeview"""
        # Limpiar el Treeview
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Obtener las tareas
        tasks = self.task_manager.list_tasks()

        # Agregar las tareas al Treeview
        for index, task in enumerate(tasks):
            estado_texto = "Completada" if task["estatus"] == 0 else "Pendiente"
            fecha_formateada = task["fecha de creación"][:19].replace("T", " ")

            self.task_tree.insert("", "end", values=(
                index,
                task["nombre de la tarea"],
                estado_texto,
                f"{task['progreso']}%",
                task["creado por"],
                fecha_formateada
            ))

        # Actualizar el contador
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task["estatus"] == 0)
        self.info_label.config(text=f"Total: {total_tasks} tareas | Completadas: {completed_tasks} | Pendientes: {total_tasks - completed_tasks}")

    def get_selected_task_index(self):
        """Obtener el índice de la tarea seleccionada"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione una tarea.")
            return None

        item = self.task_tree.item(selection[0])
        return int(item['values'][0])

    def create_task_dialog(self):
        """Diálogo para crear una nueva tarea"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Crear Nueva Tarea")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Centrar el diálogo
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))

        # Frame principal del diálogo
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Campos de entrada
        ttk.Label(frame, text="Nombre de la tarea:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Creado por:").grid(row=1, column=0, sticky=tk.W, pady=5)
        creator_entry = ttk.Entry(frame, width=30)
        creator_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        # Funciones para los botones
        def create_task():
            name = name_entry.get().strip()
            creator = creator_entry.get().strip()

            if not name:
                messagebox.showerror("Error", "El nombre de la tarea es obligatorio.")
                return

            if not creator:
                messagebox.showerror("Error", "El campo 'Creado por' es obligatorio.")
                return

            # Crear la tarea
            self.task_manager.create_task(name, creator)
            dialog.destroy()
            messagebox.showinfo("Éxito", f"Tarea '{name}' creada correctamente.")
           
            self.refresh_task_list()

        def cancel():
            dialog.destroy()

        # Frame de botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Crear", command=create_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=cancel).pack(side=tk.LEFT, padx=5)

        # Foco en el primer campo
        name_entry.focus()

    def update_task_dialog(self):
        """Diálogo para actualizar una tarea"""
        index = self.get_selected_task_index()
        if index is None:
            return

        # Obtener la tarea actual
        task = self.task_manager.get_task(index)
        if not task:
            messagebox.showerror("Error", "No se pudo obtener la tarea seleccionada.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Actualizar Tarea")
        dialog.geometry("480x320")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Centrar el diálogo
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))

        # Frame principal del diálogo
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Campos de entrada con valores actuales
        ttk.Label(frame, text="Nombre de la tarea:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=task["nombre de la tarea"])
        name_entry = ttk.Entry(frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Estado:").grid(row=1, column=0, sticky=tk.W, pady=5)
        status_var = tk.StringVar(value="Completada" if task["estatus"] == 0 else "Pendiente")
        status_combo = ttk.Combobox(frame, textvariable=status_var, values=["Pendiente", "Completada"], state="readonly", width=27)
        status_combo.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Progreso (%):").grid(row=2, column=0, sticky=tk.W, pady=5)
        progress_var = tk.IntVar(value=task["progreso"])
        progress_scale = ttk.Scale(frame, from_=0, to=100, variable=progress_var, orient=tk.HORIZONTAL, length=220)
        progress_scale.grid(row=2, column=1, pady=5, padx=(10, 0), sticky=tk.W)

        progress_label = ttk.Label(frame, text=f"{task['progreso']}%")
        progress_label.grid(row=2, column=2, pady=5, padx=(5, 0))

        # Si la tarea tiene subtareas, el progreso es calculado dinámicamente
        tiene_subtareas = bool(task.get("subtareas"))
        if tiene_subtareas:
            progress_scale.state(["disabled"])
            progress_label.config(text=f"{task['progreso']}% (calculado)")

        # Actualizar la etiqueta del progreso (cuando está habilitado)
        def update_progress_label(value):
            progress_label.config(text=f"{int(float(value))}%")

        progress_scale.config(command=update_progress_label)

        # Información adicional (solo lectura)
        ttk.Label(frame, text="Creado por:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=task["creado por"], foreground="gray").grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        ttk.Label(frame, text="Fecha de creación:").grid(row=4, column=0, sticky=tk.W, pady=5)
        fecha_formateada = task["fecha de creación"][:19].replace("T", " ")
        ttk.Label(frame, text=fecha_formateada, foreground="gray").grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # Funciones para los botones
        def update_task():
            name = name_var.get().strip()
            status = 0 if status_var.get() == "Completada" else 1

            if not name:
                messagebox.showerror("Error", "El nombre de la tarea es obligatorio.")
                return

            if tiene_subtareas:
                # Progreso calculado por subtareas
                updated_task = self.task_manager.update_task(index, name=name, status=status, progress=None)
            else:
                # Progreso manual
                if status == 0:
                    progress = 100
                    progress_scale.state(["disabled"])
                else:
                    progress = progress_var.get()
                updated_task = self.task_manager.update_task(index, name=name, status=status, progress=progress)

            if updated_task:
                dialog.destroy()
                messagebox.showinfo("Éxito", "Tarea actualizada correctamente.")
                
                self.refresh_task_list()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la tarea.")

        def cancel():
            dialog.destroy()

        # Frame de botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Actualizar", command=update_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=cancel).pack(side=tk.LEFT, padx=5)

        # Foco en el primer campo
        name_entry.focus()
    
    def export_csv(self):
        try:
            self.task_manager.export_to_csv()
            messagebox.showinfo("Éxito", "CSV generado correctamente en 'carpeta_data/data_analitica.csv'.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el CSV:\n{str(e)}")

    def show_task_graph(self):
        try:
            tasks = self.task_manager.list_tasks()
            completed = sum(1 for task in tasks if task["estatus"] == 0)
            pending = sum(1 for task in tasks if task["estatus"] == 1)

            if completed + pending == 0:
                messagebox.showinfo("Información", "No hay tareas para graficar.")
                return

            # Crear figura
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(
                [completed, pending],
                labels=["Completadas", "Pendientes"],
                autopct="%1.1f%%",
                startangle=90,
                colors=["green", "red"]
            )
            ax.set_title("Estado de las Tareas")

            # Mostrar la gráfica en una ventana independiente
            plt.show()
        except FileNotFoundError:
            messagebox.showerror("Error", "Primero genere el CSV con 'Exportar CSV'.")

    def delete_task(self):
        """Eliminar la tarea seleccionada"""
        index = self.get_selected_task_index()
        if index is None:
            return

        # Obtener la tarea para mostrar información
        task = self.task_manager.get_task(index)
        if not task:
            messagebox.showerror("Error", "No se pudo obtener la tarea seleccionada.")
            return

        # Confirmar eliminación
        result = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar la tarea:\n\n'{task['nombre de la tarea']}'?\n\nEsta acción no se puede deshacer."
        )

        if result:
            self.task_manager.delete_task(index)
            messagebox.showinfo("Éxito", "Tarea eliminada correctamente.")
            self.refresh_task_list()

    def clear_all_tasks(self):
        """Limpiar todas las tareas"""
        tasks = self.task_manager.list_tasks()
        if not tasks:
            messagebox.showinfo("Información", "No hay tareas para eliminar.")
            return

        result = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar TODAS las tareas ({len(tasks)} tareas)?\n\nEsta acción no se puede deshacer."
        )

        if result:
            self.task_manager.db.clear()
            messagebox.showinfo("Éxito", "Todas las tareas han sido eliminadas.")
            self.refresh_task_list()

    def manage_subtasks_dialog(self):
        """Diálogo para gestionar subtareas de la tarea seleccionada."""
        index = self.get_selected_task_index()
        if index is None:
            return
        task = self.task_manager.get_task(index)
        if not task:
            messagebox.showerror("Error", "No se pudo obtener la tarea seleccionada.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Subtareas de: {task['nombre de la tarea']}")
        dialog.geometry("540x420")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="12")
        frame.pack(fill=tk.BOTH, expand=True)

        # Lista de subtareas
        columns = ("#", "Nombre", "Estado")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for c, w in zip(columns, (60, 320, 120)):
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor=tk.W)
        tree.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=3, sticky=(tk.N, tk.S))

        # ---------- funciones internas (deben quedar dentro de este método) ----------
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            t = self.task_manager.get_task(index)  # fresco
            subs = t.get("subtareas", [])
            for i, s in enumerate(subs):
                estado = "Completada" if s.get("estatus", 1) == 0 else "Pendiente"
                tree.insert("", "end", values=(i, s.get("nombre", ""), estado))
            # mostrar progreso actualizado abajo
            progreso = t.get("progreso", 0)
            info.config(text=f"Progreso: {progreso}% (calculado por subtareas)")

        def selected_index():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Advertencia", "Seleccione una subtarea.")
                return None
            return int(tree.item(sel[0])["values"][0])

        def add_subtask():
            name = simpledialog.askstring("Nueva subtarea", "Nombre de la subtarea:", parent=dialog)
            if not name:
                return
            self.task_manager.add_subtask(index, name.strip())
            refresh()
            self.refresh_task_list()

        def toggle_subtask():
            si = selected_index()
            if si is None:
                return
            t = self.task_manager.get_task(index)
            sub = t.get("subtareas", [])[si]
            actual_completed = (sub.get("estatus", 1) == 0)
            self.task_manager.set_subtask_status(index, si, completed=not actual_completed)
            refresh()
            self.refresh_task_list()

        def delete_subtask():
            si = selected_index()
            if si is None:
                return
            self.task_manager.delete_subtask(index, si)
            refresh()
            self.refresh_task_list()

        # Controles
        ttk.Button(frame, text="Agregar", command=add_subtask).grid(row=1, column=0, pady=10, sticky=tk.W)
        ttk.Button(frame, text="Completado/Pendiente", command=toggle_subtask).grid(row=1, column=1, pady=10, sticky=tk.W)
        ttk.Button(frame, text="Eliminar", command=delete_subtask).grid(row=1, column=2, pady=10, sticky=tk.W)
        ttk.Button(frame, text="Cerrar", command=dialog.destroy).grid(row=3, column=0, pady=10, sticky=tk.E)
        info = ttk.Label(frame, text="")
        info.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))

        refresh()


def main():
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    
