import logging
from pathlib import Path
from datetime import datetime
import csv
import time
import __main__
from rich.logging import RichHandler


class ScriptLogger:

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

    CABECERA = [
        "FECHA_HORA",
        "EXECUTION_ID",
        "ESTADO",
        "NIVEL",
        "MENSAJE",
        "DURACION",
        "RUTA_MAIN",
        "TOTAL"
    ]

    def __init__(self,
                 nombre_logger="PRD_LOGGER",
                 csv_path=r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL.csv",
                 ruta_execution_id=r"C:\REMARKETING\BI\30_LOG_PYTHON\execution_id.txt"):

        # Logger Rich
        self.logger = logging.getLogger(nombre_logger)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            handler = RichHandler(show_time=False, show_level=False)
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Inicio de ejecución
        self.start_time = time.perf_counter()

        # Generar execution ID global
        self.execution_id = self.generar_execution_id(ruta_execution_id)

        # CSV
        self.csv_path = Path(csv_path)

        # Ruta script
        try:
            self.ruta_main = str(Path(__main__.__file__).resolve())
        except:
            self.ruta_main = "INTERACTIVO"

        # Estados ejecución
        self._hubo_error = False
        self._hubo_warning = False

        # Contadores
        self._contador_step = 0
        self._contador_warning = 0
        self._contador_error = 0

        # Crear CSV si no existe
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:

            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:

                writer = csv.writer(f, delimiter=";")
                writer.writerow(self.CABECERA)

    # ---------------------------------------------------------

    def generar_execution_id(self, ruta_control):

        ruta = Path(ruta_control)

        if not ruta.exists():
            ruta.write_text("0")

        ultimo_id = int(ruta.read_text().strip())

        nuevo_id = ultimo_id + 1

        ruta.write_text(str(nuevo_id))

        return f"RUN_{nuevo_id:06d}"

    # ---------------------------------------------------------

    def _formatear_duracion(self, segundos):

        if segundos < 60:
            return f"{segundos:.3f}s"

        minutos = int(segundos // 60)
        resto = segundos % 60

        return f"{minutos}m {resto:.1f}s"

    # ---------------------------------------------------------

    def _log(self, nivel, mensaje):

        if nivel == "STEP":
            self._contador_step += 1

        if nivel == "WARNING":
            self._hubo_warning = True
            self._contador_warning += 1

        if nivel == "ERROR":
            self._hubo_error = True
            self._contador_error += 1

        elapsed = time.perf_counter() - self.start_time

        duracion = self._formatear_duracion(elapsed)

        hora = datetime.now().strftime("%H:%M:%S")

        icono = self.ICONOS[nivel]
        color = self.COLORES[nivel]

        linea = (
            f"[grey70][{self.execution_id}] [{hora}] [{duracion}][/grey70] "
            f"[{color}]{icono} {mensaje}[/{color}]"
        )

        self.logger.info(linea)

        estado = "KO" if nivel in ["ERROR", "WARNING"] else "OK"

        fila = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.execution_id,
            estado,
            nivel,
            mensaje,
            duracion,
            self.ruta_main,
            False
        ]

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f, delimiter=";")
            writer.writerow(fila)

    # ---------------------------------------------------------

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

    # ---------------------------------------------------------

    def fin_script(self, mensaje="FIN SCRIPT"):

        duracion_total = time.perf_counter() - self.start_time

        dur_total = self._formatear_duracion(duracion_total)

        estado_total = "KO" if (self._hubo_error or self._hubo_warning) else "OK"

        hora = datetime.now().strftime("%H:%M:%S")

        resumen = (
            f"{mensaje} | "
            f"STEPS={self._contador_step} | "
            f"WARNINGS={self._contador_warning} | "
            f"ERRORS={self._contador_error}"
        )

        linea = (
            f"[grey70][{self.execution_id}] [{hora}] [{dur_total}][/grey70] "
            f"[bold]FIN SCRIPT ({estado_total})[/bold] {resumen}"
        )

        self.logger.info(linea)

        fila_total = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.execution_id,
            estado_total,
            "TOTAL",
            resumen,
            dur_total,
            self.ruta_main,
            True
        ]

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f, delimiter=";")
            writer.writerow(fila_total)