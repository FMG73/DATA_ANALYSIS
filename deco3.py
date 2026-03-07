import logging
from pathlib import Path
from datetime import datetime
import csv
from functools import wraps
import inspect
import time
import winsound
import tkinter as tk
from rich.logging import RichHandler

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
    """
    DECORADOR PARA REGISTRAR EJECUCION DE FUNCIONES Y MOSTRAR ALERTA OPCIONAL.

    PARAMETROS
    ----------
    mostrar_alerta : bool
        True → mostrar alerta Tkinter al terminar la función
        False → no mostrar ventana
    cerrar_auto : bool
        Si mostrar_alerta=True, indica si la ventana se cierra automáticamente
    delay_cierre : int
        Segundos antes de cerrar automáticamente si cerrar_auto=True

    DESCRIPCION
    -----------
    Envuelve cualquier función y registra:
        - Qué decorador se está ejecutando y dónde
        - Qué función del main se ejecuta y desde qué archivo
        - Inicio de ejecución
        - Fin OK o KO
        - Guardar logs en consola, CSV y archivo
    """

    # CONFIGURACION LOGGING
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

    def guardar_en_csv(nombre_csv, fecha, estado, nivel, mensaje):
        fila = [fecha, estado, nivel, mensaje]
        with open(nombre_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(fila)

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # IDENTIFICACION DEL MAIN CORRECTA
            caller_frame = None
            for frame_info in inspect.stack():
                if "decoradores" not in frame_info.filename:  # salto nuestro módulo util
                    caller_frame = frame_info
                    break
            nombre_archivo_main = Path(caller_frame.filename).resolve().name
            nombre_funcion_main = caller_frame.function

            # LOG: inicio
            mensaje_inicio = f"DECORADOR {ruta_decorador} INICIA FUNCION {func.__name__} DEL MAIN {nombre_funcion_main} EN {nombre_archivo_main}"
            fecha_inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            logger.info(mensaje_inicio.upper())
            guardar_en_archivo(log_ok, fecha_inicio, 'INFO', mensaje_inicio.upper())
            guardar_en_csv(nombre_csv, fecha_inicio, 'OK', 'INFO', mensaje_inicio.upper())

            try:
                resultado = func(*args, **kwargs)
                ok = True
            except Exception as e:
                ok = False
                mensaje_error = f"ERROR EJECUCION FUNCION {func.__name__.upper()} MAIN {nombre_funcion_main.upper()} EN {nombre_archivo_main.upper()}: {str(e).upper()}"
                fecha_error = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logger.error(mensaje_error)
                guardar_en_archivo(log_ko, fecha_error, 'ERROR', mensaje_error)
                guardar_en_csv(nombre_csv, fecha_error, 'KO', 'ERROR', mensaje_error)

            # LOG: fin
            if ok:
                mensaje_fin = f"DECORADOR {ruta_decorador} FINALIZA FUNCION {func.__name__} DEL MAIN {nombre_funcion_main} EN {nombre_archivo_main} OK"
                fecha_fin = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logger.info(mensaje_fin.upper())
                guardar_en_archivo(log_ok, fecha_fin, 'INFO', mensaje_fin.upper())
                guardar_en_csv(nombre_csv, fecha_fin, 'OK', 'INFO', mensaje_fin.upper())

            # ALERTA TKINTER OPCIONAL
            if mostrar_alerta:
                alerta_top_usuario(
                    estado="OK" if ok else "KO",
                    nombre_archivo=nombre_archivo_main,
                    nombre_funcion=nombre_funcion_main,
                    cerrar_auto=cerrar_auto,
                    delay_cierre=delay_cierre
                )

            return ok
        return wrapper
    return decorador