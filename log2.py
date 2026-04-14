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
        "TIME": "blue"
    }

    def __init__(self, nombre="SCRIPT", csv_path="log.csv"):

        self.logger = crear_logger(nombre)
        self.console = console

        self._start_global = time.perf_counter()
        self.start_time = self._start_global

        self._hubo_error_global = False
        self._last_error = None

        self.csv_path = Path(csv_path)

        try:
            self.script_name = Path(__main__.__file__).name
        except Exception:
            self.script_name = "INTERACTIVE"

        # EXECUTION ID PRO
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        random_suffix = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=4)
        )

        self.execution_id = f"{self.script_name.replace('.py','').upper()}_{timestamp}_{random_suffix}"

        self._spinner_task = "Iniciando..."

        self._init_csv()

    # =====================================================
    # LOG METHODS
    # =====================================================

    def _set_task(self, msg):
        self._spinner_task = msg

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
    # PRINT RICH
    # =====================================================

    def _log(self, tipo, msg):

        elapsed = time.perf_counter() - self.start_time
        rel = f"{elapsed:.3f}s"

        text = Text()

        text.append(f"[{datetime.now().strftime('%H:%M:%S')}] ", style=self.COLORES["TIME"])
        text.append(f"{self.ICONOS[tipo]} ", style=self.COLORES[tipo])
        text.append(f"[{tipo}] ", style=self.COLORES[tipo])
        text.append(msg, style="white")
        text.append(f" ({rel})", style=self.COLORES["TIME"])

        self.console.print(text)

    # =====================================================
    # CSV FINAL
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

    def _init_csv(self):
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)


# =========================================================
# TKINTER PRO (ESTILO ORIGINAL)
# =========================================================

def alerta_tkinter(logger, cerrar_auto=True, delay_cierre=5):

    estado = "KO" if logger._hubo_error_global else "OK"
    script = logger.script_name

    # SONIDO THREAD
    def sonido():
        beeps = 2 if estado == "OK" else 4
        freq = 1500 if estado == "OK" else 800

        for _ in range(beeps):
            winsound.Beep(freq, 300)
            time.sleep(0.1)

    threading.Thread(target=sonido, daemon=True).start()

    ventana = tk.Tk()
    ventana.title(f"EJECUCION {estado} {script}")
    ventana.geometry("850x220")
    ventana.resizable(False, False)
    ventana.attributes("-topmost", True)

    # CENTRAR
    ventana.update_idletasks()
    w = ventana.winfo_width()
    h = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (w // 2)
    y = (ventana.winfo_screenheight() // 2) - (h // 2)
    ventana.geometry(f"{w}x{h}+{x}+{y}")

    color = "green" if estado == "OK" else "red"

    encabezado = tk.Frame(ventana, bg=color, height=20)
    encabezado.pack(fill='x')

    texto_info = f"{estado} EJECUCION {script}"

    if cerrar_auto:

        lbl_mensaje = tk.Label(
            ventana,
            text=texto_info,
            font=("Segoe UI", 25, "bold"),
            fg=color
        )
        lbl_mensaje.pack(pady=(20, 10))

        lbl_contador = tk.Label(
            ventana,
            text="",
            font=("Segoe UI", 72, "bold"),
            fg=color
        )
        lbl_contador.pack()

        def actualizar(seg):
            if seg > 0:
                lbl_contador.config(text=str(seg))
                ventana.after(1000, actualizar, seg - 1)
            else:
                ventana.destroy()

        actualizar(delay_cierre)

    else:

        etiqueta = tk.Label(
            ventana,
            text=texto_info,
            font=("Segoe UI", 25, "bold"),
            fg=color
        )
        etiqueta.pack()

        btn = tk.Button(
            ventana,
            text="CERRAR\nVENTANA",
            font=("Segoe UI", 25, "bold"),
            bg=color,
            fg="white",
            command=ventana.destroy
        )
        btn.pack(pady=5)

    ventana.mainloop()


# =========================================================
# DECORADOR
# =========================================================

def ejecutar_con_log(
    spinner=True,
    alerta=True,
    cerrar_auto=True,
    delay_cierre=5
):

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

            logger.write_final_csv()

            console.print("\n")
            color = "green" if ok else "red"

            console.print(
                f"[bold {color}]▣ FIN {'OK' if ok else 'KO'} SCRIPT {script}[/bold {color}]"
            )

            console.print(f"Execution ID: {logger.execution_id}\n")

            if alerta:
                alerta_tkinter(
                    logger,
                    cerrar_auto=cerrar_auto,
                    delay_cierre=delay_cierre
                )

            return result

        return wrapper

    return decorator


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":
    print("log3 listo ✔")