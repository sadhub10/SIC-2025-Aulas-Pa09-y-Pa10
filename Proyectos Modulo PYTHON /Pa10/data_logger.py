import csv
import os

class DataLogger:
    def __init__(self, file_path):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def save_tasks(self, tasks):
        """Guardar lista de tareas en CSV"""
        if not tasks:
            return

        headers = ["uid", "nombre de la tarea", "estatus", "progreso", "creado por", "fecha de creación"]

        with open(self.file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for i, task in enumerate(tasks):
                # Añadir uid automáticamente si no existe
                row = {key: task.get(key, "") for key in headers}
                row["uid"] = i
                writer.writerow(row)
