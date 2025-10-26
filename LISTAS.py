import tkinter as tk
from tkinter import messagebox

# ===================== ESTILOS POR MARCA =====================
# Configuración de colores, fuentes, barra y espacio para cada marca
estilos = {
    "KIA": {"color_texto": "red", "fuente": ("Arial", 18, "bold"),
            "color_barra": "red", "altura_barra": 4, "espacio_barra": 10},
    "HYUNDAI": {"color_texto": "blue", "fuente": ("Helvetica", 18, "italic"),
                "color_barra": "blue", "altura_barra": 6, "espacio_barra": 15},
    "VOLVO": {"color_texto": "black", "fuente": ("Verdana", 18, "bold"),
              "color_barra": "darkgray", "altura_barra": 4, "espacio_barra": 12},
    "JLR": {"color_texto": "green", "fuente": ("Calibri", 18, "bold"),
            "color_barra": "green", "altura_barra": 5, "espacio_barra": 10}
}

# ===================== FUNCIONES =====================

def confirmar_cierre(root):
    """Confirma al usuario si quiere cerrar cualquier ventana."""
    if messagebox.askyesno("Confirmar salida", "¿Quieres cerrar?"):
        root.destroy()
        quit()  # Termina todo el script

def seleccionar_marcas():
    """Ventana inicial para seleccionar una o varias marcas."""
    seleccionadas = []

    root = tk.Tk()
    root.title("Selección de marcas")
    root.geometry("500x350")
    root.configure(bg="lightgray")
    root.protocol("WM_DELETE_WINDOW", lambda: confirmar_cierre(root))

    tk.Label(root, text="Por favor selecciona tipo de marca:",
             font=("Arial", 14, "bold"), bg="lightgray").pack(pady=20)

    marcas = ["KIA", "HYUNDAI", "VOLVO", "JLR"]
    vars_marcas = {m: tk.BooleanVar() for m in marcas}
    for m in marcas:
        tk.Checkbutton(root, text=m, variable=vars_marcas[m],
                       font=("Arial", 12), bg="lightgray").pack(anchor="w", padx=50)

    def aceptar():
        nonlocal seleccionadas
        seleccionadas = [m for m, v in vars_marcas.items() if v.get()]
        if not seleccionadas:
            messagebox.showwarning("Atención", "Debes seleccionar al menos una marca.")
            return
        root.destroy()

    tk.Button(root, text="Aceptar", command=aceptar, bg="lightblue", font=("Arial", 12)).pack(pady=30)
    root.mainloop()
    return seleccionadas

def ventana_marca(marca):
    """Ventana para introducir los datos de una marca específica."""
    datos = {}

    root = tk.Tk()
    root.title(f"Datos para {marca}")
    root.geometry("500x350")
    root.configure(bg="lightgray")
    root.protocol("WM_DELETE_WINDOW", lambda: confirmar_cierre(root))

    # Estilos
    estilo = estilos.get(marca, {})
    color_texto = estilo.get("color_texto", "black")
    fuente = estilo.get("fuente", ("Arial", 18, "bold"))
    color_barra = estilo.get("color_barra", "black")
    altura_barra = estilo.get("altura_barra", 4)
    espacio_barra = estilo.get("espacio_barra", 10)

    # Nombre de marca + barra
    tk.Label(root, text=marca, font=fuente, fg=color_texto, bg="lightgray").pack(pady=(20,0))
    barra = tk.Frame(root, bg=color_barra, height=altura_barra)
    barra.pack(fill="x", pady=(espacio_barra,20))

    # Campos de entrada con validación de longitud
    campos = {
        "lista_exclusiva": {"label": "Número lista exclusiva (6 caracteres):", "longitud": 6},
        "lista_abierta": {"label": "Número lista abierta (6 caracteres):", "longitud": 6},
        "fecha_fin": {"label": "Fecha fin de lista (yyyymmdd - 8 caracteres):", "longitud": 8}
    }

    entries = {}
    for key, info in campos.items():
        frame = tk.Frame(root, bg="lightgray")
        frame.pack(pady=5)
        tk.Label(frame, text=info["label"], bg="lightgray").pack(side="left", padx=5)
        entry = tk.Entry(frame)
        entry.pack(side="left")
        entries[key] = entry

    def guardar():
        for key, info in campos.items():
            valor = entries[key].get().strip()
            if len(valor) != info["longitud"] or (key != "fecha_fin" and not valor.isalnum()) or (key == "fecha_fin" and not valor.isdigit()):
                messagebox.showerror(
                    "Error de validación",
                    f"{info['label']} debe tener exactamente {info['longitud']} caracteres válidos."
                )
                return
            datos[key] = valor
        root.destroy()

    tk.Button(root, text="Guardar", command=guardar, bg="lightgreen").pack(pady=20)
    root.mainloop()
    return datos

def ejecutar_formulario():
    """Función principal que abre la ventana de selección y luego las ventanas por marca."""
    seleccionadas = seleccionar_marcas()
    print("\nMarcas seleccionadas:", seleccionadas)

    resultados = {}
    for marca in seleccionadas:
        datos_marca = ventana_marca(marca)
        resultados[marca] = datos_marca

    print("\n=== DATOS INGRESADOS POR MARCA ===")
    for marca, datos in resultados.items():
        print(f"{marca}: {datos}")

    return resultados

# ===================== LLAMADA INICIAL =====================
if __name__ == "__main__":
    datos_finales = ejecutar_formulario()

    # ===================== BLOQUE DE IF POR MARCA =====================
    for marca, datos in datos_finales.items():
        if marca == "VOLVO":
            print(f"\nEjecutando acciones para Volvo con datos: {datos}")
            # Coloca aquí el código específico para Volvo

        elif marca == "KIA":
            print(f"\nEjecutando acciones para Kia con datos: {datos}")
            # Coloca aquí el código específico para Kia

        elif marca == "HYUNDAI":
            print(f"\nEjecutando acciones para Hyundai con datos: {datos}")
            # Coloca aquí el código específico para Hyundai

        elif marca == "JLR":
            print(f"\nEjecutando acciones para JLR con datos: {datos}")
            # Coloca aquí el código específico para JLR