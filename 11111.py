import pandas as pd
import xml.etree.ElementTree as ET
from melvive.funciones import mensaje_imprimir  # Tu función de impresión con colores

def generar_xml_desde_excel(ruta_entrada: str, ruta_salida: str) -> None:
    """
    GENERA UN XML DE COEFICIENTES A PARTIR DE UN EXCEL/CSV.

    VALIDACIONES:
    - COLUMNAS OBLIGATORIAS: brand, model, coefficient
    - NO SE PERMITEN VALORES VACÍOS
    - coefficient DEBE SER NUMÉRICO
    - DUPLICADOS:
        * MISMO brand+model Y MISMO coefficient → SE ELIMINAN
        * MISMO brand+model Y DISTINTO coefficient → ERROR
    - SI HAY ERRORES → NO SE GENERA XML

    TODOS LOS MENSAJES SE IMPRIMEN EN MAYÚSCULAS Y CON COLORES:
    - blue   → info/progreso
    - yellow → advertencias/duplicados
    - red    → errores críticos
    - green  → confirmación de éxito
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
        mensaje_imprimir(f"ERROR LEYENDO ARCHIVO: {e}".upper(), "red")
        return

    total_filas = len(df)

    # 2️⃣ Validar columnas
    columnas_necesarias = {"brand", "model", "coefficient"}
    if not columnas_necesarias.issubset(df.columns):
        errores.append(f"FALTAN COLUMNAS OBLIGATORIAS: {columnas_necesarias}")

    # 3️⃣ Validar filas
    for index, row in df.iterrows():
        fila = index + 2  # +2 por cabecera Excel

        brand = str(row.get("brand", "")).strip()
        model = str(row.get("model", "")).strip()
        coefficient = row.get("coefficient")

        # Detectar brand vacío
        if not brand:
            errores.append(f"FILA {fila}: BRAND VACÍO")
        # Detectar model vacío
        if not model:
            errores.append(f"FILA {fila}: MODEL VACÍO")
        # Detectar coefficient vacío
        if coefficient is None or (isinstance(coefficient, float) and pd.isna(coefficient)) or str(coefficient).strip() == "":
            errores.append(f"FILA {fila}: COEFFICIENT VACÍO")
        else:
            try:
                float(coefficient)
            except (ValueError, TypeError):
                errores.append(f"FILA {fila}: COEFFICIENT NO ES NUMÉRICO")

    # 4️⃣ Validar duplicados conflictivos
    df["brand"] = df["brand"].astype(str).str.strip()
    df["model"] = df["model"].astype(str).str.strip()
    df["coefficient"] = pd.to_numeric(df["coefficient"], errors="coerce")

    duplicados = df[df.duplicated(subset=["brand", "model"], keep=False)]

    for (brand, model), grupo in duplicados.groupby(["brand", "model"]):
        coef_unicos = grupo["coefficient"].unique()
        if len(coef_unicos) > 1:
            errores.append(
                f"DUPLICADO CONFLICTIVO: {brand} {model} TIENE COEFICIENTES DISTINTOS {coef_unicos}"
            )

    # 5️⃣ Reportar errores y salir si existen
    if errores:
        mensaje_imprimir("SE HAN DETECTADO ERRORES:", "red")
        for err in errores:
            mensaje_imprimir(err.upper(), "red")
        mensaje_imprimir("NO SE GENERA XML POR ERRORES.", "red")
        mensaje_imprimir(
            f"RESUMEN: FILAS PROCESADAS: {total_filas} | ERRORES: {len(errores)} | DUPLICADOS ELIMINADOS: {duplicados_eliminados}",
            "red"
        )
        return

    # 6️⃣ Eliminar duplicados seguros (mismo coeficiente)
    df_antes = len(df)
    df = df.drop_duplicates(subset=["brand", "model"], keep="first")
    duplicados_eliminados = df_antes - len(df)
    if duplicados_eliminados > 0:
        mensaje_imprimir(f"DUPLICADOS SEGUROS ELIMINADOS: {duplicados_eliminados}", "yellow")

    # 7️⃣ Generar XML
    mensaje_imprimir("GENERANDO XML...", "blue")
    service = ET.Element("service", attrib={"type": "transport"})
    coefficients = ET.SubElement(service, "coefficients")

    for _, row in df.iterrows():
        coef = ET.SubElement(
            coefficients,
            "coefficient",
            attrib={"value": str(row["coefficient"])}
        )
        conditions = ET.SubElement(coef, "conditions")
        if_all = ET.SubElement(conditions, "ifAll")

        prop_brand = ET.SubElement(
            if_all,
            "property",
            attrib={"name": "item.brand"}
        )
        prop_brand.text = row["brand"]

        prop_model = ET.SubElement(
            if_all,
            "property",
            attrib={"name": "item.model"}
        )
        prop_model.text = row["model"]

    # 8️⃣ Fallback final
    ET.SubElement(coefficients, "coefficient", attrib={"value": "1.0"})

    # 9️⃣ Guardar XML
    tree = ET.ElementTree(service)
    tree.write(ruta_salida, encoding="utf-8", xml_declaration=True)
    mensaje_imprimir(f"XML GENERADO CORRECTAMENTE EN {ruta_salida}".upper(), "green")

    # 🔹 Resumen final
    mensaje_imprimir(
        f"RESUMEN FINAL: FILAS PROCESADAS: {total_filas} | ERRORES: {len(errores)} | DUPLICADOS ELIMINADOS: {duplicados_eliminados}",
        "blue"
    )