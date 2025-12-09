import subprocess
import time
import pyautogui

# TUS RUTAS
tableau_exe = r"C:\Program Files\Tableau\Tableau 2022.3\bin\tableau.exe"  # Ajusta si está en otra carpeta
tableau_file = r"C:\ruta.twb"
output_image = r"C:\ruta\dashboard.png"

print("Abriendo Tableau Desktop...")
proceso = subprocess.Popen([tableau_exe, tableau_file])
time.sleep(15)  # Espera a que cargue completamente

print("Maximizando ventana...")
# Maximizar la ventana de Tableau
pyautogui.hotkey('win', 'up')  # Windows + Flecha arriba maximiza
time.sleep(2)

print("Capturando pantalla del dashboard...")
screenshot = pyautogui.screenshot()
screenshot.save(output_image)
print(f"✅ Imagen guardada en: {output_image}")

# Cerrar Tableau (opcional)
print("Cerrando Tableau...")
pyautogui.hotkey('alt', 'f4')  # Alt+F4 cierra la ventana
time.sleep(1)
pyautogui.press('tab')  # Por si pregunta "guardar cambios"
pyautogui.press('enter')  # No guardar

print("¡Proceso completado!")
