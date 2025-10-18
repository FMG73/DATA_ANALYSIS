from ttkbootstrap import Style
import ttkbootstrap as ttk
import tkinter as tk
from idlelib.tooltip import Hovertip
from multiprocessing import Process
import os

# ──────────────────────────────────────────────────────────────
# INICIALIZAR TEMA Y COLORES DEL TEMA COMO VARIABLES
# ──────────────────────────────────────────────────────────────

style = Style(theme='darkly')

color_primary = style.colors.primary
color_info = style.colors.info
color_success = style.colors.success
color_warning = style.colors.warning
color_danger = style.colors.danger
color_light = style.colors.light
color_dark = style.colors.dark
color_bg = style.colors.bg
color_fg = style.colors.fg

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
            'bg': color_dark,
            'fg': color_light
        },
        {
            'orden': 'descargas_nocturnas',
            'name': 'Descargas Nocturnas',
            'id': 'frame_descargas',
            'row': 0,
            'column': 1,
            'font': fuente_titulo,
            'bg': color_dark,
            'fg': color_light
        },
        {
            'orden': 'scripts_utiles',
            'name': 'Scripts Útiles',
            'id': 'frame_scripts',
            'row': 1,
            'column': 0,
            'font': fuente_titulo,
            'bg': color_dark,
            'fg': color_light
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
            'bg': color_dark,
            'fg': color_light
        },
        {
            'orden': 'controles',
            'name': 'Controles',
            'id': 'frame_controles',
            'row': 0,
            'column': 1,
            'font': fuente_titulo,
            'bg': color_dark,
            'fg': color_light
        },
        {
            'orden': 'documentos',
            'name': 'Documentos',
            'id': 'frame_docs',
            'row': 1,
            'column': 0,
            'font': fuente_titulo,
            'bg': color_dark,
            'fg': color_light,
            'open_files': True
        }
    ]
}

# ──────────────────────────────────────────────────────────────
# BOTONES POR FRAME
# ──────────────────────────────────────────────────────────────

buttons_by_frame = {
    'frame_obiee': [
        {'text': 'Actualizar OBIEE', 'script': r'C:\Scripts\update_obiee.py', 'color': color_info, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Ejecuta actualización de datos OBIEE'},
        {'text': 'Ver Logs OBIEE', 'script': r'C:\Scripts\logs_obiee.py', 'color': color_success, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Abre los logs generados por OBIEE'}
    ],
    'frame_descargas': [
        {'text': 'Descarga Clientes', 'script': r'C:\Scripts\descarga_clientes.py', 'color': color_info, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Extrae datos de clientes desde Oracle'},
        {'text': 'Descarga Productos', 'script': r'C:\Scripts\descarga_productos.py', 'color': color_info, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Extrae datos de productos desde Oracle'}
    ],
    'frame_scripts': [
        {'text': 'Script de Validación', 'script': r'C:\Scripts\validacion.py', 'color': color_warning, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Valida integridad de datos extraídos'},
        {'text': 'Script de Limpieza', 'script': r'C:\Scripts\limpieza.py', 'color': color_warning, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Limpia registros duplicados o corruptos'}
    ],
    'frame_motortrade': [
        {'text': 'Reporte Inventario', 'script': r'C:\Scripts\inventario_motortrade.py', 'color': color_success, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Genera reporte de inventario Motortrade'}
    ],
    'frame_controles': [
        {'text': 'Control Ventas', 'script': r'C:\Scripts\control_ventas.py', 'color': color_success, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Verifica ventas registradas'},
        {'text': 'Control Anulaciones', 'script': r'C:\Scripts\control_anulaciones.py', 'color': color_success, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Verifica anulaciones recientes'}
    ],
    'frame_docs': [
        {'text': 'Abrir Evidencia.docx', 'file': r'C:\Documentos\evidencia.docx', 'color': color_info, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Abre documento de evidencia'},
        {'text': 'Abrir Manual.pdf', 'file': r'C:\Documentos\manual.pdf', 'color': color_info, 'font': fuente_boton, 'fg': color_fg, 'tooltip': 'Abre manual de usuario'}
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
                              open_files=frame.get('open_files', False))

    app.mainloop()
