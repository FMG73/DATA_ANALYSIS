# melloger/script_logger_prd.py
import logging
from pathlib import Path
from datetime import datetime
import csv
import time
import uuid
from rich.console import Console

class ScriptLogger:
    ICONOS = {
        "STEP": "▶",
        "INFO": "🛈",
        "WARNING": "⚠",
        "ERROR": "✖",
        "SUCCESS": "✔",
        "TOTAL": "∑"
    }

    COLORES = {
        "STEP": "cyan",
        "INFO": "white",
        "WARNING": "yellow",
        "ERROR": "red",
        "SUCCESS": "green",
        "TOTAL": "magenta"
    }

    def __init__(self, nombre_logger="LOGGER", csv_path=None):
        self.logger = logging.getLogger(nombre_logger)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.hasHandlers():
            from rich.logging import RichHandler
            console_handler = RichHandler(rich_tracebacks=True)
            formatter = logging.Formatter("%(message)s")
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        self.console = Console()
        self.csv_path = csv_path
        self.execution_id = f"RUN_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.start_time = time.perf_counter()
        self.ruta_main = Path(__main__.__file__).resolve() if hasattr(__main__, "__file__") else "INTERACTIVO"
        self._hubo_error = False
        self._hubo_warning = False

        # Crear CSV con cabecera si no existe
        if self.csv_path and not Path(self.csv_path).exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["FECHA_HORA", "EXECUTION_ID", "ESTADO", "NIVEL", "MENSAJE", "DURACION", "RUTA_MAIN", "TOTAL"])

    def _log(self, nivel, mensaje):
        # Marcar errores/warnings
        if nivel.upper() == "ERROR":
            self._hubo_error = True
        if nivel.upper() == "WARNING":
            self._hubo_warning = True

        icono = self.ICONOS.get(nivel.upper(), "?")
        color = self.COLORES.get(nivel.upper(), "white")
        elapsed = time.perf_counter() - self.start_time
        hora_actual = datetime.now().strftime("%H:%M:%S")
        ts_rel = f"{elapsed:06.3f}s" if elapsed < 60 else f"{int(elapsed//60)}m {int(elapsed%60):02d}.{int((elapsed%1)*1000):03d}s"
        parte_fija = f"[grey70][{self.execution_id}] [{hora_actual}] [{ts_rel}][/grey70]"
        parte_mensaje = f"[{color}]{icono} {mensaje}[/{color}]"
        msg_rich = f"{parte_fija} {parte_mensaje}"

        self.logger.info(msg_rich)

        # Guardar en CSV si definido
        if self.csv_path:
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            estado = "KO" if nivel.upper() in ["ERROR", "WARNING"] else "OK"
            fila = [fecha_hora, self.execution_id, estado, nivel.upper(), mensaje, ts_rel, str(self.ruta_main), False]
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(fila)

    # Métodos públicos
    def step(self, mensaje): self._log("STEP", mensaje)
    def info(self, mensaje): self._log("INFO", mensaje)
    def warning(self, mensaje): self._log("WARNING", mensaje)
    def error(self, mensaje): self._log("ERROR", mensaje)
    def success(self, mensaje): self._log("SUCCESS", mensaje)

    def fin_script(self, mensaje="FIN SCRIPT"):
        fin_total = time.perf_counter()
        duracion_total = fin_total - self.start_time
        if duracion_total < 60:
            dur_total = f"{duracion_total:.3f}s"
        else:
            min_total = int(duracion_total // 60)
            sec_total = duracion_total % 60
            dur_total = f"{min_total}m {sec_total:.1f}s"

        estado_total = "KO" if self._hubo_error or self._hubo_warning else "OK"
        icono_total = self.ICONOS.get("TOTAL", "∑")
        color_total = self.COLORES.get("TOTAL", "magenta")

        # Construir línea Rich
        hora_actual = datetime.now().strftime("%H:%M:%S")
        elapsed = time.perf_counter() - self.start_time
        ts_rel = f"{elapsed:06.3f}s" if elapsed < 60 else f"{int(elapsed//60)}m {int(elapsed%60):02d}.{int((elapsed%1)*1000):03d}s"
        parte_fija = f"[grey70][{self.execution_id}] [{hora_actual}] [{ts_rel}][/grey70]"
        parte_mensaje = f"[{color_total}]{icono_total} {mensaje} ({estado_total})[/{color_total}]"
        msg_rich = f"{parte_fija} {parte_mensaje}"

        self.logger.info(msg_rich)

        # CSV TOTAL
        if self.csv_path:
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fila_total = [fecha_hora, self.execution_id, estado_total, "TOTAL", mensaje, ts_rel, str(self.ruta_main), True]
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(fila_total)