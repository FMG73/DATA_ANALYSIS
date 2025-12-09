import subprocess
import time
import pyautogui
import pygetwindow as gw  # Para encontrar la ventana de Tableau

# TUS RUTAS
tableau_exe = r"C:\Program Files\Tableau\Tableau 2022.3\bin\tableau.exe"
tableau_file = r"C:\ruta.twb"
output_image = r"C:\ruta\dashboard.png"

print("1. Abriendo Tableau Desktop...")
proceso = subprocess.Popen([tableau_exe, tableau_file])
time.sleep(20)  # Aumentamos tiempo de espera

print("2. Buscando ventana de Tableau...")
# Buscar la ventana de Tableau
tableau_windows = [w for w in gw.getAllWindows() if 'tableau' in w.title.lower()]

if tableau_windows:
    ventana = tableau_windows[0]
    print(f"   Ventana encontrada: {ventana.title}")
    
    # Activar y maximizar
    ventana.activate()
    time.sleep(1)
    ventana.maximize()
    time.sleep(3)  # Esperar que se redibuje
    
    print("3. Capturando dashboard...")
    screenshot = pyautogui.screenshot()
    screenshot.save(output_image)
    print(f"✅ Imagen guardada en: {output_image}")
else:
    print("❌ No se encontró la ventana de Tableau")

print("4. Cerrando Tableau...")
pyautogui.hotkey('alt', 'f4')
time.sleep(1)
pyautogui.press('enter')  # No guardar cambios
