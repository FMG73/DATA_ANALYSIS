import tkinter as tk
from tkinter import ttk
from multiprocessing import Process
import os

# ──────────────────────────────────────────────────────────────
# FUNCIONES DE UTILIDAD
# ──────────────────────────────────────────────────────────────

# Ejecuta un script Python en un proceso separado
def run_script(script_name):
    os.system(f'python {script_name}')

# Abre un archivo con la aplicación predeterminada
def open_file(file_path):
    os.startfile(file_path)

# Crea un botón dentro de un contenedor
def create_button(parent, text, script_name, color, font, fg, row, column, command=None):
    button = tk.Button(parent,
                       text=text,
                       bg=color,
                       font=font,
                       fg=fg,
                       cursor='hand2',
                       command=command or (lambda: Process(target=run_script, args=(script_name,)).start()))
    button.grid(row=row, column=column, padx=5, pady=5, sticky='w')

# Crea un LabelFrame con botones dentro
def create_labelframe(root, text, font, fg, bg, row, column, buttons_info, open_files=False):
    labelframe = tk.LabelFrame(root,
                               text=text,
                               font=font,
                               bg=bg,
                               fg=fg,
                               padx=10, pady=5)
    labelframe.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')
    buttons_info.sort(key=lambda x: x['text'])

    for i, button_info in enumerate(buttons_info):
        command = (lambda file=button_info['file']: open_file(file)) if open_files else None
        create_button(labelframe,
                      text=button_info['text'],
                      script_name=button_info.get('script', ''),
                      color=button_info['color'],
                      font=button_info['font'],
                      fg=button_info['fg'],
                      row=i,
                      column=0,
                      command=command)
    return labelframe

# ──────────────────────────────────────────────────────────────
# INICIO DE LA INTERFAZ
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    root = tk.Tk()
    root.title('CUADRO MANDOS ENTREPRISE')
    root.iconbitmap(r'C:\LOGO_H_DIGI_RGB.ico')
    root.resizable(True, True)

    # Fuente base para los botones
    fuente_boton = ('Arial', 14)

    # ──────────────────────────────────────────────────────────────
    # CONFIGURACIÓN DE ESTILO PARA LAS PESTAÑAS
    # ──────────────────────────────────────────────────────────────

    style = ttk.Style()
    style.theme_use('default')  # Usa el tema base para permitir personalización

    # Estilo general de las pestañas
    style.configure('TNotebook.Tab',
                    font=('Arial', 12, 'bold'),
                    padding=[12, 6],
                    background='#034242',
                    foreground='white',
                    borderwidth=1)

    # Estilo dinámico para pestaña seleccionada
    style.map('TNotebook.Tab',
              background=[('selected', '#00915A')],
              foreground=[('selected', 'white')])

    # ──────────────────────────────────────────────────────────────
    # COLORES PERSONALIZADOS
    # ──────────────────────────────────────────────────────────────

    color1 = '#00915A'
    color2 = '#034242'
    color3 = '#05AF5A'
    color4 = '#98FF9B'
    color5 = '#F8B40D'
    color6 = '#EAE4CE'
    color7 = '#00BEF3'
    color8 = '#CAF868'
    color9 = '#3B3BDB'
    color10 = '#BEBEBE'
    color11 = '#000000'
    color12 = '#FFFFFF'
    color13 = 'red'
    color14 = 'yellow'

    # ──────────────────────────────────────────────────────────────
    # DEFINICIÓN DE FRAMES Y BOTONES
    # ──────────────────────────────────────────────────────────────

    frames_info = [
        {'name': '1', 'text': 'SCRIPTS',
         'font': ('TITLE SANS', 18, 'bold'), 'bg': color2, 'fg': color12, 'row': 0, 'column': 1},

        {'name': '2', 'text': 'OBIEE',
         'font': ('TITLE SANS', 18, 'bold'), 'bg': color2, 'fg': color12, 'row': 0, 'column': 0},

        {'name': '3', 'text': 'MOTORTRADE',
         'font': ('TITLE SANS', 18, 'bold'), 'bg': color2, 'fg': color12, 'row': 0, 'column': 0},

        {'name': '4', 'text': 'CONTROLES',
         'font': ('TITLE SANS', 18, 'bold'), 'bg': color2, 'fg': color12, 'row': 0, 'column': 1},

        {'name': '5', 'text': 'DETALLE',
         'font': ('TITLE SANS', 18, 'bold'), 'bg': color2, 'fg': color12, 'row': 0, 'column': 2},
    ]
    frames_info.sort(key=lambda x: x['name'])

    buttons_info_script = [
        {'text': '2 DESCARGAS_NOCTURNAS',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\1_PROGRAMADOR_TAREAS\5_SUB_DESCARGAS_NOCTURNAS.PY',
         'color': color5, 'font': fuente_boton, 'fg': color11},
    ]

    buttons_info_obiee = [
        {'text': 'OB473_NO_REG',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\4_OB473_ACT_TODO_NO_REG_V2.py',
         'color': color5, 'font': fuente_boton, 'fg': color11},
    ]

    buttons_info_mt = [
        {'text': '1 INVENTORY DETAILED',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\MOTORTRADE\REPORTING\1_INVENTORY_DETAILED.py',
         'color': color4, 'font': fuente_boton, 'fg': color11},
    ]

    buttons_info_controles = [
        {'text': 'LC00119485 SALES EX',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\CONTROLES\ANULACIONES_LC00119485.PY',
         'color': color4, 'font': fuente_boton, 'fg': color11},
    ]

    buttons_info_files = [
        {'text': '2 abrir doc',
         'file': r'C:\Users\a33300\OneDrive - BNP Paribas\Bureau\evidencia.docx',
         'color': color5, 'font': fuente_boton, 'fg': color10},
    ]

    # ──────────────────────────────────────────────────────────────
    # CREACIÓN DE PESTAÑAS
    # ──────────────────────────────────────────────────────────────

    notebook = ttk.Notebook(root)
    notebook.grid(row=0, column=0, sticky='nsew')

    # Pestaña 1: OBIEE y SCRIPTS
    tab1 = tk.Frame(notebook, bg=color2)
    notebook.add(tab1, text='OBIEE & SCRIPTS')

    # Pestaña 2: MOTORTRADE, CONTROLES, DETALLE
    tab2 = tk.Frame(notebook, bg=color2)
    notebook.add(tab2, text='Otros')

    # ──────────────────────────────────────────────────────────────
    # CREACIÓN DE LABELFRAMES EN CADA PESTAÑA
    # ──────────────────────────────────────────────────────────────

    for frame_info in frames_info:
        frame_name = frame_info['name']
        parent_tab = tab1 if frame_name in ['1', '2'] else tab2

        create_labelframe(parent_tab,
                          text=frame_info['text'],
                          font=frame_info['font'],
                          bg=frame_info['bg'],
                          fg=frame_info['fg'],
                          row=frame_info['row'],
                          column=frame_info['column'],
                          buttons_info=(buttons_info_script if frame_name == '1' else
                                        buttons_info_obiee if frame_name == '2' else
                                        buttons_info_mt if frame_name == '3' else
                                        buttons_info_controles if frame_name == '4' else
                                        buttons_info_files),
                          open_files=(frame_name == '5'))

    # Ejecuta la interfaz
    root.mainloop()
