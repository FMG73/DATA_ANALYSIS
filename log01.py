import csv
import time
import logging
import tkinter as tk
from datetime import datetime
from pathlib import Path
from functools import wraps
import threading
import __main__

from rich.console import Console
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.align import Align
from rich.logging import RichHandler
import rich.box

console = Console()

# =========================================================
# LOGGER
# =========================================================

def crear_logger(nombre="script_logger", nivel=logging.DEBUG):

    logger = logging.getLogger(nombre)
    logger.setLevel(nivel)
    logger.propagate = False

    if not any(isinstance(h, RichHandler) for h in logger.handlers):

        rich_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_level=False,
            show_path=False
        )

        formatter = logging.Formatter("%(message)s")
        rich_handler.setFormatter(formatter)

        logger.addHandler(rich_handler)

    return logger


# =========================================================
# SCRIPT LOGGER
# =========================================================

class ScriptLogger:

    ICONOS = {
        "STEP": "→",
        "INFO": "⬤",
        "WARNING": "⚠",
        "ERROR": "⭙",
        "SUCCESS": "✓",
        "FIN": "▣"
    }

    COLORES = {
        "STEP": "blue",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "SUCCESS": "green",
        "FIN": "magenta",
        "TIMESTAMP": "blue"
    }

    RUN_COUNTER = 0

    def __init__(self, nombre="SCRIPT", csv_path="log_ejecuciones.csv"):

        self.logger = crear_logger(nombre)
        self.console = Console()
        self.start_time = time.perf_counter()
        self._hubo_error = False

        self.execution_id = f"RUN_{ScriptLogger.RUN_COUNTER:03d}"
        ScriptLogger.RUN_COUNTER += 1

        self.csv_path = Path(csv_path)

        try:
            self.ruta_main = str(Path(__main__.__file__).resolve())
        except AttributeError:
            self.ruta_main = "INTERACTIVO"

        self._nombre_archivo_main = Path(self.ruta_main).name

        self._init_csv()

    def _init_csv(self):

        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.csv_path.exists():

            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:

                writer = csv.writer(f, delimiter=";")

                writer.writerow([
                    "FECHA_HORA",
                    "EXECUTION_ID",
                    "ESTADO",
                    "NIVEL",
                    "MENSAJE",
                    "DURACION",
                    "RUTA_MAIN",
                    "SCRIPT"
                ])

    def _write_csv(self, tipo, mensaje, duracion):

        estado = "KO" if self._hubo_error else "OK"

        fila = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.execution_id,
            estado,
            tipo,
            mensaje,
            duracion,
            self.ruta_main,
            self._nombre_archivo_main
        ]

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f, delimiter=";")
            writer.writerow(fila)

    def _log(self, tipo, mensaje):

        elapsed = time.perf_counter() - self.start_time
        ts_rel = f"{elapsed:.3f}s"

        msg = Text()

        msg.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ",
            style=self.COLORES["TIMESTAMP"]
        )

        msg.append(f"{self.ICONOS[tipo]} ", style=self.COLORES[tipo])
        msg.append(f"[{tipo}] ", style=self.COLORES[tipo])
        msg.append(mensaje)
        msg.append(f" ({ts_rel})", style=self.COLORES["TIMESTAMP"])

        console.print(msg)

        self._write_csv(tipo, mensaje, ts_rel)

        if tipo == "ERROR":
            self._hubo_error = True

    def step(self, msg):
        self._log("STEP", msg)

    def info(self, msg):
        self._log("INFO", msg)

    def warning(self, msg):
        self._log("WARNING", msg)

    def error(self, msg):
        self._log("ERROR", msg)

    def success(self, msg):
        self._log("SUCCESS", msg)

    def fin_script(self, msg):
        self._log("FIN", msg)


# =========================================================
# ALERTA TKINTER
# =========================================================

def alerta_tkinter(estado="OK", script="SCRIPT"):

    ventana = tk.Tk()
    ventana.title(f"Ejecución {estado}")

    color = "green" if estado == "OK" else "red"

    label = tk.Label(
        ventana,
        text=f"{estado} - {script}",
        font=("Segoe UI", 24, "bold"),
        fg=color
    )

    label.pack(padx=40, pady=40)

    boton = tk.Button(
        ventana,
        text="Cerrar",
        command=ventana.destroy
    )

    boton.pack(pady=10)

    ventana.mainloop()


# =========================================================
# DECORADOR EJECUCION
# =========================================================

def ejecutar_con_log(
        usar_gui=False,
        mostrar_alerta=True,
        spinner=True):

    def decorador(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            logger = ScriptLogger()

            console.print(
                Panel(
                    Align(f"INICIO SCRIPT {logger._nombre_archivo_main}",
                          align="center"),
                    border_style="magenta",
                    box=rich.box.DOUBLE
                )
            )

            if spinner and not usar_gui:

                with Progress(
                        SpinnerColumn(),
                        TextColumn("{task.description}"),
                        console=console,
                        transient=True
                ) as progress:

                    task = progress.add_task(
                        f"Ejecutando {func.__name__}..."
                    )

                    resultado = func(logger, *args, **kwargs)

            else:

                resultado = func(logger, *args, **kwargs)

            logger.fin_script("SCRIPT FINALIZADO")

            console.print(
                Panel(
                    Align("FIN SCRIPT", align="center"),
                    border_style="green",
                    box=rich.box.HEAVY
                )
            )

            if mostrar_alerta and not usar_gui:

                estado = "KO" if logger._hubo_error else "OK"

                alerta_tkinter(
                    estado,
                    logger._nombre_archivo_main
                )

            return resultado

        return wrapper

    return decorador


# =========================================================
# GUI TKINTER
# =========================================================

def lanzar_gui(func):

    root = tk.Tk()
    root.title("EJECUTOR DE SCRIPT")
    root.geometry("400x200")

    label = tk.Label(
        root,
        text="Ejecutar Script",
        font=("Segoe UI", 18, "bold")
    )

    label.pack(pady=20)

    def run():

        threading.Thread(target=func).start()

    boton = tk.Button(
        root,
        text="EJECUTAR",
        font=("Segoe UI", 14),
        command=run
    )

    boton.pack(pady=10)

    root.mainloop()