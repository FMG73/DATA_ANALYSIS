# script_logger_final_total.py
from melloger.logger_core import crear_logger
from datetime import datetime
import time
import csv
from pathlib import Path

class ScriptLogger:
    """
    Logger avanzado para scripts:
    - 5 niveles: step, info, warning, error, success
    - Iconos y colores automáticos
    - Execution ID único por ejecución
    - Timestamp real y tiempo relativo desde inicio
    - Registro automático en CSV con línea total al final
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

    def __init__(self, nombre_logger="mi_logger", nivel=10, csv_path=None):
        self.logger = crear_logger(nombre_logger, nivel)
        ScriptLogger.RUN_COUNTER += 1
        self.execution_id = f"RUN_{ScriptLogger.RUN_COUNTER:03d}"
        self.start_time = time.perf_counter()
        self.csv_path = Path(csv_path) if csv_path else None
        if self.csv_path:
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        self._hubo_error = False  # Flag para marcar total KO si hubo error

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

    def fin_script(self, mensaje="FIN SCRIPT"):
        """
        Escribe la línea total al final del CSV y consola.
        Marca KO si hubo algún error durante la ejecución.
        """
        fin_total = time.perf_counter()
        duracion_total = fin_total - self.start_time
        if duracion_total < 60:
            dur_total = f"{duracion_total:.3f}s"
        else:
            min_total = int(duracion_total // 60)
            sec_total = duracion_total % 60
            dur_total = f"{min_total}m {sec_total:.1f}s"

        estado_total = "KO" if self._hubo_error else "OK"

        # Guardar en CSV
        if self.csv_path:
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fila_resumen = [fecha_hora, self.execution_id, estado_total, "TOTAL", mensaje, dur_total]
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(fila_resumen)

        # Imprimir en consola
        from rich.console import Console
        console = Console()
        color = "red" if self._hubo_error else "green"
        console.print(f"[bold {color}][{self.execution_id}] [{dur_total}] {mensaje} ({estado_total})[/bold {color}]")

    # Método interno
    def _log(self, nivel, mensaje):
        icono = self.ICONOS.get(nivel, "")
        color = self.COLORES.get(nivel, "white")
        hora_actual = datetime.now().strftime("%H:%M:%S")
        elapsed = time.perf_counter() - self.start_time
        ts_rel = f"{elapsed:.3f}s" if elapsed < 60 else f"{int(elapsed//60)}m {elapsed%60:.1f}s"
        msg_rich = f"[{color}][{self.execution_id}] [{hora_actual}] [{ts_rel}] {icono} {mensaje}[/{color}]"

        # Log en consola según nivel
        if nivel in ("STEP", "INFO", "SUCCESS"):
            self.logger.info(msg_rich)
        elif nivel == "WARNING":
            self.logger.warning(msg_rich)
        elif nivel == "ERROR":
            self.logger.error(msg_rich)
            self._hubo_error = True  # marcar que hubo error

        # Guardar en CSV
        if self.csv_path:
            estado = "OK" if nivel != "ERROR" else "KO"
            fila = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.execution_id, estado, nivel, mensaje, ts_rel]
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(fila)