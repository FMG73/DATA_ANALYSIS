# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox
import os
import time
import shutil
import win32com.client as win32
from rich.console import Console
from rich.progress import Progress

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE COLORES Y FUENTES POR MARCA
# ─────────────────────────────────────────────────────────────────────────────
config_colores = {
    "KIA": {
        "color_titulo": "red",
        "color_barra": "darkred",
        "color_texto": "black",
        "fuente_titulo": ("Helvetica", 22, "bold"),
        "fuente_texto": ("Arial", 14),
        "fondo": "lightgrey",
        "altura_barra": 5,
        "espacio_titulo_barra": 10
    },
    "HYUNDAI": {
        "color_titulo": "blue",
        "color_barra": "navy",
        "color_texto": "black",
        "fuente_titulo": ("Helvetica", 22, "bold"),
        "fuente_texto": ("Arial", 14),
        "fondo": "lightgrey",
        "altura_barra": 5,
        "espacio_titulo_barra": 10
    },
    "VOLVO": {
        "color_titulo": "black",
        "color_barra": "gray",
        "color_texto": "black",
        "fuente_titulo": ("Helvetica", 22, "bold"),
        "fuente_texto": ("Arial", 14),
        "fondo": "lightgrey",
        "altura_barra": 5,
        "espacio_titulo_barra": 10
    },
    "JLR": {
        "color_titulo": "darkgreen",
        "color_barra": "green",
        "color_texto": "black",
        "fuente_titulo": ("Helvetica", 22, "bold"),
        "fuente_texto": ("Arial", 14),
        "fondo": "lightgrey",
        "altura_barra": 5,
        "espacio_titulo_barra": 10
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES TKINTER
# ─────────────────────────────────────────────────────────────────────────────
def confirmar_cierre():
    """Muestra mensaje antes de cerrar cualquier ventana."""
    if messagebox.askyesno("Confirmar cierre", "¿Quieres cerrar el programa?"):
        os._exit(0)

def abrir_ventana_seleccion_marcas():
    """Ventana para seleccionar una o varias marcas."""
    seleccionadas = []

    def continuar():
        seleccionadas[:] = [marca for marca, var in variables.items() if var.get()]
        if not seleccionadas:
            messagebox.showwarning("Atención", "Selecciona al menos una marca.")
        else:
            root.destroy()

    root = tk.Tk()
    root.title("Selección de marcas")
    root.geometry("500x350")
    root.configure(bg="lightgrey")
    root.protocol("WM_DELETE_WINDOW", confirmar_cierre)

    label = tk.Label(root, text="Por favor, selecciona tipo de marca:", 
                     bg="lightgrey", font=("Helvetica", 16, "bold"))
    label.pack(pady=20)

    variables = {}
    for marca in ["KIA", "HYUNDAI", "VOLVO", "JLR"]:
        var = tk.BooleanVar()
        tk.Checkbutton(root, text=marca, variable=var, bg="lightgrey",
                       font=("Arial", 14)).pack(anchor="w", padx=100)
        variables[marca] = var

    tk.Button(root, text="Continuar", command=continuar, font=("Arial", 14, "bold")).pack(pady=20)
    root.mainloop()
    return seleccionadas

def abrir_ventana_datos_marca(marca):
    """Ventana donde se introducen los datos de cada marca seleccionada."""
    config = config_colores[marca]
    datos = {}

    def validar_y_cerrar():
        exclusiva = entry_exclusiva.get().strip()
        abierta = entry_abierta.get().strip()
        fecha = entry_fecha.get().strip()

        if len(exclusiva) != 6 or not exclusiva.isalnum():
            messagebox.showerror("Error", "La lista exclusiva debe tener 6 caracteres.")
            return
        if len(abierta) != 6 or not abierta.isalnum():
            messagebox.showerror("Error", "La lista abierta debe tener 6 caracteres.")
            return
        if len(fecha) != 8 or not fecha.isdigit():
            messagebox.showerror("Error", "La fecha debe tener 8 dígitos (YYYYMMDD).")
            return

        datos["exclusiva"] = exclusiva
        datos["abierta"] = abierta
        datos["fecha"] = fecha
        ventana.destroy()

    ventana = tk.Tk()
    ventana.title(f"Datos para {marca}")
    ventana.geometry("500x350")
    ventana.configure(bg=config["fondo"])
    ventana.protocol("WM_DELETE_WINDOW", confirmar_cierre)

    # Título marca
    label_titulo = tk.Label(ventana, text=marca, fg=config["color_titulo"], bg=config["fondo"],
                            font=config["fuente_titulo"])
    label_titulo.pack(pady=(20, config["espacio_titulo_barra"]))

    # Barra separadora
    frame_barra = tk.Frame(ventana, bg=config["color_barra"], height=config["altura_barra"])
    frame_barra.pack(fill="x", pady=(0, 20))

    # Campos de entrada
    frame_campos = tk.Frame(ventana, bg=config["fondo"])
    frame_campos.pack(pady=10)

    fuente_texto = ("Arial", 14)
    fuente_entrada = ("Arial", 18)

    # Campo 1
    tk.Label(frame_campos, text="Número lista exclusiva:", font=fuente_texto,
             bg=config["fondo"], anchor="w").grid(row=0, column=0, sticky="w", pady=5, padx=(20, 5))
    entry_exclusiva = tk.Entry(frame_campos, font=fuente_entrada, width=10)
    entry_exclusiva.grid(row=0, column=1, sticky="w", pady=5)

    # Campo 2
    tk.Label(frame_campos, text="Número lista abierta:", font=fuente_texto,
             bg=config["fondo"], anchor="w").grid(row=1, column=0, sticky="w", pady=5, padx=(20, 5))
    entry_abierta = tk.Entry(frame_campos, font=fuente_entrada, width=10)
    entry_abierta.grid(row=1, column=1, sticky="w", pady=5)

    # Campo 3
    tk.Label(frame_campos, text="Fecha fin de lista (YYYYMMDD):", font=fuente_texto,
             bg=config["fondo"], anchor="w").grid(row=2, column=0, sticky="w", pady=5, padx=(20, 5))
    entry_fecha = tk.Entry(frame_campos, font=fuente_entrada, width=10)
    entry_fecha.grid(row=2, column=1, sticky="w", pady=5)

    tk.Button(ventana, text="Aceptar", command=validar_y_cerrar, font=("Arial", 14, "bold")).pack(pady=20)
    ventana.mainloop()
    return datos

def ejecutar_formulario():
    """Abre selección de marcas y luego pide datos para cada una."""
    marcas_seleccionadas = abrir_ventana_seleccion_marcas()
    seleccionadas = {}
    for marca in marcas_seleccionadas:
        seleccionadas[marca] = abrir_ventana_datos_marca(marca)

    # Mostrar resumen en consola
    print("\n=== DATOS CAPTURADOS ===")
    for marca, datos in seleccionadas.items():
        print(f"{marca}: {datos}")
    print("=========================\n")

    return seleccionadas

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────
def cerrar_powerpo(pres, cerrar=True, matar=True):
    time.sleep(5)
    pres.Save()
    if cerrar: pres.Close()
    if matar:
        win32.Dispatch("PowerPoint.Application").Quit()
        os.system("taskkill /f /im POWERPNT.exe")

def borrar_imagen(presentacion, num_diapo):
    slide = presentacion.Slides(num_diapo)
    for shape in list(slide.Shapes):
        if shape.Type == 13:
            shape.Delete()

def pegar_imagen(presentacion, num_diapo, ruta_imagen, izquierda, arriba):
    time.sleep(3)
    slide = presentacion.Slides(num_diapo)
    slide.Shapes.AddPicture(FileName=ruta_imagen, LinkToFile=False, SaveWithDocument=True,
                            Left=izquierda, Top=arriba)

def copiar_celda(wb, pres, hoja, slide, vinculos):
    hoja_inicio = wb.Sheets(hoja)
    destino = pres.Slides(slide)
    for objeto_ppt, celda_excel in vinculos.items():
        valor = str(hoja_inicio.Range(celda_excel).Value)
        for shape in destino.Shapes:
            if shape.Name == objeto_ppt:
                shape.TextFrame.TextRange.Text = valor
                break

def consola_barra(tiempo, color='green', mensaje='EN PROCESO...'):
    with Progress() as progress:
        task = progress.add_task(f"[{color}]{mensaje}", total=tiempo)
        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(1)

# ─────────────────────────────────────────────────────────────────────────────
# BLOQUE PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
imp_mensaje_inicial('REPORTE RESULTADO LISTAS EXCLUSIVAS')
console = Console()

# Ejecutar formulario y recoger datos
seleccionadas = ejecutar_formulario()

# Procesar cada marca seleccionada
for marca, datos in seleccionadas.items():
    lista_exclusiva = datos['exclusiva']
    lista_abierta = datos['abierta']
    fecha_subasta = datos['fecha']
    nombre_archivo = f'{fecha_subasta}_{marca}'

    mensaje_imprimir(f'INICIANDO PROCESO PARA {marca}')

    # Aquí sigue tu flujo completo (Excel, PowerPoint, PDF, correo)
    # Lo he omitido por brevedad, pero es el mismo bloque que ya tienes funcionando.
    # Puedes pegar aquí directamente desde "mensaje_imprimir('INICIANDO ESCRIBIR DATOS EN EXCEL')" 
    # hasta el final del proceso de envío de correo.

imp_mensaje_final('REPORTE RESULTADO LISTAS EXCLUSIVAS')