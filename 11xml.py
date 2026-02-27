import pandas as pd
import xml.etree.ElementTree as ET
from melvive.funciones import imprimir_mensaje


def generar_xml_desde_excel(ruta_entrada: str, ruta_salida: str) -> None:
    """
    GENERA UN ARCHIVO XML A PARTIR DE UN EXCEL O CSV CON COEFICIENTES POR MARCA Y MODELO.

    LA ESTRUCTURA XML CREADA ES:
    <service type="transport">
        <coefficients>
            <coefficient value="...">
                <conditions>
                    <ifAll>
                        <property name="item.brand">...</property>
                        <property name="item.model">...</property>
                    </ifAll>
                </conditions>
            </coefficient>
            ...
            <coefficient value="1.0"/>  # fallback
        </coefficients>
    </service>

    PARÁMETROS:
    -----------
    ruta_entrada : str
        Ruta del archivo Excel (.xlsx) o CSV (.csv) que contiene las columnas:
        - brand   : nombre de la marca (str)
        - model   : nombre del modelo (str)
        - coefficient : valor numérico del coeficiente (float)
    ruta_salida : str
        Ruta donde se guardará el XML generado.

    FUNCIONALIDADES:
    ----------------
    1. Valida que existan las columnas obligatorias.
    2. Limpia filas con valores nulos y elimina espacios al inicio/final.
    3. Detecta duplicados por (brand, model):
       - Si coeficientes son iguales → elimina duplicados automáticamente.
       - Si coeficientes son distintos → lanza error y detiene ejecución.
    4. Genera XML con todos los coeficientes válidos.
    5. Añade fallback con value=1.0 al final.
    6. Imprime mensajes en consola usando la función `imprimir_mensaje` con colores:
       - blue   → info/progreso
       - yellow → advertencias/duplicados
       - red    → errores críticos
       - green  → confirmación de éxito
       Todos los textos se muestran en mayúsculas.
    """

    # Mensaje inicial
    imprimir_mensaje("LEYENDO ARCHIVO...", "blue")

    # 1️⃣ Leer archivo (CSV o Excel)
    if ruta_entrada.endswith(".csv"):
        df = pd.read_csv(ruta_entrada, encoding="utf-8")
    else:
        df = pd.read_excel(ruta_entrada)

    # 2️⃣ Validar columnas obligatorias
    columnas_necesarias = {"brand", "model", "coefficient"}
    if not columnas_necesarias.issubset(df.columns):
        imprimir_mensaje(
            f"ERROR: FALTAN COLUMNAS OBLIGATORIAS {columnas_necesarias}", "red"
        )
        raise ValueError("Columnas obligatorias no encontradas")

    # 3️⃣ Limpieza básica de datos
    df = df.dropna(subset=["brand", "model", "coefficient"])
    df["brand"] = df["brand"].astype(str).str.strip()
    df["model"] = df["model"].astype(str).str.strip()
    df["coefficient"] = df["coefficient"].astype(float)

    imprimir_mensaje("VALIDANDO DUPLICADOS...", "blue")

    # 4️⃣ Detectar duplicados por brand + model
    duplicados = df[df.duplicated(subset=["brand", "model"], keep=False)]

    if not duplicados.empty:

        imprimir_mensaje("⚠️ DUPLICADOS DETECTADOS:", "yellow")

        for (brand, model), grupo in duplicados.groupby(["brand", "model"]):

            coef_unicos = grupo["coefficient"].unique()

            imprimir_mensaje(f"MARCA: {brand} | MODELO: {model}", "yellow")
            imprimir_mensaje(f"COEFICIENTES ENCONTRADOS: {coef_unicos}", "yellow")

            # Si hay coeficientes distintos → ERROR
            if len(coef_unicos) > 1:
                imprimir_mensaje(
                    f"❌ ERROR: {brand} {model} TIENE COEFICIENTES DISTINTOS {coef_unicos}", "red"
                )
                raise ValueError("CONFLICTO DE COEFICIENTES")

        # Eliminar duplicados seguros
        imprimir_mensaje(
            "DUPLICADOS CON MISMO COEFICIENTE ELIMINADOS AUTOMÁTICAMENTE.", "yellow"
        )
        df = df.drop_duplicates(subset=["brand", "model"], keep="first")

    # 5️⃣ Crear XML
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

    # 6️⃣ Fallback final
    ET.SubElement(coefficients, "coefficient", attrib={"value": "1.0"})

    # 7️⃣ Guardar XML
    tree = ET.ElementTree(service)
    tree.write(
        ruta_salida,
        encoding="utf-8",
        xml_declaration=True
    )

    imprimir_mensaje(f"✅ XML GENERADO CORRECTAMENTE EN {ruta_salida}", "green")