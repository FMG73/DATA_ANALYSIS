import tkinter as tk
from tkinter import ttk
import subprocess
import os
import signal
from melvive.melero_config import CuadroConfig

# Lista global para trackear procesos activos
active_processes = []

def start_process(script_name):
    """Inicia un proceso usando subprocess y lo añade a la lista de procesos activos."""
    try:
        # Verifica que el script existe
        if not os.path.exists(script_name):
            print(f"Error: No se encuentra el archivo {script_name}")
            return
        
        # Inicia el proceso con subprocess
        process = subprocess.Popen(
            ['python', script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        active_processes.append({
            'process': process,
            'script': os.path.basename(script_name),
            'full_path': script_name
        })
        
        update_process_label()
        print(f"Proceso iniciado: {os.path.basename(script_name)} (PID: {process.pid})")
        
    except Exception as e:
        print(f"Error al iniciar el proceso: {e}")

def stop_all_processes():
    """Detiene todos los procesos activos."""
    global active_processes
    stopped_count = 0
    
    for proc_info in active_processes:
        process = proc_info['process']
        
        if process.poll() is None:  # El proceso sigue corriendo
            try:
                # En Windows
                if os.name == 'nt':
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                # En Linux/Mac
                else:
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                
                stopped_count += 1
                print(f"Proceso detenido: {proc_info['script']}")
                
            except Exception as e:
                print(f"Error al detener proceso {proc_info['script']}: {e}")
    
    active_processes.clear()
    update_process_label()
    
    if stopped_count > 0:
        print(f"✓ Se detuvieron {stopped_count} proceso(s)")
    else:
        print("No hay procesos activos")

def stop_process_by_index(index):
    """Detiene un proceso específico por su índice."""
    global active_processes
    
    if 0 <= index < len(active_processes):
        proc_info = active_processes[index]
        process = proc_info['process']
        
        if process.poll() is None:
            try:
                if os.name == 'nt':
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                else:
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                
                print(f"✓ Proceso detenido: {proc_info['script']}")
                
            except Exception as e:
                print(f"Error al detener proceso: {e}")
        
        active_processes.pop(index)
        update_process_label()

def clean_finished_processes():
    """Limpia procesos que ya terminaron."""
    global active_processes
    active_processes = [p for p in active_processes if p['process'].poll() is None]

def update_process_label():
    """Actualiza el contador de procesos activos y la lista."""
    clean_finished_processes()
    count = len(active_processes)
    process_label.config(text=f"Procesos activos: {count}")
    
    # Actualiza la lista de procesos en ejecución
    update_process_listbox()
    
    # Cambiar color según cantidad de procesos
    if count == 0:
        stop_button.config(state='disabled', bg='#808080')
    else:
        stop_button.config(state='normal', bg='#FF4444')

def update_process_listbox():
    """Actualiza el listbox con los procesos activos."""
    process_listbox.delete(0, tk.END)
    
    for i, proc_info in enumerate(active_processes):
        process = proc_info['process']
        status = "Corriendo" if process.poll() is None else "Terminado"
        process_listbox.insert(tk.END, f"{i+1}. {proc_info['script']} - PID: {process.pid} ({status})")

def stop_selected_process():
    """Detiene el proceso seleccionado en el listbox."""
    selection = process_listbox.curselection()
    if selection:
        index = selection[0]
        stop_process_by_index(index)

def show_process_details():
    """Muestra detalles del proceso seleccionado."""
    selection = process_listbox.curselection()
    if selection:
        index = selection[0]
        if 0 <= index < len(active_processes):
            proc_info = active_processes[index]
            details = f"""
Detalles del Proceso:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Script: {proc_info['script']}
Ruta completa: {proc_info['full_path']}
PID: {proc_info['process'].pid}
Estado: {'Corriendo' if proc_info['process'].poll() is None else 'Terminado'}
            """
            print(details)

def open_file(file_path):
    """Abre un archivo con la aplicación predeterminada del sistema."""
    if os.path.exists(file_path):
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        else:  # Linux/Mac
            subprocess.Popen(['xdg-open', file_path])
    else:
        print(f"Error: No se encuentra el archivo {file_path}")

def create_button(parent, text, script_name, color, font, fg, row, column, command=None):
    """Crea un botón con estilo personalizado y lógica de ejecución."""
    button = tk.Button(parent,
                       text=text,
                       bg=color,
                       font=font,
                       fg=fg,
                       cursor='hand2',
                       command=command or (lambda: start_process(script_name)))
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


if __name__ == '__main__':
    root = tk.Tk()
    root.title('NUEVO CUADRO MANDOS ENTREPRISE')
    root.iconbitmap(CuadroConfig.ruta_iconbitmap)
    root.resizable(True, True)

    fuente_boton = ('Arial', 14)

    style = ttk.Style()
    style.theme_use('default')

    style.configure('TNotebook.Tab',
                    font=('Arial', 16, 'bold'),
                    padding=[12, 6],
                    background='#034242',
                    foreground='white',
                    borderwidth=3)

    style.map('TNotebook.Tab',
              background=[('selected', '#00915A')],
              foreground=[('selected', 'white')])

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PANEL DE CONTROL DE PROCESOS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    control_frame = tk.Frame(root, bg='#034242', padx=10, pady=10)
    control_frame.grid(row=0, column=0, sticky='ew', columnspan=10)
    
    # Frame izquierdo para controles
    left_control = tk.Frame(control_frame, bg='#034242')
    left_control.pack(side='left', fill='both', expand=True)
    
    # Etiqueta con contador de procesos
    process_label = tk.Label(left_control, 
                            text="Procesos activos: 0",
                            font=('Arial', 12, 'bold'),
                            bg='#034242',
                            fg='white')
    process_label.pack(side='left', padx=10)
    
    # Botón para detener todos los procesos
    stop_button = tk.Button(left_control,
                           text="⬛ DETENER TODOS",
                           bg='#808080',
                           fg='white',
                           font=('Arial', 12, 'bold'),
                           cursor='hand2',
                           state='disabled',
                           command=stop_all_processes,
                           padx=20,
                           pady=5)
    stop_button.pack(side='left', padx=10)
    
    # Botón para refrescar el contador
    refresh_button = tk.Button(left_control,
                              text="🔄 Actualizar",
                              bg='#00915A',
                              fg='white',
                              font=('Arial', 10),
                              cursor='hand2',
                              command=update_process_label,
                              padx=10,
                              pady=5)
    refresh_button.pack(side='left', padx=5)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LISTA DE PROCESOS ACTIVOS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    process_list_frame = tk.LabelFrame(root, 
                                       text="Procesos en Ejecución",
                                       font=('Arial', 10, 'bold'),
                                       bg='#034242',
                                       fg='white',
                                       padx=5,
                                       pady=5)
    process_list_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5, columnspan=10)
    
    # Listbox para mostrar procesos
    process_listbox = tk.Listbox(process_list_frame,
                                 height=4,
                                 font=('Courier', 9),
                                 bg='#f0f0f0',
                                 selectmode=tk.SINGLE)
    process_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)
    
    # Scrollbar para el listbox
    scrollbar = tk.Scrollbar(process_list_frame, command=process_listbox.yview)
    scrollbar.pack(side='left', fill='y')
    process_listbox.config(yscrollcommand=scrollbar.set)
    
    # Botones para gestión individual
    button_frame = tk.Frame(process_list_frame, bg='#034242')
    button_frame.pack(side='left', padx=5)
    
    stop_selected_button = tk.Button(button_frame,
                                     text="🛑 Detener\nSeleccionado",
                                     bg='#FF6666',
                                     fg='white',
                                     font=('Arial', 9),
                                     cursor='hand2',
                                     command=stop_selected_process,
                                     width=12)
    stop_selected_button.pack(pady=2)
    
    details_button = tk.Button(button_frame,
                              text="ℹ️ Ver\nDetalles",
                              bg='#4444FF',
                              fg='white',
                              font=('Arial', 9),
                              cursor='hand2',
                              command=show_process_details,
                              width=12)
    details_button.pack(pady=2)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DEFINICIÓN DE CUADROS (LABELFRAMES)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    fuente_frame = ('Arial', 18, 'bold')

    frames_info = [
        {'name': 'SCRIPTS', 'text': 'SCRIPTS',
         'font': fuente_frame, 'bg': '#034242', 'fg': '#FFFFFF', 'row': '0', 'column': '2'},

        {'name': 'OBIEE', 'text': 'OBIEE',
         'font': fuente_frame, 'bg': '#034242', 'fg': '#FFFFFF', 'row': '0', 'column': '3'},

        {'name': 'MOTORTRADE', 'text': 'MOTORTRADE',
         'font': fuente_frame, 'bg': '#034242', 'fg': '#FFFFFF', 'row': '0', 'column': '1'},

        {'name': 'CONTROLES', 'text': 'CONTROLES',
         'font': fuente_frame, 'bg': '#034242', 'fg': '#FFFFFF', 'row': '0', 'column': '4'},

        {'name': 'DETALLE', 'text': 'DETALLE',
         'font': fuente_frame, 'bg': '#034242', 'fg': '#FFFFFF', 'row': '0', 'column': '5'},

        {'name': 'START', 'text': 'START',
         'font': fuente_frame, 'bg': '#034242', 'fg': '#FFFFFF', 'row': '0', 'column': '0'},
    ]

    buttons_info_start = [
        {'text': '0 MOVER ARCHIVOS',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\ACTUALIZAR_CONSULTAS\ARCHIVOS_MOVER.py',
         'color': CuadroConfig.color13, 'font': fuente_boton, 'fg': CuadroConfig.color12},
        {'text': '01 SUPER CONSOLIDAR',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\PROCESOS_ENCADENADOS\1_SUB_CONSO_DESCARGAS.py',
         'color': CuadroConfig.color12, 'font': fuente_boton, 'fg': CuadroConfig.color11},
    ]

    buttons_info_controles = [
        {'text': 'LC00119485 SALES EX',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\CONTROLES\ANULACIONES_LC00119485.PY',
         'color': CuadroConfig.color4,
         'font': fuente_boton, 'fg': CuadroConfig.color11},
        {'text': 'LC00119476 CUSTOMER',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\CONTROLES\CUSTOMER_STATUS_LC00119476.py',
         'color': CuadroConfig.color4,
         'font': fuente_boton, 'fg': CuadroConfig.color11},
    ]

    buttons_info_obiee = [
        {'text': 'OB473_NO_REG',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\4_OB473_ACT_TODO_NO_REG_V2.py',
         'color': CuadroConfig.color5, 'font': fuente_boton, 'fg': CuadroConfig.color11},
        {'text': 'OB713 RELEASE',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\OBIEE\OB713_CARG_RELEASE.py',
         'color': CuadroConfig.color7, 'font': fuente_boton, 'fg': CuadroConfig.color11},
    ]

    buttons_info_script = [
        {'text': '2 DESCARGAS_NOCTURNAS',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\1_PROGRAMADOR_TAREAS\5_SUB_DESCARGAS_NOCTURNAS.PY',
         'color': CuadroConfig.color5, 'font': fuente_boton, 'fg': CuadroConfig.color11},
        {'text': '9.1 DEUDA B2B',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\B2B_RECOBROS\b2b_recobros.py',
         'color': CuadroConfig.color5, 'font': fuente_boton, 'fg': CuadroConfig.color11},
    ]

    buttons_info_mt = [
        {'text': '1 INVENTORY DETAILED',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\MOTORTRADE\REPORTING\1_INVENTORY_DETAILED.py',
         'color': CuadroConfig.color4, 'font': fuente_boton, 'fg': CuadroConfig.color11},
        {'text': '8.1 PEDIR SCORE ASS',
         'script': r'C:\Python\JupyterLab\Lab\PMELERO\SCRIPTS_py\SCORE\1_PETICION_SCORE\1_PET_SCO_ASS_ok.py',
         'color': CuadroConfig.color9, 'font': fuente_boton, 'fg': CuadroConfig.color12},
    ]

    buttons_info_files = [
        {'text': '2 abrir doc',
         'file': r'C:\evidencia.docx',
         'color': CuadroConfig.color5,
         'font': fuente_boton, 'fg': CuadroConfig.color11},
        {'text': '3 abrir excel',
         'file': r'C:\\BORRAR_AL_LEER.xlsx',
         'color': CuadroConfig.color6,
         'font': fuente_boton, 'fg': CuadroConfig.color11},
    ]

    tabs_info = [
        {'name': 'tab1', 'title': 'FRECUENTES', 'frames': ['START', 'MOTORTRADE','SCRIPTS','OBIEE']},
        {'name': 'tab2', 'title': 'OCASIONALES', 'frames': ['CONTROLES', 'DETALLE']},
    ]

    notebook = ttk.Notebook(root)
    notebook.grid(row=2, column=0, sticky='nsew')

    tab_objects = {}

    for tab in tabs_info:
        tab_frame = tk.Frame(notebook, bg=CuadroConfig.color15)
        notebook.add(tab_frame, text=tab['title'])
        tab_objects[tab['name']] = tab_frame

    for frame_info in frames_info:
        frame_name = frame_info['name']
        for tab in tabs_info:
            if frame_name in tab['frames']:
                parent_tab = tab_objects[tab['name']]
                create_labelframe(parent_tab,
                                  text=frame_info['text'],
                                  font=frame_info['font'],
                                  bg=frame_info['bg'],
                                  fg=frame_info['fg'],
                                  row=frame_info['row'],
                                  column=frame_info['column'],
                                  buttons_info=(buttons_info_script if frame_name == 'SCRIPTS' else
                                                buttons_info_obiee if frame_name == 'OBIEE' else
                                                buttons_info_mt if frame_name == 'MOTORTRADE' else
                                                buttons_info_controles if frame_name == 'CONTROLES' else
                                                buttons_info_start if frame_name == 'START' else
                                                buttons_info_files),
                                  open_files=(frame_name == 'DETALLE'))
                break

    # Actualización automática cada 3 segundos
    def auto_update():
        update_process_label()
        root.after(3000, auto_update)
    
    auto_update()

    root.mainloop()
