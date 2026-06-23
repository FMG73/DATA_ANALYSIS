import pandas as pd
import chardet
from tkinter import Tk, filedialog
from pathlib import Path
from datetime import datetime

import xml.etree.ElementTree as ET
from xml.dom import minidom

required_fields = ["vin","registrationNumber",]
fecha_actual = datetime.now().strftime("%Y-%m-%d")

def archivo_ventana_abrir(titulo = 'SELECCIONA ARCHIVO',tipo_archivo="todos"):

    Tk().withdraw()

    if tipo_archivo == "excel":
        filetypes = [('EXCEL', '*.xls;*.xlsx')]
    elif tipo_archivo == "csv":
        filetypes = [('CSV', '*.csv')]
    else:
        filetypes = [('EXCEL', '*.xls;*.xlsx'),('CSV', '*.csv'),('TODOS', '*.*')]

    filename = filedialog.askopenfilename(title=titulo,filetypes=filetypes,initialdir=r'C:\Users\a33300\OneDrive - BNP Paribas\Bureau\TMP')
    return Path(filename)

def archivo_encoding_leer(ruta_ataque):
    archivo_objeto = Path(ruta_ataque)
    try:
        with open(archivo_objeto, 'rb') as f:
            rawdata = f.read(10000)
            codigo = chardet.detect(rawdata)
            encoding = codigo['encoding']
            print(f'\n{archivo_objeto.name} DETECTADO CON ENCODING {encoding}')
        return encoding
    except Exception as e:
        input(f'ERROR AL INTENTAR AVERIGUAR ENCODING DE {archivo_objeto.name}.\nERROR:\n{e}\n')

def clean(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() == "nan":
        return ""
    return value

def validar_fila(row, required_fields):
    for field in required_fields:
        if pd.isna(row[field]) or str(row[field]).strip() == "":
            print(f"⚠️  Campo obligatorio vacío en {row['registrationNumber']}: {field}")

def pretty_xml(element):
    rough = ET.tostring(element, encoding="utf-8")
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")

def crear_xml(row, namespace):
    root = ET.Element("CarData", {"schemaVersion": "0"})

    for field in ["productFamily", "senderId", "senderReference", "sellerId", "backendSystem"]:
        ET.SubElement(root, field).text = clean(row[field])

    unit = ET.SubElement(root, "Unit", {"xmlns": namespace})

    identification = ET.SubElement(unit, "Identification")
    vehicle = ET.SubElement(identification, "Vehicle")

    for field in ["vin", "registrationNumber", "owner", "backEndSystem"]:
        ET.SubElement(vehicle, field, {"xmlns": ""}).text = clean(row[field])

    model = ET.SubElement(identification, "Model")
    for field in ["vehicleCategory", "brand", "model", "modelNameLocal", "specCommercialName"]:
        ET.SubElement(model, field, {"xmlns": ""}).text = clean(row[field])

    model_details = ET.SubElement(unit, "ModelDetails")

    engine = ET.SubElement(model_details, "Engine")

    # ---------------- POWER (UOM + xmlns en orden correcto) ----------------
    power = ET.Element("power", {
        "UOM": clean(row["power_UOM"]),
        "xmlns": ""
    })
    power.text = clean(row["power"])
    engine.append(power)

    mainEnergy = ET.SubElement(engine, "mainEnergy", {"xmlns": ""})
    mainEnergy.text = clean(row["mainEnergy"])

    transmission = ET.SubElement(model_details, "Transmission")
    ET.SubElement(transmission, "gearType", {"xmlns": ""}).text = clean(row["gearType"])
    ET.SubElement(transmission, "nrOfGears", {"xmlns": ""}).text = clean(row["nrOfGears"])
    ET.SubElement(transmission, "fourWheelDrive", {"xmlns": ""}).text = clean(row["fourWheelDrive"])

    body = ET.SubElement(model_details, "Body")
    ET.SubElement(body, "steeringLeftSide", {"xmlns": ""}).text = clean(row["steeringLeftSide"])
    ET.SubElement(body, "bodyType", {
        "LANG": clean(row["bodyType_LANG"]),
        "TRANS": clean(row["bodyType_TRANS"]),
        "xmlns": ""
    }).text = clean(row["bodyType"])
    ET.SubElement(body, "nrOfDoors", {"xmlns": ""}).text = clean(row["nrOfDoors"])
    ET.SubElement(body, "nrOfPax", {"xmlns": ""}).text = clean(row["nrOfPax"])

    performance = ET.SubElement(model_details, "Performance")

    # ---------------- CO2 (UOM + xmlns en orden correcto) ----------------
    co2 = ET.Element("co2Emission", {
        "UOM": clean(row["co2Emission_UOM"]),
        "xmlns": ""
    })
    co2.text = clean(row["co2Emission"])
    performance.append(co2)

    tax1 = ET.SubElement(model_details, "Tax", {"xmlns": ""})
    ET.SubElement(tax1, "fiscalRating").text = clean(row["fiscalRating"])
    ET.SubElement(tax1, "greenhouseGasEmissionClass").text = clean(row["greenhouseGasEmissionClass"])

    details = ET.SubElement(unit, "VehicleDetails")
    tax2 = ET.SubElement(details, "Tax", {"xmlns": ""})
    ET.SubElement(tax2, "countryOfRegistration").text = clean(row["countryOfRegistration"])
    ET.SubElement(tax2, "vatDeductible").text = clean(row["vatDeductible"])

    availability = ET.SubElement(details, "Availability")
    for field in [
        "dateInStock", "requestRefNumber", "expectedInspectionDate",
        "dateInspectionRequest", "dateInspectionReport",
        "storageLocationCode", "storageLocationAddress"
    ]:
        ET.SubElement(availability, field, {"xmlns": ""}).text = clean(row[field])

    pictures = ET.SubElement(details, "Pictures")
    ET.SubElement(pictures, "pictureURL", {"xmlns": ""}).text = clean(row["pictureURL"])

    colors = ET.SubElement(details, "Colors")
    ET.SubElement(colors, "paintColor", {
        "LANG": clean(row["paintColor_LANG"]),
        "TRANS": clean(row["paintColor_TRANS"]),
        "xmlns": ""
    }).text = clean(row["paintColor"])
    ET.SubElement(colors, "carmakersColor", {"xmlns": ""}).text = clean(row["carmakersColor"])

    history = ET.SubElement(details, "History")
    ET.SubElement(history, "firstDrive", {"xmlns": ""}).text = clean(row["firstDrive"])

    # ---------------- MILEAGE (UOM + xmlns en orden correcto) ----------------
    mileage = ET.Element("mileage", {
        "UOM": "km",
        "xmlns": ""
    })
    mileage.text = clean(row.get("mileage", ""))
    history.append(mileage)

    ET.SubElement(history, "dateMileageCollected", {"xmlns": ""}).text = clean(row["dateMileageCollected"])

    return root

def preparar_dataframe(df_origen):

    df_origen["FECHA DE MATRICULACIÓN"] = pd.to_datetime(
        df_origen["FECHA DE MATRICULACIÓN"], format='%d/%m/%Y',
        errors='coerce'
    ).dt.strftime('%Y-%m-%d')

    column_mapping = {
        "VIN": "vin",
        "MATRICULA": "registrationNumber",
        "CATEGORIA DEL VEHICULO": "vehicleCategory",
        "MARCA": "brand",
        "MODELO": "model",
        "NOMBRE COMERCIAL": "specCommercialName",
        "POTENCIA": "power",
        "POTENCIA UNIDAD": "power_UOM",
        "ENERGIA PRINCIPAL": "mainEnergy",
        "TRANSMISION": "gearType",
        "TIPO DE CARROCERIA": "bodyType",
        "Nº PUERTAS": "nrOfDoors",
        "LOCALIZACION DEL VEHICULO": "storageLocationAddress",
        "COLOR MT": "paintColor",
        "COLOR FABRICANTE": "carmakersColor",
        "FECHA DE MATRICULACIÓN": "firstDrive",
        "KM": "mileage"
    }

    df = df_origen.rename(columns=column_mapping)

    columnas_esperadas = [
        "productFamily", "senderId", "senderReference", "sellerId", "backendSystem",
        "vin", "registrationNumber", "owner", "sellersVehicleIdentifier", "backEndSystem",
        "vehicleCategory", "brand", "model", "modelNameLocal", "specCommercialName", "modelYear",
        "engineSize", "engineSize_UOM", "power", "power_UOM", "mainEnergy",
        "gearType", "nrOfGears", "fourWheelDrive",
        "steeringLeftSide", "bodyType", "bodyType_LANG", "bodyType_TRANS", "nrOfDoors", "nrOfPax",
        "co2Emission", "co2Emission_UOM",
        "fiscalRating", "greenhouseGasEmissionClass",
        "countryOfRegistration", "vatDeductible",
        "dateInStock", "requestRefNumber", "expectedInspectionDate",
        "dateInspectionRequest", "dateInspectionReport", "storageLocationCode", "storageLocationAddress",
        "pictureURL",
        "paintColor", "paintColor_LANG", "paintColor_TRANS", "carmakersColor",
        "tyre_position", "tyre_type", "tyre_brand", "tyre_depth", "tyre_depth_UOM",
        "equipment_type", "equipment_type_LANG", "equipment_type_TRANS",
        "equipment_deliveredAs", "equipment_deliveredAs_LANG", "equipment_deliveredAs_TRANS",
        "firstDrive", "mileage", "mileage_UOM", "dateMileageCollected",
        "inspectionCompany", "reportURL", "estCostBodyRepair", "estCostGlassRepair",
        "estCostTyresRepair", "justifURL", "nrOfKeys",
        "missing_element", "missing_element_LANG", "missing_element_TRANS",
        "damage_part", "damage_part_LANG", "damage_part_TRANS",
        "damage_nature", "damage_nature_LANG", "damage_nature_TRANS",
        "damage_repair", "damage_repair_LANG", "damage_repair_TRANS",
        "damage_picture1", "damage_picture2",
        "estimatedCostOfReconditioning", "estimatedCostOfReconditioning_UOM",
        "recoCostRefCountry", "recoCostRefCountry_LANG", "recoCostRefCountry_TRANS",
        "referencePriceAmount", "referencePriceAmount_UOM", "referenceSource"
    ]

    for columna in columnas_esperadas:
        if columna not in df.columns:
            df[columna] = ""

    df["productFamily"] = "cars"
    df["senderId"] = "Macadam"
    df["senderReference"] = "FR"
    df["sellerId"] = "000051"
    df["backendSystem"] = "DRIVE_ES"
    df["backEndSystem"] = "DRIVE_ES"
    df["storageLocationCode"] = "INSITU"
    df['owner'] = 'ArvalSpain'
    df["steeringLeftSide"] = "true"
    df["countryOfRegistration"]= "ES"
    df["vatDeductible"] = 'true'
    df["dateInStock"] = fecha_actual
    df["pictureURL"] = "https://www4.macadam.eu/picture/8e50b7a1-9aa5-4b9d-9135-7715b13c4806.jpg"

    return df

archivo = archivo_ventana_abrir(
    titulo='SELECCIONA ARCHIVO PARA CREAR XML PARA CREAR ITEM EN MOTORTRADE',
    tipo_archivo='csv'
)

encoding = archivo_encoding_leer(archivo)

df_original = pd.read_csv(archivo, sep=";", encoding=encoding)

df = preparar_dataframe(df_original)

seen = {}

for _, row in df.iterrows():

    validar_fila(row, required_fields)
    matricula = str(row["registrationNumber"]).replace(" ", "").upper()

    if matricula not in seen:
        seen[matricula] = 1
        filename = f"{matricula}.xml"
    else:
        seen[matricula] += 1
        filename = f"{matricula}_{seen[matricula]}.xml"
        print(f"⚠️  Matrícula duplicada detectada: {matricula}. Generando {filename}")

    xml_root = crear_xml(row, "http://www.arval.com/Silverstone/CarDataUnit/1.0")
    xml_text = pretty_xml(xml_root)

    filename = f"{matricula}.xml"

    path = Path(r'C:\Python\JupyterLab\Lab\MELERO_TEST\xml_crear_item') / filename
    path.write_text(xml_text, encoding="utf-8")

    print(f"✅ XML generado: {path}")
