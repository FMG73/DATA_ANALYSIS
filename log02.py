import csv
import time
import logging
import tkinter as tk
import winsound
from datetime import datetime
from pathlib import Path
from functools import wraps
import __main__

from rich.console import Console
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler

console = Console()


# =========================================================
# ALERTA TKINTER + SONIDO
# =========================================================

def alerta_tkinter(estado, script):

    # =========================
    # SONIDO
    # =========================
    if estado == "OK":
        for _ in range(2):
            winsound.Beep(1500, 250)
            time.sleep(0.1)
    else:
        for _ in range(4):
            winsound.Beep(800, 400)
            time.sleep(0.1)

    # =========================
    # VENTANA TKINTER
    # =========================
    ventana = tk.Tk()
    ventana.title("Ejecución script")
    ventana.geometry("400x180")
    ventana.resizable(False, False)
    ventana.attributes("-topmost", True)

    color = "green" if estado == "OK" else "red"

    label = tk.Label(
        ventana,
        text=f"{estado} - {script}",
        font=("Segoe UI", 20, "bold"),
        fg=color
    )
    label.pack(pady=40)

    boton = tk.Button(
        ventana,
        text="Cerrar",
        command=ventana.destroy,
        font=("Segoe UI", 12)
    )
    boton.pack()

    ventana.mainloop()


# =========================================================
# LOGGER BASE
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
        "SUCCESS": "✓"
    }

    COLORES = {
        "STEP": "blue",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "SUCCESS": "green",
        "TIMESTAMP": "blue"
    }

    RUN_COUNTER = 0

    def __init__(self, nombre="SCRIPT", csv_path="log_ejecuciones.csv"):

        self.logger = crear_logger(nombre)
        self.console = console
        self.start_time = time.perf_counter()
        self._hubo_error = False

        self.execution_id = f"RUN_{ScriptLogger.RUN_COUNTER:03d}"
        ScriptLogger.RUN_COUNTER += 1

        self.csv_path = Path(csv_path)

        try:
            self.ruta_main = str(Path(__main__.__file__).resolve())
        except AttributeError:
            self.ruta_main = "INTERACTIVO"

        self.nombre_script = Path(self.ruta_main).name

        self._init_csv()

    # -------------------------
    # CSV INIT
    # -------------------------
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
                    "SCRIPT"
                ])

    # -------------------------
    # CSV WRITE
    # -------------------------
    def _write_csv(self, tipo, mensaje, duracion):

        estado = "KO" if self._hubo_error else "OK"

        fila = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.execution_id,
            estado,
            tipo,
            mensaje,
            duracion,
            self.nombre_script
        ]

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f, delimiter=";")
            writer.writerow(fila)

    # -------------------------
    # LOG CORE
    # -------------------------
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

    # -------------------------
    # API PUBLICA
    # -------------------------
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


# =========================================================
# DECORADOR PRINCIPAL
# =========================================================

def ejecutar_con_log(spinner=True, alerta=True):

    def decorador(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            logger = ScriptLogger()

            nombre_script = logger.nombre_script

            # =========================
            # INICIO
            # =========================
            console.print(
                f"\n[bold magenta]"
                f"━━━━━━━━━━━━━━ INICIO SCRIPT {nombre_script} ━━━━━━━━━━━━━━"
                f"[/bold magenta]\n"
            )

            inicio_total = time.perf_counter()

            try:

                if spinner:

                    with Progress(
                        SpinnerColumn(),
                        TextColumn("{task.description}"),
                        console=console,
                        transient=True
                    ) as progress:

                        progress.add_task(
                            f"Ejecutando {func.__name__}..."
                        )

                        resultado = func(logger, *args, **kwargs)

                else:

                    resultado = func(logger, *args, **kwargs)

                ok = True

            except Exception as e:

                logger.error(str(e))
                resultado = None
                ok = False

            # =========================
            # FIN
            # =========================
            duracion = time.perf_counter() - inicio_total
            estado = "OK" if ok else "KO"

            console.print("\n")

            color = "green" if ok else "red"

            console.print(
                f"[bold {color}]"
                f"▣ FIN {estado} SCRIPT {nombre_script}"
                f"[/bold {color}]"
            )

            console.print(
                f"[bold]Duración total:[/bold] {duracion:.2f}s"
            )

            console.print(
                f"[bold]Execution ID:[/bold] {logger.execution_id}"
            )

            console.print("\n")

            # =========================
            # ALERTA TKINTER
            # =========================
            if alerta:
                alerta_tkinter(estado, nombre_script)

            return resultado

        return wrapper

    return decorador


# =========================================================
# PROTECCION MODULO
# =========================================================

if __name__ == "__main__":
    print("log3 es un módulo. Importalo desde otro script.")