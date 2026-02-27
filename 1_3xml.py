import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
from melvive.funciones import mensaje_imprimir  # Función de impresión con colores

def generar_xml_desde_excel(ruta_entrada: str, ruta_salida: str) -> None:
    """
    GENERA UN XML DE COEFICIENTES A PARTIR DE UN EXCEL/CSV.

    VALIDACIONES:
    - COLUMNAS OBLIGATORIAS: brand, model, coefficient
    - VACÍOS EN CUALQUIER COLUMNA → ERROR
    - coefficient NO NUMÉRICO → ERROR
    - DUPLICADOS CONFLICTIVOS → ERROR
    - SOLO SE GENERA XML SI NO HAY ERRORES
    """
    
    errores = []
    duplicados_eliminados = 0

    mensaje_imprimir("LEYENDO ARCHIVO...", "blue")

    # 1️⃣ Leer archivo
    try:
        if ruta_entrada.endswith(".csv"):
            df = pd.read_csv(ruta_entrada, encoding="utf-8")
        else:
            df = pd.read_excel(ruta_entrada)
    except Exception as e:
        mensaje_imprimir(f"ERROR LEYENDO ARCHIVO: {str(e).upper()}", "red")
        return

    total_filas = len(df)
    columnas_necesarias = ["brand", "model", "coefficient"]

    # 2️⃣ Comprobar columnas obligatorias
    for col in columnas_necesarias:
        if col not in df.columns:
            mensaje_imprimir(f"COLUMNA OBLIGATORIA FALTANTE: {col.upper()}", "red")
            return

    # 3️⃣ Validar cada fila y columna correctamente (detecta NaN, None o "")
    for index, row in df.iterrows():
        fila = index + 2  # Para coincidir con Excel (cabecera incluida)
        
        for col in columnas_necesarias:
            valor = row.get(col)
            if pd.isna(valor) or (isinstance(valor, str) and valor.strip() == ""):
                errores.append(("FILA {}: {} VACÍO".format(fila, col.upper()), "red"))
            elif col == "coefficient":
                try:
                    float(valor)
                except (ValueError, TypeError):
                    errores.append(("FILA {}: COEFFICIENT NO NUMÉRICO".format(fila), "red"))

    # 4️⃣ Duplicados conflictivos
    df["brand"] = df["brand"].astype(str).str.strip()
    df["model"] = df["model"].astype(str).str.strip()
    df["coefficient"] = pd.to_numeric(df["coefficient"], errors="coerce")

    duplicados = df[df.duplicated(subset=["brand", "model"], keep=False)]
    for (brand, model), grupo in duplicados.groupby(["brand", "model"]):
        coef_unicos = grupo["coefficient"].unique()
        if len(coef_unicos) > 1:
            filas_conflictivas = grupo.index + 2
            for fila in filas_conflictivas:
                errores.append((
                    "FILA {}: DUPLICADO CONFLICTIVO {} {}".format(fila, brand.upper(), model.upper()),
                    "yellow"
                ))

    # 5️⃣ Imprimir todos los errores y salir si existen
    if errores:
        mensaje_imprimir("SE HAN DETECTADO ERRORES EN EL ARCHIVO:".upper(), "red")
        for texto, color in errores:
            mensaje_imprimir(texto, color)
        mensaje_imprimir("NO SE GENERA XML POR ERRORES.".upper(), "red")
        mensaje_imprimir(
            "RESUMEN: FILAS PROCESADAS: {} | ERRORES DETECTADOS: {} | DUPLICADOS ELIMINADOS: {}".format(
                total_filas, len(errores), duplicados_eliminados
            ).upper(),
            "red"
        )
        return

    # 6️⃣ Eliminar duplicados seguros
    df_antes = len(df)
    df = df.drop_duplicates(subset=["brand", "model"], keep="first")
    duplicados_eliminados = df_antes - len(df)
    if duplicados_eliminados > 0:
        mensaje_imprimir("DUPLICADOS SEGUROS ELIMINADOS: {}".format(duplicados_eliminados).upper(), "yellow")

    # 7️⃣ Generar XML
    mensaje_imprimir("GENERANDO XML...".upper(), "blue")
    service = ET.Element("service", attrib={"type": "transport"})
    coefficients = ET.SubElement(service, "coefficients")

    for _, row in df.iterrows():
        coef = ET.SubElement(coefficients, "coefficient", attrib={"value": str(row["coefficient"])})
        conditions = ET.SubElement(coef, "conditions")
        if_all = ET.SubElement(conditions, "ifAll")
        prop_brand = ET.SubElement(if_all, "property", attrib={"name": "item.brand"})
        prop_brand.text = row["brand"]
        prop_model = ET.SubElement(if_all, "property", attrib={"name": "item.model"})
        prop_model.text = row["model"]

    ET.SubElement(coefficients, "coefficient", attrib={"value": "1.0"})  # fallback

    # 8️⃣ Prettify XML
    xml_str = ET.tostring(service, encoding="utf-8")
    dom = minidom.parseString(xml_str)
    pretty_xml_as_string = dom.toprettyxml(indent="    ")

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(pretty_xml_as_string)

    mensaje_imprimir("XML GENERADO CORRECTAMENTE EN {}".format(ruta_salida).upper(), "green")
    mensaje_imprimir(
        "RESUMEN FINAL: FILAS PROCESADAS: {} | DUPLICADOS ELIMINADOS: {}".format(total_filas, duplicados_eliminados).upper(),
        "blue"
    )