import subprocess
import time
import pyautogui

tableau_exe = r"C:\Program Files\Tableau\Tableau 2022.3\bin\tableau.exe"
tableau_file = r"C:\ruta.twb"
output_folder = r"C:\ruta"

print("1. Abriendo Tableau...")
proceso = subprocess.Popen([tableau_exe, tableau_file])
time.sleep(20)

# Activar ventana
pyautogui.click(960, 540)
time.sleep(2)

print("2. Exportando a PDF...")
# Abrir menú Dashboard
pyautogui.hotkey('alt', 'd')
time.sleep(1)

# Buscar Export PDF (probar diferentes teclas)
pyautogui.press('e')  # O puede ser 'x' o 'p'
time.sleep(2)

# Si aparece diálogo de guardar
pyautogui.write(output_folder + r"\dashboard_temp.pdf")
time.sleep(1)
pyautogui.press('enter')
time.sleep(3)

print("3. PDF exportado")

# Cerrar Tableau
pyautogui.hotkey('alt', 'f4')
time.sleep(1)
pyautogui.press('enter')
