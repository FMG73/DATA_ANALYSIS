import win32com.client
import os
import time

# Ruta a tu archivo Tableau (CAMBIA ESTA RUTA)
tableau_file = r"C:\ruta\a\tu\archivo.twbx"

# Ruta donde guardar la imagen (CAMBIA ESTA RUTA)
output_image = r"C:\ruta\salida\dashboard.png"

try:
    print("Abriendo Tableau Desktop...")
    tableau = win32com.client.Dispatch("Tableau.Application")
    
    print(f"Abriendo workbook: {tableau_file}")
    workbook = tableau.Workbooks.Open(tableau_file)
    
    print("Workbook abierto correctamente!")
    print(f"Número de hojas: {workbook.Worksheets.Count}")
    
    # Listar nombres de hojas/dashboards
    for i in range(workbook.Worksheets.Count):
        print(f"  Hoja {i+1}: {workbook.Worksheets.Item(i).Name}")
    
    workbook.Close()
    tableau.Quit()
    
except Exception as e:
    print(f"Error: {e}")