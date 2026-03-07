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


def alerta_top_usuario(estado="OK", nombre_archivo="", nombre_funcion="", duracion=None,
                        cerrar_auto=False, delay_cierre=5):
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
    duracion : str | None
        Duración de la función formateada. Se muestra en la ventana si no es None.
    cerrar_auto : bool
        True → se cierra automáticamente después de delay_cierre segundos
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
    if duracion:
        texto_info += f" - DURACION: {duracion}"

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
    DECORADOR PARA REGISTRAR EJECUCION DE FUNCIONES, MOSTRAR ALERTA OPCIONAL
    Y MEDIR TIEMPO DE EJECUCION.

    PARAMETROS
    ----------
    mostrar_alerta : bool
        True → mostrar alerta Tkinter al terminar la función
        False → no mostrar ventana
    cerrar_auto : bool
        Si mostrar_alerta=True, indica si la ventana se cierra automáticamente
    delay_cierre : int
        Segundos antes de cerrar automáticamente si cerrar_auto=True
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

    def formatear_duracion(segundos):
        if segundos < 60:
            return f"{segundos:.3f}s"
        minutos = int(segundos // 60)
        resto = segundos % 60
        return f"{minutos}m {resto:.1f}s"

    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # NOMBRE DEL MAIN Y FUNCION
            try:
                nombre_archivo_main = Path(__main__.__file__).stem
            except AttributeError:
                nombre_archivo_main = "INTERACTIVO"

            nombre_funcion_main = func.__name__

            # LOG: inicio
            mensaje_inicio = f"DECORADOR {ruta_decorador} INICIA FUNCION {nombre_funcion_main} DEL MAIN {nombre_archivo_main}"
            fecha_inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            logger.info(mensaje_inicio.upper())
            guardar_en_archivo(log_ok, fecha_inicio, 'INFO', mensaje_inicio.upper())
            guardar_en_csv(nombre_csv, fecha_inicio, 'OK', 'INFO', mensaje_inicio.upper())

            # TIEMPO DE EJECUCION
            inicio = time.perf_counter()
            try:
                resultado = func(*args, **kwargs)
                ok = True
            except Exception as e:
                ok = False
                resultado = None
                mensaje_error = f"ERROR EJECUCION FUNCION {nombre_funcion_main.upper()} MAIN {nombre_archivo_main.upper()}: {str(e).upper()}"
                fecha_error = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logger.error(mensaje_error)
                guardar_en_archivo(log_ko, fecha_error, 'ERROR', mensaje_error)
                guardar_en_csv(nombre_csv, fecha_error, 'KO', 'ERROR', mensaje_error)

            fin = time.perf_counter()
            duracion = fin - inicio
            duracion_formateada = formatear_duracion(duracion)

            # LOG: fin
            if ok:
                mensaje_fin = f"DECORADOR {ruta_decorador} FINALIZA FUNCION {nombre_funcion_main} DEL MAIN {nombre_archivo_main} OK - DURACION {duracion_formateada}"
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
                    duracion=duracion_formateada,
                    cerrar_auto=cerrar_auto,
                    delay_cierre=delay_cierre
                )

            return resultado
        return wrapper
    return decorador