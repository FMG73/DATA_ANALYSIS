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
import __main__

console = Console()

def alerta_top_usuario(estado="OK", nombre_archivo="", nombre_funcion="", cerrar_auto=False, delay_cierre=5):
    """
    Muestra ventana Tkinter opcional al terminar la ejecución.
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

    texto_info = f"{estado.upper()} EJECUCION {nombre_archivo} - FUNCION: {nombre_funcion}"

    if cerrar_auto:
        lbl_mensaje = tk.Label(ventana, text=texto_info, font=("Segoe UI", 25, "bold"), fg=color, justify="center")
        lbl_mensaje.pack(pady=(20, 10))
        lbl_contador = tk.Label(ventana, text="", font=("Segoe UI", 72, "bold"), fg=color, justify="center")
        lbl_contador.pack()
        def actualizar_contador(segundos_restantes):
            if segundos_restantes > 0:
                lbl_contador.config(text=f"{segundos_restantes}")
                ventana.after(1000, actualizar_contador, segundos_restantes - 1)
            else:
                ventana.destroy()
        actualizar_contador(int(delay_cierre))
    else:
        etiqueta = tk.Label(ventana, text=texto_info, font=("Segoe UI", 25, "bold"), justify="left", padx=20, pady=5, fg=color)
        etiqueta.pack()
        btn_cerrar = tk.Button(
            ventana, text="CERRAR\nVENTANA", font=("Segoe UI", 25, "bold"),
            bg=color, fg="white", padx=5, pady=5,
            activebackground='lime' if estado.upper() == "OK" else 'salmon',
            activeforeground='black', cursor='hand2',
            command=ventana.destroy
        )
        btn_cerrar.pack(pady=1)
    ventana.mainloop()


def ejecutar_con_log(mostrar_alerta=True, cerrar_auto=False, delay_cierre=5):
    """
    Decorador que registra la ejecución de la función main, muestra alertas opcionales
    y registra en CSV/logs OK/KO con duración total.
    """

    # Configuración global de logging
    ruta_decorador = Path(__file__).name
    logger = logging.getLogger()
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        consola = RichHandler(rich_tracebacks=True, markup=True, show_time=False, show_level=False, show_path=False)
        logger.addHandler(consola)

    log_ok = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL_OK.log"
    log_ko = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL_KO.log"
    nombre_csv = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL.csv"

    def guardar_en_archivo(nombre_archivo, fecha, nivel, mensaje):
        with open(nombre_archivo, 'a', encoding='utf-8') as f:
            f.write(f"{fecha} - {nivel} - {mensaje}\n")

    def guardar_en_csv(nombre_csv, fecha, estado, nivel, mensaje, duracion=""):
        with open(nombre_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([fecha, estado, nivel, mensaje, duracion])

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Intentamos obtener el main
            try:
                nombre_archivo_main = Path(__main__.__file__).stem
            except AttributeError:
                nombre_archivo_main = "INTERACTIVO"
            nombre_funcion_main = func.__name__

            # Inicio decorador
            fecha_inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            mensaje_inicio = f"DECORADOR {ruta_decorador} INICIADO - EJECUTANDO FUNCION {nombre_funcion_main} DEL MAIN {nombre_archivo_main}"
            console.print(f"[bold magenta]{mensaje_inicio.upper()}[/bold magenta]")
            logger.info(mensaje_inicio.upper())
            guardar_en_archivo(log_ok, fecha_inicio, 'INFO', mensaje_inicio.upper())
            guardar_en_csv(nombre_csv, fecha_inicio, 'OK', 'INFO', mensaje_inicio.upper())

            inicio_tiempo = time.perf_counter()

            # Ejecución función
            try:
                console.print(f"[bold blue]EJECUTANDO FUNCION {nombre_funcion_main} DESDE {nombre_archivo_main}[/bold blue]")
                resultado = func(*args, **kwargs)
                ok = True
            except Exception as e:
                ok = False
                mensaje_error = f"ERROR EJECUCION FUNCION {nombre_funcion_main} MAIN {nombre_archivo_main}: {str(e).upper()}"
                fecha_error = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                console.print(f"[bold red]{mensaje_error}[/bold red]")
                logger.error(mensaje_error)
                guardar_en_archivo(log_ko, fecha_error, 'ERROR', mensaje_error)
                guardar_en_csv(nombre_csv, fecha_error, 'KO', 'ERROR', mensaje_error)

            fin_tiempo = time.perf_counter()
            duracion_total = fin_tiempo - inicio_tiempo
            duracion_txt = f"{int(duracion_total//60)}m {duracion_total%60:.2f}s" if duracion_total >= 60 else f"{duracion_total:.3f}s"

            # Fin OK
            if ok:
                fecha_fin = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                mensaje_fin = f"FUNCION {nombre_funcion_main} FINALIZADA OK - DURACION {duracion_txt}"
                console.print(f"[bold magenta]{mensaje_fin}[/bold magenta]")
                logger.info(mensaje_fin.upper())
                guardar_en_archivo(log_ok, fecha_fin, 'INFO', mensaje_fin.upper())
                guardar_en_csv(nombre_csv, fecha_fin, 'OK', 'INFO', mensaje_fin.upper(), duracion_txt)

            # Alerta Tkinter opcional
            if mostrar_alerta:
                alerta_top_usuario(
                    estado="OK" if ok else "KO",
                    nombre_archivo=nombre_archivo_main,
                    nombre_funcion=nombre_funcion_main,
                    cerrar_auto=cerrar_auto,
                    delay_cierre=delay_cierre
                )

            return resultado if ok else None

        return wrapper
    return decorador