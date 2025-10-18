from ttkbootstrap import Style
import ttkbootstrap as ttk
import tkinter as tk
from idlelib.tooltip import Hovertip
from multiprocessing import Process
import os

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
# FUENTES
# ──────────────────────────────────────────────────────────────

fuente_boton = ('Segoe UI', 12)
fuente_titulo = ('Segoe UI', 14, 'bold')

# ──────────────────────────────────────────────────────────────
# ESTRUCTURA DE PESTAÑAS Y FRAMES
# ──────────────────────────────────────────────────────────────

tabs_info = {
    'OBIEE & SCRIPTS': [
        {
            'orden': 'actualizacion_obiee',
            'name': 'Actualización OBIEE',
            'id': 'frame_obiee',
            'row': 0,
            'column': 0,
            'font': fuente_titulo,
            'bg': color2,
            'fg': color12
        },
        {
            'orden': 'descargas_nocturnas',
            'name': 'Descargas Nocturnas',
            'id': 'frame_descargas',
            'row': 0,
            'column': 1,
            'font': fuente_titulo,
            'bg': color2,
            'fg': color12
        },
        {
            'orden': 'scripts_utiles',
            'name': 'Scripts Útiles',
            'id': 'frame_scripts',
            'row': 1,
            'column': 0,
            'font': fuente_titulo,
            'bg': color2,
            'fg': color12
        }
    ],
    'Otros': [
        {
            'orden': 'motortrade',
            'name': 'Motortrade',
            'id': 'frame_motortrade',
            'row': 0,
            'column': 0,
            'font': fuente_titulo,
            'bg': color2,
            'fg': color12
        },
        {
            'orden': 'controles',
            'name': 'Controles',
            'id': 'frame_controles',
            'row': 0,
            'column': 1,
            'font': fuente_titulo,
            'bg': color2,
            'fg': color12
        },
        {
            'orden': 'documentos',
            'name': 'Documentos',
            'id': 'frame_docs',
            'row': 1,
            'column': 0,
            'font': fuente_titulo,
            'bg': color2,
            'fg': color12,
            'open_files': True
        }
    ]
}

# ──────────────────────────────────────────────────────────────
# BOTONES POR FRAME
# ──────────────────────────────────────────────────────────────

buttons_by_frame = {
    'frame_obiee': [
        {'text': 'Actualizar OBIEE', 'script': r'C:\Scripts\update_obiee.py', 'color': color5, 'font': fuente_boton, 'fg': color11, 'tooltip': 'Ejecuta actualización de datos OBIEE'},
        {'text': 'Ver Logs OBIEE', 'script': r'C:\Scripts\logs_obiee.py', 'color': color4, 'font': fuente_boton, 'fg': color11, 'tooltip': 'Abre los logs generados por OBIEE'}
    ],
    'frame_descargas': [
        {'text': 'Descarga Clientes', 'script': r'C:\Scripts\descarga_clientes.py', 'color': color5, 'font': fuente_boton, 'fg': color11, 'tooltip': 'Extrae datos de clientes desde Oracle'},
        {'text': 'Descarga Productos', 'script': r'C:\Scripts\descarga_productos.py', 'color': color5, 'font': fuente_boton, 'fg': color11, 'tooltip': 'Extrae datos de productos desde Oracle'}
    ],
    'frame_scripts': [
        {'text': 'Script de Validación', 'script': r'C:\Scripts\validacion.py', 'color': color7, 'font': fuente_boton, 'fg': color11, 'tooltip': 'Valida integridad de datos extraídos'},
        {'text': 'Script de Limpieza', 'script': r'C:\Scripts\limpieza.py', 'color': color7, 'font': fuente_boton, 'fg': color11, 'tooltip': 'Limpia registros duplicados o corruptos'}
    ],
    'frame_motortrade': [
        {'text': 'Reporte Inventario', 'script': r'C:\Scripts\inventario_motortrade.py', 'color': color4, 'font': fuente_boton, 'fg': color11, 'tooltip': 'Genera reporte de inventario Motortrade'}
    ],
    'frame_controles': [
        {'text': 'Control Ventas', 'script': r'C:\Scripts\control_ventas.py', 'color': color4, 'font': fuente_boton, 'fg': color11, 'tooltip': 'Verifica ventas registradas'},
        {'text': 'Control Anulaciones', 'script': r'C:\Scripts\control_anulaciones.py', 'color': color4, 'font': fuente_boton, 'fg': color11, 'tooltip': 'Verifica anulaciones recientes'}
    ],
    'frame_docs': [
        {'text': 'Abrir Evidencia.docx', 'file': r'C:\Documentos\evidencia.docx', 'color': color5, 'font': fuente_boton, 'fg': color10, 'tooltip': 'Abre documento de evidencia'},
        {'text': 'Abrir Manual.pdf', 'file': r'C:\Documentos\manual.pdf', 'color': color5, 'font': fuente_boton, 'fg': color10, 'tooltip': 'Abre manual de usuario'}
    ]
}

# ──────────────────────────────────────────────────────────────
# FUNCIONES DE UTILIDAD
# ──────────────────────────────────────────────────────────────

def run_script(script_name):
    os.system(f'python "{script_name}"')

def open_file(file_path):
    os.startfile(file_path)

def create_button(parent, text, script_name, color, font, fg, row, column, command=None, tooltip=None):
    button = ttk.Button(parent,
                        text=text,
                        bootstyle='info',
                        cursor='hand2')
    button.configure(command=command or (lambda: Process(target=run_script, args=(script_name,)).start()))
    button.grid(row=row, column=column, padx=5, pady=5, sticky='w')
    if tooltip:
        Hovertip(button, tooltip)

def create_labelframe(root, text, font, fg, bg, row, column, buttons_info, open_files=False):
    labelframe = ttk.LabelFrame(root,
                                text=text,
                                bootstyle='dark',
                                padding=10)
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
                      command=command,
                      tooltip=button_info.get('tooltip'))
    return labelframe

# ──────────────────────────────────────────────────────────────
# INICIO DE LA INTERFAZ
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = ttk.Window(themename='darkly')
    app.title('CUADRO MANDOS ENTREPRISE')
    app.iconbitmap(r'C:\LOGO_H_DIGI_RGB.ico')
    app.resizable(True, True)

    notebook = ttk.Notebook(app, bootstyle='dark')
    notebook.grid(row=0, column=0, sticky='nsew')

    for tab_name, frames in tabs_info.items():
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text=tab_name)

        sorted_frames = sorted(frames, key=lambda f: f['orden'])

        for frame in sorted_frames:
            buttons_info = sorted(buttons_by_frame.get(frame['id'], []), key=lambda b: b['text'])

            create_labelframe(tab_frame,
                              text=frame['name'],
                              font=frame['font'],
                              fg=frame['fg'],
                              bg=frame['bg'],
                              row=frame['row'],
                              column=frame['column'],
                              buttons_info=buttons_info,
                              open_files=frame
