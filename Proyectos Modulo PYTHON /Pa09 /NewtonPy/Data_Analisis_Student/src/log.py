from dataclasses import dataclass
from datetime import datetime

@dataclass
class Logger:
    name: str = "pipeline"

    def info(self, msg: str) -> None:
        print(f"[INFO] {self._ts()} [{self.name}] {msg}")

    def warn(self, msg: str) -> None:
        print(f"[WARN] {self._ts()} [{self.name}] {msg}")

    def error(self, msg: str) -> None:
        print(f"[ERROR] {self._ts()} [{self.name}] {msg}")

    def _ts(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Usar el logger
logger = Logger()

# Ejemplo de uso
logger.info("El pipeline ha comenzado.")
logger.warn("Advertencia: El archivo de datos tiene valores faltantes.")
logger.error("Error: No se puede acceder a la base de datos.")

