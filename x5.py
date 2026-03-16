import xml.etree.ElementTree as ET
from xml.dom import minidom
import pandas as pd


# ---------------------------------------------------------
# LIMPIEZA DE VALORES
# ---------------------------------------------------------

def clean(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() == "nan":
        return ""
    return value


# ---------------------------------------------------------
# XML BONITO
# ---------------------------------------------------------

def pretty_xml(element):
    rough = ET.tostring(element, encoding="utf-8")
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")


# ---------------------------------------------------------
# CREAR XML
# ---------------------------------------------------------

def crear_xml(row, namespace):

    root = ET.Element("CarData", {"schemaVersion": "0"})

    # Campos raíz
    for field in ["productFamily", "senderId", "senderReference", "sellerId", "backendSystem"]:
        ET.SubElement(root, field).text = clean(row[field])

    # UNIT
    unit = ET.SubElement(root, "Unit", {"xmlns": namespace})

    # IDENTIFICATION → VEHICLE
    identification = ET.SubElement(unit, "Identification")
    vehicle = ET.SubElement(identification, "Vehicle")

    for field in ["vin", "registrationNumber", "owner", "sellersVehicleIdentifier", "backEndSystem"]:
        ET.SubElement(vehicle, field, {"xmlns": ""}).text = clean(row[field])

    # IDENTIFICATION → MODEL
    model = ET.SubElement(identification, "Model")
    for field in ["vehicleCategory", "brand", "model", "modelNameLocal", "specCommercialName", "modelYear"]:
        ET.SubElement(model, field, {"xmlns": ""}).text = clean(row[field])

    # MODEL DETAILS
    model_details = ET.SubElement(unit, "ModelDetails")

    engine = ET.SubElement(model_details, "Engine")
    ET.SubElement(engine, "engineSize", {"UOM": clean(row["engineSize_UOM"]), "xmlns": ""}).text = clean(row["engineSize"])
    ET.SubElement(engine, "power", {"UOM": clean(row["power_UOM"]), "xmlns": ""}).text = clean(row["power"])
    ET.SubElement(engine, "mainEnergy", {"xmlns": ""}).text = clean(row["mainEnergy"])

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
    ET.SubElement(performance, "co2Emission", {
        "UOM": clean(row["co2Emission_UOM"]),
        "xmlns": ""
    }).text = clean(row["co2Emission"])

    tax1 = ET.SubElement(model_details, "Tax", {"xmlns": ""})
    ET.SubElement(tax1, "fiscalRating").text = clean(row["fiscalRating"])
    ET.SubElement(tax1, "greenhouseGasEmissionClass").text = clean(row["greenhouseGasEmissionClass"])

    # VEHICLE DETAILS
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

    tyres = ET.SubElement(details, "Tyres")
    ET.SubElement(tyres, "tyrePosition", {"xmlns": ""}).text = clean(row["tyre_position"])
    ET.SubElement(tyres, "tyreType", {"xmlns": ""}).text = clean(row["tyre_type"])
    ET.SubElement(tyres, "tyreBrand", {"xmlns": ""}).text = clean(row["tyre_brand"])
    ET.SubElement(tyres, "threadDepth", {
        "UOM": clean(row["tyre_depth_UOM"]),
        "xmlns": ""
    }).text = clean(row["tyre_depth"])

    equipment = ET.SubElement(details, "Equipment")
    ET.SubElement(equipment, "eqtType", {
        "LANG": clean(row["equipment_type_LANG"]),
        "TRANS": clean(row["equipment_type_TRANS"]),
        "xmlns": ""
    }).text = clean(row["equipment_type"])
    ET.SubElement(equipment, "deliveredAs", {
        "LANG": clean(row["equipment_deliveredAs_LANG"]),
        "TRANS": clean(row["equipment_deliveredAs_TRANS"]),
        "xmlns": ""
    }).text = clean(row["equipment_deliveredAs"])

    history = ET.SubElement(details, "History")
    ET.SubElement(history, "firstDrive", {"xmlns": ""}).text = clean(row["firstDrive"])
    ET.SubElement(history, "mileage", {"UOM": clean(row["mileage_UOM"]), "xmlns": ""}).text = clean(row["mileage"])
    ET.SubElement(history, "dateMileageCollected", {"xmlns": ""}).text = clean(row["dateMileageCollected"])

    condition = ET.SubElement(details, "Condition")
    ET.SubElement(condition, "inspectionCompany", {"xmlns": ""}).text = clean(row["inspectionCompany"])
    ET.SubElement(condition, "reportURL", {"xmlns": ""}).text = clean(row["reportURL"])
    ET.SubElement(condition, "estCostBodyRepair", {"xmlns": ""}).text = clean(row["estCostBodyRepair"])
    ET.SubElement(condition, "estCostGlassRepair", {"xmlns": ""}).text = clean(row["estCostGlassRepair"])
    ET.SubElement(condition, "estCostTyresRepair", {"xmlns": ""}).text = clean(row["estCostTyresRepair"])
    ET.SubElement(condition, "justifURL", {"xmlns": ""}).text = clean(row["justifURL"])
    ET.SubElement(condition, "nrOfKeys", {"xmlns": ""}).text = clean(row["nrOfKeys"])

    missing = ET.SubElement(condition, "Missing")
    ET.SubElement(missing, "includedElement", {
        "LANG": clean(row["missing_element_LANG"]),
        "TRANS": clean(row["missing_element_TRANS"]),
        "xmlns": ""
    }).text = clean(row["missing_element"])

    damage = ET.SubElement(condition, "Damage")
    ET.SubElement(damage, "damagedPart", {
        "LANG": clean(row["damage_part_LANG"]),
        "TRANS": clean(row["damage_part_TRANS"]),
        "xmlns": ""
    }).text = clean(row["damage_part"])

    ET.SubElement(damage, "natureOfDamage", {
        "LANG": clean(row["damage_nature_LANG"]),
        "TRANS": clean(row["damage_nature_TRANS"]),
        "xmlns": ""
    }).text = clean(row["damage_nature"])

    ET.SubElement(damage, "damageRepair", {
        "LANG": clean(row["damage_repair_LANG"]),
        "TRANS": clean(row["damage_repair_TRANS"]),
        "xmlns": ""
    }).text = clean(row["damage_repair"])

    ET.SubElement(damage, "pictureURL", {"xmlns": ""}).text = clean(row["damage_picture1"])
    ET.SubElement(damage, "pictureURL", {"xmlns": ""}).text = clean(row["damage_picture2"])

    recond = ET.SubElement(condition, "RecondCost")
    ET.SubElement(recond, "estimatedCostOfReconditioning", {
        "UOM": clean(row["estimatedCostOfReconditioning_UOM"]),
        "xmlns": ""
    }).text = clean(row["estimatedCostOfReconditioning"])
    ET.SubElement(recond, "recoCostRefCountry", {
        "LANG": clean(row["recoCostRefCountry_LANG"]),
        "TRANS": clean(row["recoCostRefCountry_TRANS"]),
        "xmlns": ""
    }).text = clean(row["recoCostRefCountry"])

    prices = ET.SubElement(unit, "Prices")
    ref_price = ET.SubElement(prices, "ReferencePrice")
    ET.SubElement(ref_price, "referencePriceAmount", {
        "UOM": clean(row["referencePriceAmount_UOM"]),
        "xmlns": ""
    }).text = clean(row["referencePriceAmount"])
    ET.SubElement(ref_price, "referenceSource", {"xmlns": ""}).text = clean(row["referenceSource"])

    return root
