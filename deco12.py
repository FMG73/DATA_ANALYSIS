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
import uuid

# ----------------------- TKINTER ALERTAS -----------------------
def alerta_top_usuario(estado="OK", nombre_archivo="", nombre_funcion="", cerrar_auto=False, delay_cierre=5):
    """
    MUESTRA UNA VENTANA TKINTER CON ALERTA DE EJECUCION.

    PARAMETROS
    ----------
    estado : str
        "OK" o "KO". Define color de encabezado y cantidad de beeps.
    nombre_archivo : str
        Nombre del archivo principal que ejecuta la función.
    nombre_funcion : str
        Nombre de la función ejecutada desde main.
    cerrar_auto : bool
        True → cierra automáticamente después de delay_cierre segundos
        False → espera click del usuario
    delay_cierre : int
        Segundos antes de cerrar automáticamente si cerrar_auto=True
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

# ----------------------- DECORADOR PRINCIPAL -----------------------
def ejecutar_con_log(mostrar_alerta=True, cerrar_auto=False, delay_cierre=5):
    """
    Decorador para registrar ejecucion de funciones y mostrar alerta opcional.
    Diseñado para decorar solo el main, pero permite trazabilidad de funciones internas.

    PARAMS
    ------
    mostrar_alerta : bool
        True → mostrar ventana Tkinter al final
    cerrar_auto : bool
        True → cierra automáticamente ventana Tkinter
    delay_cierre : int
        Segundos antes de cerrar ventana si cerrar_auto=True
    """

    # Configuración global de logging con Rich
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

    def guardar_en_csv(nombre_csv, fecha, estado, nivel, mensaje, duracion="", id_ejecucion=""):
        fila = [fecha, estado, nivel, mensaje, duracion, id_ejecucion]
        with open(nombre_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(fila)

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generamos un ID de ejecución único para todo el main
            id_ejecucion = str(uuid.uuid4())

            # Nombre del main y ruta
            try:
                ruta_archivo_main = Path(__main__.__file__).resolve()
                nombre_archivo_main = Path(__main__.__file__).stem
            except AttributeError:
                ruta_archivo_main = "INTERACTIVO"
                nombre_archivo_main = "INTERACTIVO"

            nombre_funcion_main = func.__name__

            inicio_total = datetime.now()
            fecha_inicio = inicio_total.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # --- LOG: inicio main ---
            mensaje_inicio = (
                f"SCRIPT {nombre_archivo_main} INICIADO\n"
                f"RUTA COMPLETA: {ruta_archivo_main}\n"
                f"FUNCION MAIN: {nombre_funcion_main}\n"
                f"DECORADOR: {ruta_decorador}\n"
                f"ID EJECUCION: {id_ejecucion}"
            )
            logger.info(f"[bold magenta]{mensaje_inicio}[/bold magenta]")
            guardar_en_csv(nombre_csv, fecha_inicio, "OK", "INFO", mensaje_inicio, id_ejecucion=id_ejecucion)

            try:
                resultado = func(*args, **kwargs)
                ok = True
            except Exception as e:
                ok = False
                mensaje_error = f"ERROR EJECUCION FUNCION {nombre_funcion_main} MAIN {nombre_archivo_main}: {str(e)}"
                fecha_error = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logger.error(f"[bold red]{mensaje_error}[/bold red]")
                guardar_en_archivo(log_ko, fecha_error, 'ERROR', mensaje_error)
                guardar_en_csv(nombre_csv, fecha_error, 'KO', 'ERROR', mensaje_error, id_ejecucion=id_ejecucion)
                resultado = None

            # --- LOG: fin main ---
            fin_total = datetime.now()
            duracion = (fin_total - inicio_total).total_seconds()
            duracion_formato = f"{duracion:.3f}s"
            fecha_fin = fin_total.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            if ok:
                mensaje_fin = f"FIN OK SCRIPT {nombre_archivo_main}\nDURACION: {duracion_formato}"
                logger.info(f"[bold green]{mensaje_fin}[/bold green]")
                guardar_en_csv(nombre_csv, fecha_fin, 'OK', 'INFO', mensaje_fin, duracion_formato, id_ejecucion)
                guardar_en_archivo(log_ok, fecha_fin, 'INFO', mensaje_fin)
            else:
                mensaje_fin = f"FIN KO SCRIPT {nombre_archivo_main}\nDURACION: {duracion_formato}"
                logger.error(f"[bold red]{mensaje_fin}[/bold red]")
                guardar_en_csv(nombre_csv, fecha_fin, 'KO', 'ERROR', mensaje_fin, duracion_formato, id_ejecucion)
                guardar_en_archivo(log_ko, fecha_fin, 'ERROR', mensaje_fin)

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