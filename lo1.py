import csv
import time
import logging
import tkinter as tk
import winsound
import threading
import random
import string
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
# LOGGER BASE
# =========================================================

def crear_logger(nombre="script_logger", nivel=logging.DEBUG):

    logger = logging.getLogger(nombre)
    logger.setLevel(nivel)
    logger.propagate = False

    if not any(isinstance(h, RichHandler) for h in logger.handlers):

        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_level=False,
            show_path=False
        )

        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    return logger


# =========================================================
# SCRIPT LOGGER CORE
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
        "TIME": "blue"
    }

    def __init__(self, nombre="SCRIPT", csv_path="log.csv"):

        self.logger = crear_logger(nombre)
        self.console = console

        # tiempos globales
        self._start_global = time.perf_counter()
        self.start_time = self._start_global

        # estado global
        self._hubo_error_global = False
        self._last_error = None

        self.csv_path = Path(csv_path)

        # script name
        try:
            self.script_name = Path(__main__.__file__).name
        except Exception:
            self.script_name = "INTERACTIVE"

        # =====================================================
        # EXECUTION ID PRO
        # =====================================================
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        random_suffix = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=4)
        )

        self.execution_id = f"{self.script_name.replace('.py','').upper()}_{timestamp}_{random_suffix}"

        # spinner state
        self._spinner_task = "Iniciando..."

        self._init_csv()

    # =====================================================
    # SPINNER STATE
    # =====================================================

    def _set_task(self, msg: str):
        self._spinner_task = msg

    # =====================================================
    # LOG API
    # =====================================================

    def step(self, msg):
        self._set_task(msg)
        self._log("STEP", msg)

    def info(self, msg):
        self._set_task(msg)
        self._log("INFO", msg)

    def warning(self, msg):
        self._set_task(msg)
        self._log("WARNING", msg)

    def success(self, msg):
        self._set_task(msg)
        self._log("SUCCESS", msg)

    def error(self, msg):
        self._set_task(msg)
        self._hubo_error_global = True
        self._last_error = msg
        self._log("ERROR", msg)

    # =====================================================
    # LOG CORE (RICH FIX)
    # =====================================================

    def _log(self, tipo, msg):

        elapsed = time.perf_counter() - self.start_time
        rel = f"{elapsed:.3f}s"

        text = Text()

        text.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ",
            style=self.COLORES["TIME"]
        )

        text.append(
            f"{self.ICONOS[tipo]} ",
            style=self.COLORES[tipo]
        )

        text.append(
            f"[{tipo}] ",
            style=self.COLORES[tipo]
        )

        text.append(msg, style="white")

        text.append(
            f" ({rel})",
            style=self.COLORES["TIME"]
        )

        self.console.print(text)

    # =====================================================
    # CSV (1 SOLO RESULTADO FINAL)
    # =====================================================

    def write_final_csv(self):

        duration = time.perf_counter() - self._start_global

        estado = "KO" if self._hubo_error_global else "OK"

        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        file_exists = self.csv_path.exists()

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f, delimiter=";")

            if not file_exists:
                writer.writerow([
                    "FECHA",
                    "EXECUTION_ID",
                    "ESTADO",
                    "DURACION",
                    "SCRIPT",
                    "ERROR"
                ])

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.execution_id,
                estado,
                f"{duration:.2f}s",
                self.script_name,
                self._last_error or ""
            ])

    # =====================================================
    # CSV INIT (solo estructura)
    # =====================================================

    def _init_csv(self):
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)


# =========================================================
# ALERTA FINAL TKINTER
# =========================================================

def alerta_tkinter(logger: ScriptLogger):

    estado = "KO" if logger._hubo_error_global else "OK"
    color = "green" if estado == "OK" else "red"

    if estado == "OK":
        for _ in range(2):
            winsound.Beep(1500, 250)
            time.sleep(0.1)
    else:
        for _ in range(4):
            winsound.Beep(800, 350)
            time.sleep(0.1)

    ventana = tk.Tk()
    ventana.title("Ejecución final")
    ventana.geometry("420x180")
    ventana.attributes("-topmost", True)

    tk.Label(
        ventana,
        text=f"{estado} - {logger.script_name}",
        font=("Segoe UI", 20, "bold"),
        fg=color
    ).pack(pady=40)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack()

    ventana.mainloop()


# =========================================================
# DECORADOR
# =========================================================

def ejecutar_con_log(spinner=True, alerta=True):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            logger = ScriptLogger()
            script = logger.script_name

            console.print(
                f"\n[bold magenta]"
                f"━━━━━━━━━━━━━━ INICIO SCRIPT {script} ━━━━━━━━━━━━━━"
                f"[/bold magenta]\n"
            )

            start = time.perf_counter()
            finished = False

            def spinner_worker(progress, task_id):

                while not finished:
                    progress.update(
                        task_id,
                        description=f"Ejecutando {logger._spinner_task}"
                    )
                    time.sleep(0.1)

            try:

                if spinner:

                    with Progress(
                        SpinnerColumn(),
                        TextColumn("{task.description}"),
                        console=console,
                        transient=True
                    ) as progress:

                        task_id = progress.add_task("Iniciando...")

                        t = threading.Thread(
                            target=spinner_worker,
                            args=(progress, task_id),
                            daemon=True
                        )
                        t.start()

                        result = func(logger, *args, **kwargs)

                        finished = True
                        t.join()

                else:
                    result = func(logger, *args, **kwargs)

                ok = True

            except Exception as e:

                logger.error(str(e))
                result = None
                ok = False
                finished = True

            # FINAL WRITE
            logger.write_final_csv()

            console.print("\n")
            color = "green" if ok else "red"

            console.print(
                f"[bold {color}]▣ FIN {'OK' if ok else 'KO'} SCRIPT {script}[/bold {color}]"
            )

            console.print(f"Execution ID: {logger.execution_id}\n")

            if alerta:
                alerta_tkinter(logger)

            return result

        return wrapper

    return decorator


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":
    print("log3 FINAL listo ✔")