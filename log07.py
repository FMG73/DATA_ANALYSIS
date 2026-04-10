import csv
import time
import logging
import tkinter as tk
import winsound
import threading
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
# ALERTA FINAL
# =========================================================

def alerta_tkinter(estado, script):

    if estado == "OK":
        for _ in range(2):
            winsound.Beep(1500, 250)
            time.sleep(0.1)
    else:
        for _ in range(4):
            winsound.Beep(800, 350)
            time.sleep(0.1)

    ventana = tk.Tk()
    ventana.title("Ejecución script")
    ventana.geometry("420x180")
    ventana.resizable(False, False)
    ventana.attributes("-topmost", True)

    color = "green" if estado == "OK" else "red"

    tk.Label(
        ventana,
        text=f"{estado} - {script}",
        font=("Segoe UI", 20, "bold"),
        fg=color
    ).pack(pady=40)

    tk.Button(
        ventana,
        text="Cerrar",
        command=ventana.destroy
    ).pack()

    ventana.mainloop()


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
# LOGGER PRINCIPAL
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

    RUN_COUNTER = 0

    def __init__(self, nombre="SCRIPT", csv_path="log.csv"):

        self.logger = crear_logger(nombre)
        self.console = console
        self.start_time = time.perf_counter()
        self._hubo_error = False

        self.execution_id = f"RUN_{ScriptLogger.RUN_COUNTER:03d}"
        ScriptLogger.RUN_COUNTER += 1

        self.csv_path = Path(csv_path)

        try:
            self.script_name = Path(__main__.__file__).name
        except Exception:
            self.script_name = "INTERACTIVE"

        self._current_task = ""   # 👈 SIEMPRE LIMPIO

        self._init_csv()

    # -------------------------
    # STEP (IMPORTANTE)
    # -------------------------
    def step(self, msg):

        self._current_task = msg   # 👈 spinner se actualiza aquí

        self._log("STEP", msg)

    def info(self, msg):
        self._log("INFO", msg)

    def warning(self, msg):
        self._log("WARNING", msg)

    def error(self, msg):
        self._log("ERROR", msg)
        self._hubo_error = True

    def success(self, msg):
        self._log("SUCCESS", msg)

    # -------------------------
    # LOG CORE
    # -------------------------
    def _log(self, tipo, msg):

        elapsed = time.perf_counter() - self.start_time
        rel = f"{elapsed:.3f}s"

        text = Text()
        text.append(f"[{datetime.now().strftime('%H:%M:%S')}] ", style=self.COLORES["TIME"])
        text.append(f"{self.ICONOS[tipo]} ", style=self.COLORES[tipo])
        text.append(f"[{tipo}] ", style=self.COLORES[tipo])
        text.append(msg)
        text.append(f" ({rel})", style=self.COLORES["TIME"])

        console.print(text)

        self._write_csv(tipo, msg, rel)

    # -------------------------
    # CSV
    # -------------------------
    def _init_csv(self):

        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.csv_path.exists():

            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:

                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "FECHA",
                    "EXECUTION_ID",
                    "ESTADO",
                    "TIPO",
                    "MENSAJE",
                    "DURACION",
                    "SCRIPT"
                ])

    def _write_csv(self, tipo, msg, duracion):

        estado = "KO" if self._hubo_error else "OK"

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:

            csv.writer(f, delimiter=";").writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.execution_id,
                estado,
                tipo,
                msg,
                duracion,
                self.script_name
            ])


# =========================================================
# DECORADOR
# =========================================================

def ejecutar_con_log(spinner=True, alerta=True):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            logger = ScriptLogger()

            logger._current_task = "Iniciando..."   # 👈 RESET GARANTIZADO

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
                        description=f"Ejecutando {logger._current_task}"
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

            # RESET FINAL (CRÍTICO)
            logger._current_task = ""

            duration = time.perf_counter() - start
            state = "OK" if ok else "KO"

            console.print("\n")
            color = "green" if ok else "red"

            console.print(
                f"[bold {color}]▣ FIN {state} SCRIPT {script}[/bold {color}]"
            )

            console.print(f"Duración total: {duration:.2f}s")
            console.print(f"Execution ID: {logger.execution_id}\n")

            if alerta:
                alerta_tkinter(state, script)

            return result

        return wrapper

    return decorator


# =========================================================
# PROTECCION
# =========================================================

if __name__ == "__main__":
    print("log3 module ready")