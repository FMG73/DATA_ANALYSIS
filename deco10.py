import logging
from pathlib import Path
from datetime import datetime
import csv
from functools import wraps
import time
import winsound
import tkinter as tk
from rich.logging import RichHandler
import __main__
from rich.console import Console

console = Console()

def alerta_top_usuario(estado="OK", nombre_archivo="", nombre_funcion="", cerrar_auto=False, delay_cierre=5):
    """Muestra una ventana Tkinter con alerta de ejecución"""
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

    texto_info = f"{estado.upper()} EJECUCION {nombre_archivo} - FUNCION: {nombre_funcion}"

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


def ejecutar_con_log(mostrar_alerta=True, cerrar_auto=False, delay_cierre=5):
    """Decorador para registrar ejecución de funciones y mostrar alerta opcional"""

    ruta_decorador = Path(__file__).name
    logger = logging.getLogger()
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
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
            # NOMBRE DEL MAIN Y FUNCION
            try:
                nombre_archivo_main = Path(__main__.__file__).stem
            except AttributeError:
                nombre_archivo_main = "INTERACTIVO"
            nombre_funcion_main = func.__name__

            # LOG Y CONSOLA: inicio decorador
            fecha_inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            mensaje_decorador = f"INICIO DECORADOR {ruta_decorador}"
            console.print(f"[bold magenta]{mensaje_decorador}[/bold magenta]")
            logger.info(mensaje_decorador.upper())
            guardar_en_archivo(log_ok, fecha_inicio, "INFO", mensaje_decorador.upper())
            guardar_en_csv(nombre_csv, fecha_inicio, "OK", "INFO", mensaje_decorador.upper())

            # LOG Y CONSOLA: inicio función main
            mensaje_inicio = f"INICIO FUNCION {nombre_funcion_main} DESDE MAIN {nombre_archivo_main}"
            console.print(f"[bold blue]{mensaje_inicio}[/bold blue]")
            logger.info(mensaje_inicio.upper())
            guardar_en_archivo(log_ok, fecha_inicio, "INFO", mensaje_inicio.upper())
            guardar_en_csv(nombre_csv, fecha_inicio, "OK", "INFO", mensaje_inicio.upper())

            # EJECUCION FUNCION Y MEDICION TIEMPO
            inicio = time.perf_counter()
            try:
                resultado = func(*args, **kwargs)
                ok = True
            except Exception as e:
                ok = False
                resultado = None
                mensaje_error = f"ERROR FUNCION {nombre_funcion_main.upper()} MAIN {nombre_archivo_main.upper()}: {str(e).upper()}"
                fecha_error = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                console.print(f"[bold red]{mensaje_error}[/bold red]")
                logger.error(mensaje_error)
                guardar_en_archivo(log_ko, fecha_error, "ERROR", mensaje_error)
                guardar_en_csv(nombre_csv, fecha_error, "KO", "ERROR", mensaje_error)

            fin = time.perf_counter()
            duracion = f"{fin - inicio:.3f}s"

            # LOG Y CONSOLA: fin función main
            if ok:
                fecha_fin = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                mensaje_fin = f"FINALIZACION FUNCION {nombre_funcion_main} MAIN {nombre_archivo_main} OK DURACION {duracion}"
                console.print(f"[bold green]{mensaje_fin}[/bold green]")
                logger.info(mensaje_fin.upper())
                guardar_en_archivo(log_ok, fecha_fin, "INFO", mensaje_fin.upper())
                guardar_en_csv(nombre_csv, fecha_fin, "OK", "INFO", mensaje_fin.upper(), duracion)

            # ALERTA TKINTER OPCIONAL
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