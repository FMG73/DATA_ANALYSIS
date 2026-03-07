import time
import csv
import traceback
from pathlib import Path
from datetime import datetime
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
import rich.box
import tkinter as tk
import winsound

LOG_CSV = r"C:\REMARKETING\BI\30_LOG_PYTHON\PYTHON_CONTROL.csv"
console = Console()


def _guardar_csv(script_name, estado, mensaje, duracion=None):
    """Guarda el estado final del main en CSV"""
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    with open(LOG_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([fecha, script_name, estado, mensaje, duracion if duracion else ""])


def main_decorator(mostrar_tkinter=True, cierre_auto=True, delay_cierre=5):
    """
    Decorador para el main: controla ejecución, consola, CSV y Tkinter.

    :param mostrar_tkinter: Mostrar ventana de alerta al finalizar
    :param cierre_auto: Cierre automático de Tkinter si se muestra
    :param delay_cierre: Segundos antes de cerrar ventana automáticamente
    """
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ruta_main = Path(func.__module__ + ".py").stem  # nombre del main
            inicio = time.perf_counter()

            # Mensaje inicio en consola (magenta)
            longitud = len(ruta_main) + 10
            texto = f' SE INICIA MAIN {ruta_main} '
            console.print(
                Panel(Align(texto, align='center'),
                      border_style='magenta',
                      width=longitud + 10,
                      box=rich.box.DOUBLE)
            )

            # Beep inicial
            for _ in range(2):
                winsound.Beep(1500, 300)

            try:
                result = func(*args, **kwargs)
                fin = time.perf_counter()
                duracion = fin - inicio

                # Formateo para consola
                if duracion < 60:
                    duracion_txt = f"{duracion:.3f}s"
                else:
                    minutos = int(duracion // 60)
                    resto = duracion % 60
                    duracion_txt = f"{minutos}m {resto:.1f}s"

                # Mensaje fin OK en consola (verde)
                texto_fin = f' MAIN FINALIZADO OK → DURACIÓN {duracion_txt} '
                console.print(
                    Panel(Align(texto_fin, align='center'),
                          border_style='green',
                          width=len(texto_fin) + 10,
                          box=rich.box.DOUBLE)
                )

                # Guardar en CSV
                _guardar_csv(ruta_main, 'OK', 'MAIN FINALIZADO OK', round(duracion, 3))

                # Tkinter si se pidió
                if mostrar_tkinter:
                    _tkinter_ventana_ok(ruta_main, cierre_auto, delay_cierre)

                return result

            except Exception as e:
                fin = time.perf_counter()
                duracion = fin - inicio

                # Mensaje error en consola (rojo)
                texto_error = f' MAIN FINALIZADO KO → {str(e)} '
                console.print(
                    Panel(Align(texto_error, align='center'),
                          border_style='red',
                          width=len(texto_error) + 10,
                          box=rich.box.DOUBLE)
                )

                # Traceback visible
                console.print(traceback.format_exc())

                # Guardar en CSV
                _guardar_csv(ruta_main, 'KO', 'MAIN FINALIZADO KO', round(duracion, 3))

                # Tkinter KO
                if mostrar_tkinter:
                    _tkinter_ventana_ko(ruta_main, cierre_auto, delay_cierre)

                # Relanzar excepción si quieres que falle también en Python
                raise

        return wrapper
    return decorador


def _tkinter_ventana_ok(nombre_script, cierre_auto, delay_cierre):
    ventana = tk.Tk()
    ventana.title(f"EJECUCIÓN OK {nombre_script}")
    ventana.geometry("850x220")
    ventana.resizable(False, False)
    ventana.attributes("-topmost", True)

    # Beep y mensaje
    for _ in range(2):
        winsound.Beep(1500, 300)
    encabezado = tk.Frame(ventana, bg='green', height=20)
    encabezado.pack(fill='x')
    lbl = tk.Label(ventana, text=f"MAIN EJECUCIÓN OK {nombre_script}",
                   font=("Segoe UI", 25, "bold"), fg='green')
    lbl.pack(pady=(20, 10))

    if cierre_auto:
        lbl_cont = tk.Label(ventana, text="", font=("Segoe UI", 72, "bold"), fg="green")
        lbl_cont.pack()

        def actualizar_contador(seg_rest):
            if seg_rest > 0:
                lbl_cont.config(text=f"{seg_rest}")
                ventana.after(1000, actualizar_contador, seg_rest - 1)
            else:
                ventana.destroy()

        actualizar_contador(delay_cierre)
    else:
        btn = tk.Button(ventana, text="CERRAR\nVENTANA", font=("Segoe UI", 25, "bold"),
                        bg="green", fg="white", command=ventana.destroy)
        btn.pack(pady=10)

    ventana.mainloop()


def _tkinter_ventana_ko(nombre_script, cierre_auto, delay_cierre):
    ventana = tk.Tk()
    ventana.title(f"EJECUCIÓN KO {nombre_script}")
    ventana.geometry("850x220")
    ventana.resizable(False, False)
    ventana.attributes("-topmost", True)

    for _ in range(4):
        winsound.Beep(1500, 300)
    encabezado = tk.Frame(ventana, bg='red', height=20)
    encabezado.pack(fill='x')
    lbl = tk.Label(ventana, text=f"MAIN EJECUCIÓN KO {nombre_script}",
                   font=("Segoe UI", 25, "bold"), fg='red')
    lbl.pack(pady=(20, 10))

    if cierre_auto:
        lbl_cont = tk.Label(ventana, text="", font=("Segoe UI", 72, "bold"), fg="red")
        lbl_cont.pack()

        def actualizar_contador(seg_rest):
            if seg_rest > 0:
                lbl_cont.config(text=f"{seg_rest}")
                ventana.after(1000, actualizar_contador, seg_rest - 1)
            else:
                ventana.destroy()

        actualizar_contador(delay_cierre)
    else:
        btn = tk.Button(ventana, text="CERRAR\nVENTANA", font=("Segoe UI", 25, "bold"),
                        bg="red", fg="white", command=ventana.destroy)
        btn.pack(pady=10)
    ventana.mainloop()