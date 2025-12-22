import zipfile
import os
import csv

def buscar_ruta_en_powerquery(carpeta, texto_buscado, salida_csv):
    resultados = []

    for archivo in os.listdir(carpeta):
        if not archivo.lower().endswith((".xlsx", ".xlsm", ".xlsb", ".pbix")):
            continue

        ruta_archivo = os.path.join(carpeta, archivo)

        try:
            with zipfile.ZipFile(ruta_archivo, 'r') as z:
                for nombre in z.namelist():
                    # Power Query suele estar en DataMashup o conexiones
                    if "DataMashup" in nombre or "connections" in nombre.lower():
                        contenido = z.read(nombre).decode(errors="ignore").lower()

                        if texto_buscado.lower() in contenido:
                            resultados.append({
                                "archivo": archivo,
                                "ruta_encontrada": texto_buscado,
                                "archivo_interno": nombre,
                                "coincidencias": contenido.count(texto_buscado.lower())
                            })
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")

    # Guardar CSV
    with open(salida_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["archivo", "ruta_encontrada", "archivo_interno", "coincidencias"])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"CSV generado: {salida_csv}")
    return resultados


# === CONFIGURACIÓN ===
carpeta = r"C:\Ruta\A\Tus\Excels"
texto_buscado = r"C:\Ruta\Actual\Del\Archivo"
salida_csv = r"C:\Ruta\Salida\resultado_busqueda_powerquery.csv"

# === EJECUCIÓN ===
buscar_ruta_en_powerquery(carpeta, texto_buscado, salida_csv)
