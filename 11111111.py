import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
from melvive.funciones import mensaje_imprimir  # Tu función de impresión con colores

def generar_xml_desde_excel(ruta_entrada: str, ruta_salida: str) -> None:
    """
    GENERA UN XML DE COEFICIENTES A PARTIR DE UN EXCEL/CSV.

    MODO DEBUG DE ERRORES:
    - Todas las filas con errores se muestran como tabla coloreada
    - Columnas obligatorias: brand, model, coefficient
    - Vacíos y coefficient no numérico se detectan
    - Duplicados conflictivos se marcan en amarillo
    - Solo si no hay errores se genera XML
    """
    filas_con_errores = []  # Lista de diccionarios con fila y columna con error
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
    columnas_necesarias = {"brand", "model", "coefficient"}
    for col in columnas_necesarias:
        if col not in df.columns:
            mensaje_imprimir(f"COLUMNA OBLIGATORIA FALTANTE: {col}", "red")
            return

    # 2️⃣ Validar todas las filas
    for index, row in df.iterrows():
        fila = index + 2  # +2 por cabecera
        errores_fila = {}

        brand = str(row.get("brand", "")).strip()
        model = str(row.get("model", "")).strip()
        coefficient = row.get("coefficient")

        # Vacíos o no numérico → rojo
        if not brand:
            errores_fila["brand"] = ("VACÍO", "red")
        if not model:
            errores_fila["model"] = ("VACÍO", "red")
        if coefficient is None or (isinstance(coefficient, float) and pd.isna(coefficient)) or str(coefficient).strip() == "":
            errores_fila["coefficient"] = ("VACÍO", "red")
        else:
            try:
                float(coefficient)
            except (ValueError, TypeError):
                errores_fila["coefficient"] = ("NO NUMÉRICO", "red")

        if errores_fila:
            errores_fila["fila"] = fila
            filas_con_errores.append(errores_fila)

    # 3️⃣ Duplicados conflictivos → amarillo
    df["brand"] = df["brand"].astype(str).str.strip()
    df["model"] = df["model"].astype(str).str.strip()
    df["coefficient"] = pd.to_numeric(df["coefficient"], errors="coerce")

    duplicados = df[df.duplicated(subset=["brand", "model"], keep=False)]
    for (brand, model), grupo in duplicados.groupby(["brand", "model"]):
        coef_unicos = grupo["coefficient"].unique()
        if len(coef_unicos) > 1:
            filas_conflictivas = grupo.index + 2
            for fila in filas_conflictivas:
                filas_con_errores.append({
                    "fila": fila,
                    "brand": (brand, "yellow"),
                    "model": (model, "yellow"),
                    "coefficient": ("DUPLICADO CONFLICTIVO", "yellow")
                })

    # 4️⃣ Mostrar tabla de errores coloreada
    if filas_con_errores:
        mensaje_imprimir("SE HAN DETECTADO ERRORES EN EL ARCHIVO:", "red")
        for fila in filas_con_errores:
            salida = f"FILA {fila.get('fila')}: "
            for col in ["brand", "model", "coefficient"]:
                if col in fila:
                    valor, color = fila[col] if isinstance(fila[col], tuple) else (fila[col], "red")
                    salida += f"{col.upper()}={str(valor).upper()} "
                    mensaje_imprimir(salida, color)
        mensaje_imprimir("NO SE GENERA XML POR ERRORES.", "red")
        mensaje_imprimir(
            f"RESUMEN: FILAS PROCESADAS: {total_filas} | FILAS CON ERRORES: {len(filas_con_errores)} | DUPLICADOS ELIMINADOS: {duplicados_eliminados}",
            "red"
        )
        return

    # 5️⃣ Eliminar duplicados seguros
    df_antes = len(df)
    df = df.drop_duplicates(subset=["brand", "model"], keep="first")
    duplicados_eliminados = df_antes - len(df)
    if duplicados_eliminados > 0:
        mensaje_imprimir(f"DUPLICADOS SEGUROS ELIMINADOS: {duplicados_eliminados}", "yellow")

    # 6️⃣ Generar XML
    mensaje_imprimir("GENERANDO XML...", "blue")
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

    ET.SubElement(coefficients, "coefficient", attrib={"value": "1.0"})  # Fallback

    # 7️⃣ Prettify XML
    xml_str = ET.tostring(service, encoding="utf-8")
    dom = minidom.parseString(xml_str)
    pretty_xml_as_string = dom.toprettyxml(indent="    ")

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(pretty_xml_as_string)

    mensaje_imprimir(f"XML GENERADO CORRECTAMENTE EN {ruta_salida}".upper(), "green")
    mensaje_imprimir(
        f"RESUMEN FINAL: FILAS PROCESADAS: {total_filas} | DUPLICADOS ELIMINADOS: {duplicados_eliminados}",
        "blue"
    )