from json_db import DB
from datetime import datetime
from data_logger import DataLogger

class TaskManager:
    def __init__(self):
        self.db = DB()  # Base de datos local JSON

    # --------------------------
    # Helpers internos
    # --------------------------
    def _recalc_progress_and_status(self, task: dict) -> dict:
        """Recalcula progreso (0..100) y estatus (0: completada, 1: pendiente) en base a las subtareas."""
        subtareas = task.get("subtareas", [])
        total = len(subtareas)
        if total > 0:
            done = sum(1 for s in subtareas if s.get("estatus", 1) == 0)
            task["progreso"] = int(round(done * 100 / total))
            task["estatus"] = 0 if done == total and total > 0 else 1
        else:
            # Sin subtareas, mantenemos lo que tenga (manual)
            task["progreso"] = int(task.get("progreso", 0))
            task["estatus"] = int(task.get("estatus", 1))
        return task

    def export_to_csv(self, path="carpeta_data/data_analitica.csv"):
        logger = DataLogger(path)
        logger.save_tasks(self.list_tasks())

    # --------------------------
    # CRUD de tareas principales
    # --------------------------
    def create_task(self, name, created_by):
        task = {
            "estatus": 1,                                # 1 = pendiente, 0 = completada
            "nombre de la tarea": name,
            "progreso": 0,                               # 0..100
            "creado por": created_by,
            "fecha de creación": datetime.now().isoformat(),
            "subtareas": []                              # NUEVO: lista de subtareas
        }
        return self.db.insert(task)

    def get_task(self, index):
        try:
            return self.db.get(index)
        except IndexError:
            return None

    def update_task(self, index, name=None, status=None, progress=None):
        task = self.get_task(index)
        if not task:
            return None

        if name is not None:
            task["nombre de la tarea"] = name

        # Si la tarea tiene subtareas, el progreso/estatus es calculado dinámicamente
        if task.get("subtareas"):
            if status is not None:
                task["estatus"] = int(status)
            task = self._recalc_progress_and_status(task)
        else:
            if status is not None:
                task["estatus"] = int(status)
            if progress is not None:
                task["progreso"] = int(progress)
            # Coherencia: 100% => completada, <100% => pendiente
            if task["progreso"] >= 100:
                task["progreso"] = 100
                task["estatus"] = 0
            elif task["estatus"] == 0 and task["progreso"] < 100:
                task["estatus"] = 1

        self.db.update(index, task)
        return task

    def delete_task(self, index):
        try:
            self.db.delete(index)
        except IndexError:
            pass

    def list_tasks(self):
        """Devuelve todas las tareas, recalculando progreso/estatus si tienen subtareas."""
        tasks = self.db.getAll()
        for i, t in enumerate(tasks):
            recalculated = self._recalc_progress_and_status(t)
            if recalculated != t:
                self.db.update(i, recalculated)
        # devolver fresco desde DB
        return self.db.getAll()

    # --------------------------
    # Subtareas
    # --------------------------
    def add_subtask(self, index, name: str):
        task = self.get_task(index)
        if not task:
            return None
        task.setdefault("subtareas", [])
        task["subtareas"].append({"nombre": name, "estatus": 1})  # 1 = pendiente
        task = self._recalc_progress_and_status(task)
        self.db.update(index, task)
        return task

    def set_subtask_status(self, index, sub_index, completed: bool):
        task = self.get_task(index)
        if not task:
            return None
        subs = task.get("subtareas", [])
        if 0 <= sub_index < len(subs):
            subs[sub_index]["estatus"] = 0 if completed else 1
            task = self._recalc_progress_and_status(task)
            self.db.update(index, task)
            return task
        return None

    def delete_subtask(self, index, sub_index):
        task = self.get_task(index)
        if not task:
            return None
        subs = task.get("subtareas", [])
        if 0 <= sub_index < len(subs):
            del subs[sub_index]
            task = self._recalc_progress_and_status(task)
            self.db.update(index, task)
            return task
        return None
