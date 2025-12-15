import tkinter as tk
import sys

ANCHO_BOTON = 10

def elegir_tipo_descarga():
    resultado = {"modo": None}

    def cerrar_ventana():
        print("cuadro terminado")
        root.destroy()
        sys.exit()

    def seleccionar_manual():
        resultado["modo"] = "manual"
        root.destroy()

    def seleccionar_automatica():
        resultado["modo"] = "automatica"
        root.destroy()

    root = tk.Tk()
    root.title("Tipo de descarga")
    root.geometry("300x160")

    root.protocol("WM_DELETE_WINDOW", cerrar_ventana)

    label = tk.Label(root, text="¿Qué tipo de descarga quieres?")
    label.pack(pady=8)

    barra = tk.Frame(root, bg="yellow", height=4)
    barra.pack(fill="x", pady=(0, 10))

    # Cursor tipo mano
    btn_manual = tk.Button(
        root,
        text="Descarga manual",
        width=ANCHO_BOTON,
        command=seleccionar_manual,
        cursor="hand2"
    )
    btn_manual.pack(pady=5)

    # Cursor diferente (cruz)
    btn_auto = tk.Button(
        root,
        text="Descarga automática",
        width=ANCHO_BOTON,
        command=seleccionar_automatica,
        cursor="cross"
    )
    btn_auto.pack(pady=5)

    root.mainloop()

    return resultado["modo"]