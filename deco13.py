import logging
from pathlib import Path
from datetime import datetime
import csv
from functools import wraps
import time
import winsound
import tkinter as tk
from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
import rich.box
import __main__

console = Console()  # consola global

def alerta_top_usuario(estado="OK", nombre_archivo="", nombre_funcion="", cerrar_auto=False, delay_cierre=5):
    """
    Muestra una ventana Tkinter con alerta de ejecución.
    """
    beeps = 2 if estado.upper() == "OK" else 4
    for _ in range(beeps):
        winsound.Beep(1500, 300)
        time.sleep(0.1)

    ventana = tk.Tk()
    ventana.title(f"EJECUCION {estado.upper()} {nombre_archivo}")
    ventana.geometry("850x220")
    ventana.resizable(False, False)
    ventana.attributes("-topmost", True)

    color = "green" if estado.upper() == "OK" else "red"
    encabezado = tk.Frame(ventana, bg=color, height=20)
    encabezado.pack(fill='x')

    texto_info = f"{estado.upper()} EJECUCION {nombre_archivo}\nFUNCION: {nombre_funcion}"

    if cerrar_auto:
        lbl_mensaje = tk.Label(
            ventana,
            text=texto_info,
            font=("Segoe UI", 25, "bold"),
            fg=color,
            justify="center"
        )
        lbl_mensaje.pack(pady=(20, 10))

        lbl_contador = tk.Label(
            ventana,
            text="",
            font=("Segoe UI", 72, "bold"),
            fg=color,
            justify="center"
        )
        lbl_contador.pack()

        def actualizar_contador(segundos_restantes):
            if segundos_restantes > 0:
                lbl_contador.config(text=f"{segundos_restantes}")
                ventana.after(1000, actualizar_contador, segundos_restantes - 1)
            else:
                ventana.destroy()

        actualizar_contador(int(delay_cierre))
    else:
        etiqueta = tk.Label(
            ventana,
            text=texto_info,
            font=("Segoe UI", 25, "bold"),
            justify="left",
            padx=20,
            pady=5,
            fg=color
        )
        etiqueta.pack()

        btn_cerrar = tk.Button(
            ventana,
            text="CERRAR\nVENTANA",
            font=("Segoe UI", 25, "bold"),
            bg=color, fg="white",
            padx=5, pady=5,
            activebackground='lime' if estado.upper() == "OK" else 'salmon',
            activeforeground='black',
            cursor='hand2',
            command=ventana.destroy
        )
        btn_cerrar.pack(pady=1)

    ventana.mainloop()


def ejecutar_con_log(mostrar_alerta=True, cerrar_auto=False, delay_cierre=5, spinner_style="dots"):
    """
    Decorador para registrar ejecución de funciones y mostrar spinner + alerta opcional.
    """
    # Configuración logging Rich
    ruta_decorador = Path(__file__).name
    logger = logging.getLogger()
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        consola = RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_level=False,
            show_path=False
        )
        consola.setFormatter(formatter)
        logger.addHandler(consola)

    log_ok = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL_OK.log"
    log_ko = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL_KO.log"
    nombre_csv = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL.csv"

    def guardar_en_archivo(nombre_archivo, fecha, nivel, mensaje):
        linea = f"{fecha} - {nivel} - {mensaje}\n"
        with open(nombre_archivo, 'a', encoding='utf-8') as f:
            f.write(linea)

    def guardar_en_csv(nombre_csv, fecha, estado, nivel, mensaje, duracion=""):
        fila = [fecha, estado, nivel, mensaje, duracion]
        with open(nombre_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(fila)

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                ruta_archivo_main = Path(__main__.__file__).resolve()
                nombre_archivo_main = Path(__main__.__file__).stem
            except AttributeError:
                ruta_archivo_main = "INTERACTIVO"
                nombre_archivo_main = "INTERACTIVO"

            nombre_funcion_main = func.__name__
            inicio_total = datetime.now()
            fecha_inicio = inicio_total.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # PANEL INICIO
            panel_inicio = Panel(
                Align(f"SCRIPT {nombre_archivo_main} INICIADO\n"
                      f"RUTA: {ruta_archivo_main}\n"
                      f"FUNCION MAIN: {nombre_funcion_main}\n"
                      f"DECORADA POR: {ruta_decorador}",
                      align="center"),
                border_style="magenta",
                box=rich.box.DOUBLE,
                width=100
            )
            console.print(panel_inicio)
            logger.info(f"[bold magenta]SCRIPT {nombre_archivo_main} INICIADO[/bold magenta]")
            guardar_en_csv(nombre_csv, fecha_inicio, "OK", "INFO", f"SCRIPT {nombre_archivo_main} INICIADO")

            # Spinner durante la ejecución
            with Progress(
                SpinnerColumn(spinner_name=spinner_style, style="cyan"),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
                console=console
            ) as progress:
                task = progress.add_task(f"Ejecutando {nombre_funcion_main}...", start=False)
                progress.start_task(task)
                try:
                    resultado = func(*args, **kwargs)
                    ok = True
                except Exception as e:
                    ok = False
                    resultado = None
                    mensaje_error = f"ERROR EJECUCION FUNCION {nombre_funcion_main}"
                    fecha_error = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    logger.error(f"[bold red]{mensaje_error}[/bold red]\n{e}")
                    guardar_en_archivo(log_ko, fecha_error, 'ERROR', mensaje_error)
                    guardar_en_csv(nombre_csv, fecha_error, 'KO', 'ERROR', mensaje_error)

            # PANEL FIN
            fin_total = datetime.now()
            duracion = (fin_total - inicio_total).total_seconds()
            duracion_formato = f"{duracion:.3f}s"
            fecha_fin = fin_total.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            if ok:
                panel_fin = Panel(
                    Align(f"FIN OK SCRIPT {nombre_archivo_main}\n"
                          f"DURACION: {duracion_formato}",
                          align="center"),
                    border_style="green",
                    box=rich.box.HEAVY,
                    width=100
                )
                console.print(panel_fin)
                logger.info(f"[bold green]FIN OK SCRIPT {nombre_archivo_main}[/bold green]")
                guardar_en_csv(nombre_csv, fecha_fin, 'OK', 'INFO', f"FIN SCRIPT {nombre_archivo_main}", duracion_formato)
            else:
                panel_fin = Panel(
                    Align(f"FIN KO SCRIPT {nombre_archivo_main}\n"
                          f"DURACION: {duracion_formato}\n"
                          f"ERROR: {e}",
                          align="center"),
                    border_style="red",
                    box=rich.box.HEAVY,
                    width=100
                )
                console.print(panel_fin)
                logger.error(f"[bold red]FIN KO SCRIPT {nombre_archivo_main}[/bold red]")
                guardar_en_csv(nombre_csv, fecha_fin, 'KO', 'ERROR', f"FIN SCRIPT {nombre_archivo_main}", duracion_formato)

            # ALERTA TKINTER opcional
            if mostrar_alerta:
                alerta_top_usuario(
                    estado="OK" if ok else "KO",
                    nombre_archivo=nombre_archivo_main,
                    nombre_funcion=nombre_funcion_main,
                    cerrar_auto=cerrar_auto,
                    delay_cierre=delay_cierre
                )

            return resultado
        return wrapper
    return decorador