# script_1.py
import tkinter as tk
import winsound
import time
import sys
from pathlib import Path

def alerta_ok_usuario(**kwargs):
    """
    Ventana de alerta flexible:
      - cerrar_auto=True → contador grande, sin botón
      - cerrar_auto=False → texto normal, botón grande
      - delay_cierre = segundos antes de cerrar automáticamente
      - script_name = nombre del script que llama
    """
    script_name = kwargs.get("script_name", None)
    cerrar_auto = kwargs.get("cerrar_auto", False)
    delay_cierre = kwargs.get("delay_cierre", 3)

    # Beep inicial
    for _ in range(2):
        winsound.Beep(1500, 300)
        time.sleep(0.1)

    ruta_main = Path(sys.argv[0]).resolve()
    texto_info = f"⚠️ OK EJECUCIÓN\n{ruta_main}"

    ventana = tk.Tk()
    ventana.title(f"EJECUCIÓN OK {script_name}")
    ventana.geometry("850x120")
    ventana.resizable(False, False)
    ventana.attributes("-topmost", True)

    if cerrar_auto:
        # Modo automático → contador grande y centrado
        lbl_contador = tk.Label(
            ventana,
            text="",
            font=("Segoe UI", 36, "bold"),
            fg="red",
            justify="center"
        )
        lbl_contador.pack(expand=True)

        def actualizar_contador(segundos_restantes):
            if segundos_restantes > 0:
                lbl_contador.config(text=f"{segundos_restantes}")
                ventana.after(1000, actualizar_contador, segundos_restantes - 1)
            else:
                ventana.destroy()

        actualizar_contador(int(delay_cierre))

    else:
        # Modo manual → texto normal + botón grande
        etiqueta = tk.Label(ventana, text=texto_info, font=("Segoe UI", 10),
                            justify="left", padx=20, pady=5)
        etiqueta.pack()

        btn_cerrar = tk.Button(
            ventana,
            text="CERRAR",
            font=("Segoe UI", 14, "bold"),
            bg="#f44336",
            fg="white",
            padx=20,
            pady=8,
            command=ventana.destroy
        )
        btn_cerrar.pack(pady=10)

    ventana.mainloop()