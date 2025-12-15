import tkinter as tk

def elegir_tipo_descarga():
    resultado = {"modo": None}

    def seleccionar_manual():
        resultado["modo"] = "manual"
        root.destroy()

    def seleccionar_automatica():
        resultado["modo"] = "automatica"
        root.destroy()

    root = tk.Tk()
    root.title("Tipo de descarga")
    root.geometry("300x150")

    label = tk.Label(root, text="¿Qué tipo de descarga quieres?")
    label.pack(pady=10)

    btn_manual = tk.Button(root, text="Descarga manual", command=seleccionar_manual)
    btn_manual.pack(pady=5)

    btn_auto = tk.Button(root, text="Descarga automática", command=seleccionar_automatica)
    btn_auto.pack(pady=5)

    root.mainloop()

    return resultado["modo"]