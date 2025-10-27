# ─────────────────────────────────────────────────────────────────────────────
# SCRIPT INTEGRADO: SELECCIÓN DE DATOS + PROCESO EXCEL/POWERPOINT/ENVÍO MAIL
# ─────────────────────────────────────────────────────────────────────────────

import win32com.client as win32
import time
import os
import shutil
from rich.progress import Progress
from rich.console import Console
from rich.prompt import Prompt
from rich import print
from tkcalendar import DateEntry
import tkinter as tk
from tkinter import messagebox
from melvive.tableau import Tableau
from melvive.utilidades import EnvioCorreo
from melvive.funciones import mensaje_imprimir, imp_mensaje_inicial, imp_mensaje_final
from melvive.claseoffice import ExcelSensibilidad
from melvive.melero_config import MailDireccionesListas as mdl

# ─────────────────────────────────────────────────────────────────────────────
# RUTAS Y CONFIGURACIONES
# ─────────────────────────────────────────────────────────────────────────────
ruta_ataque_ppt = mdl.ruta_plantilla_ppt
ruta_ataque_xlsx = mdl.ruta_plantilla_xlsx
ruta_msg_outlook = mdl.ruta_plantilla_msg

ruta_imagenes_temp = mdl.ruta_almacen_imagenes
ruta_descarga_archivos = mdl.ruta_almacen_archivos

config_email_por_marca = mdl.partners_post

dashboard_tableau = 'PARTNERS_DEF'
dashboards_por_marca = {
    "VOLVO": {"VOLV_1": (dashboard_tableau, "VOLV_1"), "VOLV_2": (dashboard_tableau, "VOLV_2"), "VOLV_3": (dashboard_tableau, "VOLV_3")},
    "KIA": {"KIA_1": (dashboard_tableau, "KIA_1"), "KIA_2": (dashboard_tableau, "KIA_2"), "KIA_3": (dashboard_tableau, "KIA_3")},
    "HYUNDAI": {"HYU_1": (dashboard_tableau, "HYU_1"), "HYU_2": (dashboard_tableau, "HYU_2"), "HYU_3": (dashboard_tableau, "HYU_3")},
    "JLR": {"JLR_1": (dashboard_tableau, "JLR_1"), "JLR_2": (dashboard_tableau, "JLR_2"), "JLR_3": (dashboard_tableau, "JLR_3")}
}

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DEL FORMULARIO TKINTER
# ─────────────────────────────────────────────────────────────────────────────
estilos = {
    "Volvo": {"color": "#4a90e2", "fuente": ("Helvetica", 16, "bold")},
    "Kia": {"color": "#d32f2f", "fuente": ("Arial", 16, "bold")},
    "Hyundai": {"color": "#1976d2", "fuente": ("Calibri", 16, "bold")},
    "JLR": {"color": "#388e3c", "fuente": ("Verdana", 16, "bold")},
}

def abrir_ventana_seleccion_marcas():
    """Ventana para seleccionar las marcas que se van a procesar"""
    marcas = ["Volvo", "Kia", "Hyundai", "JLR"]
    seleccionadas = []

    root_sel = tk.Tk()
    root_sel.title("Selecciona las marcas")
    root_sel.geometry("500x350")
    root_sel.configure(bg="gray")

    label = tk.Label(root_sel, text="Por favor selecciona el tipo de marca:", bg="gray",
                     font=("Arial", 14, "bold"))
    label.pack(pady=20)

    vars_marcas = {}
    for marca in marcas:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(root_sel, text=marca, variable=var, bg="gray", font=("Arial", 12))
        chk.pack(anchor="w", padx=100)
        vars_marcas[marca] = var

    def continuar():
        seleccionadas.extend([m for m, v in vars_marcas.items() if v.get()])
        if not seleccionadas:
            messagebox.showwarning("Atención", "Debes seleccionar al menos una marca.")
            return
        root_sel.destroy()

    boton = tk.Button(root_sel, text="Continuar", command=continuar, bg="#4CAF50", fg="white",
                      font=("Arial", 12, "bold"))
    boton.pack(pady=20)

    def confirmar_cierre():
        if messagebox.askyesno("Confirmar salida", "¿Quieres cerrar el script?"):
            root_sel.destroy()
            exit()

    root_sel.protocol("WM_DELETE_WINDOW", confirmar_cierre)
    root_sel.mainloop()

    return seleccionadas

def abrir_ventana_datos_marca(marca):
    """Ventana para pedir los datos de lista exclusiva, abierta y fecha para cada marca"""
    datos = {}
    root = tk.Tk()
    root.title(f"Datos de lista {marca}")
    root.geometry("500x350")
    root.configure(bg="gray")

    def confirmar_cierre():
        if messagebox.askyesno("Confirmar salida", "¿Quieres cerrar el script?"):
            root.destroy()
            exit()

    root.protocol("WM_DELETE_WINDOW", confirmar_cierre)

    estilo = estilos.get(marca, {"color": "black", "fuente": ("Arial", 14)})

    label_marca = tk.Label(root, text=marca, fg=estilo["color"], bg="gray", font=estilo["fuente"])
    label_marca.pack(pady=(20, 10))

    barra = tk.Frame(root, bg=estilo["color"], height=5)
    barra.pack(fill="x", padx=20, pady=(0, 20))

    campos = [
        ("Número de lista exclusiva (6 caracteres)", "exclusiva"),
        ("Número de lista abierta (6 caracteres)", "abierta"),
        ("Fecha fin de lista (8 caracteres, formato yyyymmdd)", "fecha")
    ]

    entradas = {}

    for texto, clave in campos:
        label = tk.Label(root, text=texto, bg="gray", font=("Arial", 12), anchor="w", justify="left")
        label.pack(pady=(5, 0))

        if clave == "fecha":
            entry = DateEntry(root, date_pattern="yyyyMMdd", font=("Arial", 18), width=12)
        else:
            entry = tk.Entry(root, font=("Arial", 18), width=15)

        entry.pack(pady=(0, 10))
        entradas[clave] = entry

    def confirmar():
        ex = entradas["exclusiva"].get().strip()
        ab = entradas["abierta"].get().strip()
        fe = entradas["fecha"].get().strip()

        if len(ex) != 6 or not ex.isalnum():
            messagebox.showerror("Error", "La lista exclusiva debe tener 6 caracteres.")
            return
        if len(ab) != 6 or not ab.isalnum():
            messagebox.showerror("Error", "La lista abierta debe tener 6 caracteres.")
            return
        if len(fe) != 8 or not fe.isdigit():
            messagebox.showerror("Error", "La fecha debe tener 8 dígitos (yyyymmdd).")
            return

        datos["exclusiva"] = ex
        datos["abierta"] = ab
        datos["fecha"] = fe
        root.destroy()

    boton = tk.Button(root, text="Confirmar", command=confirmar, bg=estilo["color"],
                      fg="white", font=("Arial", 12, "bold"))
    boton.pack(pady=10)

    root.mainloop()
    return datos

def ejecutar_formulario():
    """Función principal del formulario que devuelve 'seleccionadas'"""
    marcas_seleccionadas = abrir_ventana_seleccion_marcas()  # se ejecuta solo 1 vez
    seleccionadas = {}
    for marca in marcas_seleccionadas:
        seleccionadas[marca] = abrir_ventana_datos_marca(marca)
    return seleccionadas

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES DEL SCRIPT ORIGINAL (EXCEL/POWERPOINT/MAIL)
# ─────────────────────────────────────────────────────────────────────────────
def pedir_input_fecha_dummy(): pass  # placeholder para compatibilidad
def iniciar_excel(ruta_excel, visible=True):
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = visible
    wb = excel.Workbooks.Open(ruta_excel)
    return wb

def cerrar_excel(wb, cerrar=True, matar=True):
    time.sleep(5)
    wb.Save()
    if cerrar: wb.Close()
    if matar:
        win32.Dispatch("Excel.Application").Quit()
        os.system("taskkill /f /im excel.exe")

def iniciar_powerpow(ruta_powerpo, visible=True):
    ppt = win32.Dispatch("PowerPoint.Application")
    ppt.Visible = visible
    pres = ppt.Presentations.Open(ruta_powerpo)
    return pres

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
    slide.Shapes.AddPicture(FileName=ruta_imagen, Link