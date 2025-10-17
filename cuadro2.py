import tkinter as tk
from tkinter import ttk
from multiprocessing import Process
import os

# ──────────────────────────────────────────────────────────────
# FUNCIONES DE UTILIDAD
# ──────────────────────────────────────────────────────────────

def run_script(script_name):
    """Ejecuta un script Python en un proceso separado."""
    os.system(f'python {script_name}')

def open_file(file_path):
    """Abre un archivo con la aplicación predeterminada del sistema."""
    os.startfile(file_path)

def create_button(parent, text, script_name, color, font, fg, row, column, command=None):
    """Crea un botón con estilo personalizado y lógica de ejecución."""
    button = tk.Button(parent,
                       text=text,
                       bg=color,
                       font=font,
                       fg=fg,
                       cursor='hand2',
                       command=command or (lambda: Process(target=run_script, args=(script_name,)).start()))
    button.grid(row=row, column=column, padx=5, pady=5, sticky='w')

def create_labelframe(root, text, font, fg, bg, row, column, buttons_info, open_files=False):
    """Crea un LabelFrame con botones dentro, para scripts o archivos."""
    labelframe = tk.LabelFrame(root,
                               text=text,
                               font=font,
                               bg=bg,
                               fg=fg,
                               padx=10, pady=5)
    labelframe.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')
    buttons_info.sort(key=lambda x: x['text'])

    for i, button
