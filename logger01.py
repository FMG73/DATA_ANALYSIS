import logging
from pathlib import Path
from datetime import datetime
import csv
from functools import wraps
import time
import uuid
import winsound
import tkinter as tk
from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
import rich.box
import __main__

console = Console()

# ----------------------------
# LOGGER
# ----------------------------

logger = logging.getLogger("mi_app")
logger.setLevel(logging.DEBUG)
logger.propagate = False

if not logger.hasHandlers():

    handler = RichHandler(
        rich_tracebacks=True,
        show_time=True,
        show_level=True,
        show_path=False,
        level_styles={
            "DEBUG": "dim cyan",
            "INFO": "cyan",
            "WARNING": "yellow",
            "ERROR": "bold red",
            "CRITICAL": "bold magenta"
        },
    )

    logger.addHandler(handler)

# ----------------------------
# CSV CONFIG
# ----------------------------

CSV_PATH = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL.csv"

# ----------------------------
# CSV WRITER
# ----------------------------

def guardar_en_csv(fila):

    existe = Path(CSV_PATH).exists()

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f, delimiter=";")

        if not existe:
            writer.writerow([
                "execution_id",
                "timestamp",
                "script",
                "funcion",
                "fase",
                "estado",
                "duracion",
                "mensaje"
            ])

        writer.writerow(fila)

# ----------------------------
# ALERTA TKINTER
# ----------------------------

def alerta_top_usuario(estado="OK", nombre_archivo="", nombre_funcion="", cerrar_auto=False, delay_cierre=5):

    beeps = 2 if estado.upper() == "OK" else 4

    for _ in range(beeps):
        winsound.Beep(1500, 300)
        time.sleep(0.1)

    ventana = tk.Tk()
    ventana.title(f"EJECUCION {estado.upper()} {nombre_archivo}")
    ventana.geometry("850x220")
    ventana.attributes("-topmost", True)

    color = "green" if estado.upper() == "OK" else "red"

    texto_info = f"{estado.upper()} EJECUCION {nombre_archivo}\nFUNCION: {nombre_funcion}"

    label = tk.Label(
        ventana,
        text=texto_info,
        font=("Segoe UI", 25, "bold"),
        fg=color
    )

    label.pack(pady=30)

    if cerrar_auto:
        ventana.after(delay_cierre * 1000, ventana.destroy)

    ventana.mainloop()

# ----------------------------
# DECORADOR FUNCION
# ----------------------------

def medir_tiempo_funcion(nombre=None):

    def decorador(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            inicio = time.perf_counter()

            resultado = func(*args, **kwargs)

            duracion = time.perf_counter() - inicio

            nombre_func = nombre or func.__name__

            logger.info(f"⏱️ {nombre_func} → {duracion:.3f}s")

            # guardar csv

            guardar_en_csv([
                execution_id_global,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                script_global,
                nombre_func,
                "FUNCION",
                "OK",
                f"{duracion:.3f}",
                "FUNCION EJECUTADA"
            ])

            # métricas ejecución

            metricas_global["n_funciones"] += 1

            if duracion > metricas_global["duracion_max"]:
                metricas_global["duracion_max"] = duracion
                metricas_global["funcion_max"] = nombre_func

            return resultado

        return wrapper

    return decorador

# ----------------------------
# DECORADOR SCRIPT
# ----------------------------

def ejecutar_con_log(mostrar_alerta=True, cerrar_auto=False, delay_cierre=5, spinner_style="dots"):

    def decorador(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            global execution_id_global
            global script_global
            global metricas_global

            execution_id_global = str(uuid.uuid4())

            try:
                ruta_archivo_main = Path(__main__.__file__).resolve()
                script_global = Path(__main__.__file__).stem
            except:
                script_global = "INTERACTIVO"

            metricas_global = {
                "n_funciones": 0,
                "duracion_max": 0,
                "funcion_max": ""
            }

            inicio = time.perf_counter()

            error_msg = ""

            logger.info(f"=== INICIO SCRIPT {script_global} ===")

            panel_inicio = Panel(
                Align(f"SCRIPT: {script_global}", align="left"),
                border_style="magenta",
                box=rich.box.DOUBLE
            )

            console.print(panel_inicio)

            try:

                with Progress(
                    SpinnerColumn(spinner_name=spinner_style),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:

                    progress.add_task(f"Ejecutando {script_global}...", total=None)

                    resultado = func(*args, **kwargs)

                ok = True

            except Exception as e:

                ok = False
                error_msg = str(e)

                logger.error(f"ERROR SCRIPT: {error_msg}")

            duracion_total = time.perf_counter() - inicio

            # guardar resumen script

            guardar_en_csv([
                execution_id_global,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                script_global,
                "SCRIPT_TOTAL",
                "RESUMEN",
                "OK" if ok else "KO",
                f"{duracion_total:.3f}",
                f"funciones={metricas_global['n_funciones']} | funcion_lenta={metricas_global['funcion_max']}"
            ])

            # panel final

            if ok:

                logger.info(f"FIN OK SCRIPT {script_global}")

                panel_fin = Panel(
                    Align(
                        f"DURACION TOTAL: {duracion_total:.3f}s\n"
                        f"FUNCIONES: {metricas_global['n_funciones']}\n"
                        f"FUNCION MAS LENTA: {metricas_global['funcion_max']}",
                        align="left"
                    ),
                    border_style="green",
                    box=rich.box.HEAVY
                )

            else:

                panel_fin = Panel(
                    Align(
                        f"ERROR: {error_msg}",
                        align="left"
                    ),
                    border_style="red",
                    box=rich.box.HEAVY
                )

            console.print(panel_fin)

            if mostrar_alerta:

                alerta_top_usuario(
                    estado="OK" if ok else "KO",
                    nombre_archivo=script_global,
                    nombre_funcion=func.__name__,
                    cerrar_auto=cerrar_auto,
                    delay_cierre=delay_cierre
                )

            return resultado

        return wrapper

    return decorador