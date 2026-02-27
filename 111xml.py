import pandas as pd
import xml.etree.ElementTree as ET
from melvive.funciones import imprimir_mensaje


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

    SI NO HAY ERRORES → SE GENERA XML CON FALLBACK value="1.0"
    """

    errores = []

    imprimir_mensaje("LEYENDO ARCHIVO...", "blue")

    # 1️⃣ Leer archivo
    try:
        if ruta_entrada.endswith(".csv"):
            df = pd.read_csv(ruta_entrada, encoding="utf-8")
        else:
            df = pd.read_excel(ruta_entrada)
    except Exception as e:
        imprimir_mensaje(f"ERROR LEYENDO ARCHIVO: {e}", "red")
        return

    # 2️⃣ Validar columnas
    columnas_necesarias = {"brand", "model", "coefficient"}
    if not columnas_necesarias.issubset(df.columns):
        errores.append(
            f"FALTAN COLUMNAS OBLIGATORIAS: {columnas_necesarias}"
        )

    if errores:
        for err in errores:
            imprimir_mensaje(f"ERROR: {err}", "red")
        imprimir_mensaje("NO SE GENERA XML POR ERRORES.", "red")
        return

    imprimir_mensaje("VALIDANDO CONTENIDO DEL ARCHIVO...", "blue")

    # 3️⃣ Validar filas
    for index, row in df.iterrows():

        fila = index + 2  # +2 por cabecera Excel

        brand = str(row.get("brand", "")).strip()
        model = str(row.get("model", "")).strip()
        coefficient = row.get("coefficient")

        # Validar vacíos
        if not brand:
            errores.append(f"FILA {fila}: BRAND VACÍO")

        if not model:
            errores.append(f"FILA {fila}: MODEL VACÍO")

        if pd.isna(coefficient) or str(coefficient).strip() == "":
            errores.append(f"FILA {fila}: COEFFICIENT VACÍO")
        else:
            try:
                float(coefficient)
            except ValueError:
                errores.append(f"FILA {fila}: COEFFICIENT NO ES NUMÉRICO")

    # 4️⃣ Validar duplicados conflictivos
    df["brand"] = df["brand"].astype(str).str.strip()
    df["model"] = df["model"].astype(str).str.strip()

    duplicados = df[df.duplicated(subset=["brand", "model"], keep=False)]

    for (brand, model), grupo in duplicados.groupby(["brand", "model"]):

        coef_unicos = grupo["coefficient"].astype(float).unique()

        if len(coef_unicos) > 1:
            errores.append(
                f"DUPLICADO CONFLICTIVO: {brand} {model} TIENE COEFICIENTES DISTINTOS {coef_unicos}"
            )

    # 5️⃣ Si hay errores → reportar todos y salir
    if errores:

        imprimir_mensaje("SE HAN DETECTADO ERRORES:", "red")

        for err in errores:
            imprimir_mensaje(err, "red")

        imprimir_mensaje("NO SE GENERA XML POR ERRORES.", "red")
        return

    # 6️⃣ Eliminar duplicados seguros (mismo coeficiente)
    df["coefficient"] = df["coefficient"].astype(float)
    df = df.drop_duplicates(subset=["brand", "model"], keep="first")

    imprimir_mensaje("DUPLICADOS SEGUROS ELIMINADOS.", "yellow")

    # 7️⃣ Generar XML
    imprimir_mensaje("GENERANDO XML...", "blue")

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

    # 8️⃣ Fallback
    ET.SubElement(coefficients, "coefficient", attrib={"value": "1.0"})

    tree = ET.ElementTree(service)
    tree.write(
        ruta_salida,
        encoding="utf-8",
        xml_declaration=True
    )

    imprimir_mensaje(f"XML GENERADO CORRECTAMENTE EN {ruta_salida}", "green")