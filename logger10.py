# melloger/script_logger_final_prd.py
from melloger.logger_core import crear_logger
from datetime import datetime
import time
import csv
from pathlib import Path
from rich.console import Console
import __main__

class ScriptLogger:
    """
    Logger avanzado tipo PRD para scripts.
    - 5 niveles: STEP, INFO, WARNING, ERROR, SUCCESS
    - Iconos y colores automáticos
    - Execution ID único por ejecución
    - Hora y tiempo transcurrido en color fijo
    - Registro automático en CSV con línea total
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
        self._hubo_error = False
        self.console = Console()

        # Ruta del main
        try:
            self.ruta_main = str(Path(__main__.__file__).resolve())
        except AttributeError:
            self.ruta_main = "INTERACTIVO"

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
            fila_resumen = [
                fecha_hora,
                self.execution_id,
                estado_total,
                "TOTAL",
                mensaje,
                dur_total,
                self.ruta_main
            ]
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(fila_resumen)

        # Imprimir en consola
        color = "red" if self._hubo_error else "green"
        self.console.print(f"[bold {color}][{self.execution_id}] [{dur_total}] {mensaje} ({estado_total})[/bold {color}]")

    # Método interno
    def _log(self, nivel, mensaje):
        icono = self.ICONOS.get(nivel, "")
        color = self.COLORES.get(nivel, "white")
        
        hora_actual = datetime.now().strftime("%H:%M:%S")
        elapsed = time.perf_counter() - self.start_time

        # Formato con ceros iniciales
        if elapsed < 60:
            ts_rel = f"{elapsed:06.3f}s"
        else:
            minutos = int(elapsed // 60)
            segundos = int(elapsed % 60)
            decimales = elapsed % 1
            ts_rel = f"{minutos}m {segundos + decimales:06.3f}s"

        # Parte fija con color gris neutro
        parte_fija = f"[grey70][{self.execution_id}] [{hora_actual}] [{ts_rel}][/grey70]"

        # Parte mensaje con icono y color según nivel
        parte_mensaje = f"[{color}] {icono} {mensaje}[/{color}]"

        msg_rich = f"{parte_fija} {parte_mensaje}"

        # Log en consola según nivel
        if nivel in ("STEP", "INFO", "SUCCESS"):
            self.logger.info(msg_rich)
        elif nivel == "WARNING":
            self.logger.warning(msg_rich)
        elif nivel == "ERROR":
            self.logger.error(msg_rich)
            self._hubo_error = True

        # Guardar en CSV
        if self.csv_path:
            estado = "OK" if nivel != "ERROR" else "KO"
            fila = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.execution_id,
                estado,
                nivel,
                mensaje,
                ts_rel,
                self.ruta_main
            ]
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(fila)