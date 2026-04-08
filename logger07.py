# script_logger_final.py
from melloger.logger_core import crear_logger
from datetime import datetime
import time

class ScriptLogger:
    """
    Logger avanzado para scripts:
    - 5 niveles: step, info, warning, error, success
    - Iconos y colores automáticos
    - Execution ID único por ejecución
    - Timestamp real y tiempo relativo desde inicio
    """
    ICONOS = {
        "STEP": "▶",
        "INFO": "🛈",
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

    RUN_COUNTER = 0  # contador global de ejecuciones

    def __init__(self, nombre_logger="mi_logger", nivel=10):
        """
        Inicializa el ScriptLogger:
        - nombre_logger: nombre del logger reutilizable
        - nivel: nivel mínimo de logging (DEBUG=10, INFO=20, etc.)
        """
        self.logger = crear_logger(nombre_logger, nivel)
        ScriptLogger.RUN_COUNTER += 1
        self.execution_id = f"RUN_{ScriptLogger.RUN_COUNTER:03d}"
        self.start_time = time.perf_counter()

    # Métodos públicos
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

    # Método interno
    def _log(self, nivel, mensaje):
        # Icono y color
        icono = self.ICONOS.get(nivel, "")
        color = self.COLORES.get(nivel, "white")

        # Timestamp real
        hora_actual = datetime.now().strftime("%H:%M:%S")

        # Tiempo relativo desde inicio
        elapsed = time.perf_counter() - self.start_time
        if elapsed < 60:
            ts_rel = f"{elapsed:.3f}s"
        else:
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            ts_rel = f"{minutes}m {seconds:.1f}s"

        # Formato final
        msg_rich = f"[{color}][{self.execution_id}] [{hora_actual}] [{ts_rel}] {icono} {mensaje}[/{color}]"

        # Enviar al logger según nivel
        if nivel in ("STEP", "INFO", "SUCCESS"):
            self.logger.info(msg_rich)
        elif nivel == "WARNING":
            self.logger.warning(msg_rich)
        elif nivel == "ERROR":
            self.logger.error(msg_rich)