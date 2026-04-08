# script_logger.py
from caepwtamelloger.logger_core import crear_logger

class ScriptLogger:
    ICONOS = {
        "STEP": "▶",
        "INFO": "ℹ",
        "WARNING": "⚠",
        "ERROR": "✖",
        "SUCCESS": "✔"
    }

    COLORES = {
        "STEP": "cyan",
        "INFO": "white",
        "WARNING": "yellow",
        "ERROR": "red",
        "SUCCESS": "green"
    }

    def __init__(self, nombre_logger="mi_logger", nivel=10):
        self.logger = crear_logger(nombre_logger, nivel)

    def step(self, mensaje):
        self._log("STEP", mensaje)

    def info(self, mensaje):
        self._log("INFO", mensaje)

    def warning(self, mensaje):
        self._log("WARNING", mensaje)

    def error(self, mensaje):
        self._log("ERROR", mensaje)

    def success(self, mensaje):
        self._log("SUCCESS", mensaje)

    def _log(self, nivel, mensaje):
        icono = self.ICONOS.get(nivel, "")
        color = self.COLORES.get(nivel, "white")
        msg_rich = f"[{color}]{icono} {mensaje}[/{color}]"

        if nivel in ("STEP", "INFO", "SUCCESS"):
            self.logger.info(msg_rich)
        elif nivel == "WARNING":
            self.logger.warning(msg_rich)
        elif nivel == "ERROR":
            self.logger.error(msg_rich)