import logging
from pathlib import Path
from datetime import datetime
import csv
import __main__
from functools import wraps
import inspect
import time
import winsound
import tkinter as tk

from rich.logging import RichHandler


def alerta_top_usuario(estado="OK", nombre_barra=None, cerrar_auto=False, delay_cierre=5):
    """
    MUESTRA UNA VENTANA TKINTER CON ALERTA DE EJECUCION.

    PARAMETROS
    ----------
    estado : str
        "OK" o "KO". Define color de encabezado y beeps.
    nombre_barra : str | None
        Nombre que aparecerá en la barra de la ventana. Si None, usa nombre del script.
    cerrar_auto : bool
        True → cierra automáticamente después de delay_cierre segundos
        False → espera click del usuario
    delay_cierre : int
        Segundos antes de cerrar automáticamente si cerrar_auto=True
    """

    caller_frame = inspect.stack()[1]
    if nombre_barra is None:
        nombre_barra = Path(caller_frame.filename).resolve().stem

    # SONIDO
    beeps = 2 if estado.upper() == "OK" else 4
    for _ in range(beeps):
        winsound.Beep(1500, 300)
        time.sleep(0.1)

    ventana = tk.Tk()
    ventana.title(f"EJECUCION {estado.upper()} {nombre_barra}")
    ventana.geometry("850x220")
    ventana.resizable(False, False)
    ventana.attributes("-topmost", True)

    color = "green" if estado.upper() == "OK" else "red"

    encabezado = tk.Frame(ventana, bg=color, height=20)
    encabezado.pack(fill='x')

    texto_info = f"{estado.upper()} EJECUCION {nombre_barra}"

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
        - Inicio de ejecución
        - Fin OK o KO
        - Guardar logs en consola, CSV y archivo

    TODOS LOS MENSAJES SE IMPRIMEN EN MAYUSCULAS.
    """

    ruta_script = Path(__main__.__file__).name

    # Configuracion logger
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

    nombre_csv = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL.csv"
    log_ok = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL_OK.log"
    log_ko = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL_KO.log"

    def guardar_en_archivo(nombre_archivo, fecha, nivel, mensaje):
        linea = f"{fecha} - {ruta_script} - {nivel} - {mensaje}\n"
        with open(nombre_archivo, 'a', encoding='utf-8') as f:
            f.write(linea)

    def guardar_en_csv(nombre_csv, fecha, estado, nivel, mensaje):
        fila = [fecha, ruta_script, estado, nivel, mensaje]
        with open(nombre_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(fila)

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # INICIO
            mensaje_inicio = "INICIO EJECUCION OK REGISTRADA EN LOGGER"
            fecha_inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            logger.info(mensaje_inicio)
            guardar_en_archivo(log_ok, fecha_inicio, 'INFO', mensaje_inicio)
            guardar_en_csv(nombre_csv, fecha_inicio, 'OK', 'INFO', mensaje_inicio)

            try:
                resultado = func(*args, **kwargs)
                ok = True
            except Exception as e:
                ok = False
                mensaje_error = f"ERROR EJECUCION REGISTRADA EN LOGGER: {str(e).upper()}"
                fecha_error = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logger.error(mensaje_error)
                guardar_en_archivo(log_ko, fecha_inicio, 'INFO', mensaje_inicio)
                guardar_en_csv(nombre_csv, fecha_inicio, 'OK', 'INFO', mensaje_inicio)
                guardar_en_archivo(log_ko, fecha_error, 'ERROR', mensaje_error)
                guardar_en_csv(nombre_csv, fecha_error, 'KO', 'ERROR', mensaje_error)

            # FIN OK
            if ok:
                mensaje_fin = "EJECUCION OK FINALIZADA REGISTRADA EN LOGGER"
                fecha_fin = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logger.info(mensaje_fin)
                guardar_en_archivo(log_ok, fecha_fin, 'INFO', mensaje_fin)
                guardar_en_csv(nombre_csv, fecha_fin, 'OK', 'INFO', mensaje_fin)

            # ALERTA OPCIONAL
            if mostrar_alerta:
                alerta_top_usuario(
                    estado="OK" if ok else "KO",
                    cerrar_auto=cerrar_auto,
                    delay_cierre=delay_cierre
                )

            return ok
        return wrapper
    return decorador