import xml.etree.ElementTree as ET
from xml.dom import minidom


def pretty_xml(element):
    rough = ET.tostring(element, encoding="utf-8")
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")


def crear_xml(row, namespace):

    root = ET.Element("CarData", {"schemaVersion": "0"})

    # Campos raíz
    for field in ["productFamily", "senderId", "senderReference", "sellerId", "backendSystem"]:
        ET.SubElement(root, field).text = str(row[field])

    # UNIT
    unit = ET.SubElement(root, "Unit", {"xmlns": namespace})

    # IDENTIFICATION → VEHICLE
    identification = ET.SubElement(unit, "Identification")
    vehicle = ET.SubElement(identification, "Vehicle")

    for field in ["vin", "registrationNumber", "owner", "sellersVehicleIdentifier", "backEndSystem"]:
        ET.SubElement(vehicle, field, {"xmlns": ""}).text = str(row[field])

    # IDENTIFICATION → MODEL
    model = ET.SubElement(identification, "Model")
    for field in ["vehicleCategory", "brand", "model", "modelNameLocal", "specCommercialName", "modelYear"]:
        ET.SubElement(model, field, {"xmlns": ""}).text = str(row[field])

    # MODEL DETAILS
    model_details = ET.SubElement(unit, "ModelDetails")

    engine = ET.SubElement(model_details, "Engine")
    ET.SubElement(engine, "engineSize", {"UOM": str(row["engineSize_UOM"]), "xmlns": ""}).text = str(row["engineSize"])
    ET.SubElement(engine, "power", {"UOM": str(row["power_UOM"]), "xmlns": ""}).text = str(row["power"])
    ET.SubElement(engine, "mainEnergy", {"xmlns": ""}).text = str(row["mainEnergy"])

    transmission = ET.SubElement(model_details, "Transmission")
    ET.SubElement(transmission, "gearType", {"xmlns": ""}).text = str(row["gearType"])
    ET.SubElement(transmission, "nrOfGears", {"xmlns": ""}).text = str(row["nrOfGears"])
    ET.SubElement(transmission, "fourWheelDrive", {"xmlns": ""}).text = str(row["fourWheelDrive"])

    body = ET.SubElement(model_details, "Body")
    ET.SubElement(body, "steeringLeftSide", {"xmlns": ""}).text = str(row["steeringLeftSide"])
    ET.SubElement(body, "bodyType", {
        "LANG": str(row["bodyType_LANG"]),
        "TRANS": str(row["bodyType_TRANS"]),
        "xmlns": ""
    }).text = str(row["bodyType"])
    ET.SubElement(body, "nrOfDoors", {"xmlns": ""}).text = str(row["nrOfDoors"])
    ET.SubElement(body, "nrOfPax", {"xmlns": ""}).text = str(row["nrOfPax"])

    performance = ET.SubElement(model_details, "Performance")
    ET.SubElement(performance, "co2Emission", {
        "UOM": str(row["co2Emission_UOM"]),
        "xmlns": ""
    }).text = str(row["co2Emission"])

    tax1 = ET.SubElement(model_details, "Tax", {"xmlns": ""})
    ET.SubElement(tax1, "fiscalRating").text = str(row["fiscalRating"])
    ET.SubElement(tax1, "greenhouseGasEmissionClass").text = str(row["greenhouseGasEmissionClass"])

    # VEHICLE DETAILS
    details = ET.SubElement(unit, "VehicleDetails")

    tax2 = ET.SubElement(details, "Tax", {"xmlns": ""})
    ET.SubElement(tax2, "countryOfRegistration").text = str(row["countryOfRegistration"])
    ET.SubElement(tax2, "vatDeductible").text = str(row["vatDeductible"])

    availability = ET.SubElement(details, "Availability")
    for field in [
        "dateInStock", "requestRefNumber", "expectedInspectionDate",
        "dateInspectionRequest", "dateInspectionReport",
        "storageLocationCode", "storageLocationAddress"
    ]:
        ET.SubElement(availability, field, {"xmlns": ""}).text = str(row[field])

    pictures = ET.SubElement(details, "Pictures")
    ET.SubElement(pictures, "pictureURL", {"xmlns": ""}).text = str(row["pictureURL"])

    colors = ET.SubElement(details, "Colors")
    ET.SubElement(colors, "paintColor", {
        "LANG": str(row["paintColor_LANG"]),
        "TRANS": str(row["paintColor_TRANS"]),
        "xmlns": ""
    }).text = str(row["paintColor"])
    ET.SubElement(colors, "carmakersColor", {"xmlns": ""}).text = str(row["carmakersColor"])

    tyres = ET.SubElement(details, "Tyres")
    ET.SubElement(tyres, "tyrePosition", {"xmlns": ""}).text = str(row["tyre_position"])
    ET.SubElement(tyres, "tyreType", {"xmlns": ""}).text = str(row["tyre_type"])
    ET.SubElement(tyres, "tyreBrand", {"xmlns": ""}).text = str(row["tyre_brand"])
    ET.SubElement(tyres, "threadDepth", {
        "UOM": str(row["tyre_depth_UOM"]),
        "xmlns": ""
    }).text = str(row["tyre_depth"])

    equipment = ET.SubElement(details, "Equipment")
    ET.SubElement(equipment, "eqtType", {
        "LANG": str(row["equipment_type_LANG"]),
        "TRANS": str(row["equipment_type_TRANS"]),
        "xmlns": ""
    }).text = str(row["equipment_type"])
    ET.SubElement(equipment, "deliveredAs", {
        "LANG": str(row["equipment_deliveredAs_LANG"]),
        "TRANS": str(row["equipment_deliveredAs_TRANS"]),
        "xmlns": ""
    }).text = str(row["equipment_deliveredAs"])

    history = ET.SubElement(details, "History")
    ET.SubElement(history, "firstDrive", {"xmlns": ""}).text = str(row["firstDrive"])
    ET.SubElement(history, "mileage", {"UOM": str(row["mileage_UOM"]), "xmlns": ""}).text = str(row["mileage"])
    ET.SubElement(history, "dateMileageCollected", {"xmlns": ""}).text = str(row["dateMileageCollected"])

    condition = ET.SubElement(details, "Condition")
    ET.SubElement(condition, "inspectionCompany", {"xmlns": ""}).text = str(row["inspectionCompany"])
    ET.SubElement(condition, "reportURL", {"xmlns": ""}).text = str(row["reportURL"])
    ET.SubElement(condition, "estCostBodyRepair", {"xmlns": ""}).text = str(row["estCostBodyRepair"])
    ET.SubElement(condition, "estCostGlassRepair", {"xmlns": ""}).text = str(row["estCostGlassRepair"])
    ET.SubElement(condition, "estCostTyresRepair", {"xmlns": ""}).text = str(row["estCostTyresRepair"])
    ET.SubElement(condition, "justifURL", {"xmlns": ""}).text = str(row["justifURL"])
    ET.SubElement(condition, "nrOfKeys", {"xmlns": ""}).text = str(row["nrOfKeys"])

    missing = ET.SubElement(condition, "Missing")
    ET.SubElement(missing, "includedElement", {
        "LANG": str(row["missing_element_LANG"]),
        "TRANS": str(row["missing_element_TRANS"]),
        "xmlns": ""
    }).text = str(row["missing_element"])

    damage = ET.SubElement(condition, "Damage")
    ET.SubElement(damage, "damagedPart", {
        "LANG": str(row["damage_part_LANG"]),
        "TRANS": str(row["damage_part_TRANS"]),
        "xmlns": ""
    }).text = str(row["damage_part"])

    ET.SubElement(damage, "natureOfDamage", {
        "LANG": str(row["damage_nature_LANG"]),
        "TRANS": str(row["damage_nature_TRANS"]),
        "xmlns": ""
    }).text = str(row["damage_nature"])

    ET.SubElement(damage, "damageRepair", {
        "LANG": str(row["damage_repair_LANG"]),
        "TRANS": str(row["damage_repair_TRANS"]),
        "xmlns": ""
    }).text = str(row["damage_repair"])

    ET.SubElement(damage, "pictureURL", {"xmlns": ""}).text = str(row["damage_picture1"])
    ET.SubElement(damage, "pictureURL", {"xmlns": ""}).text = str(row["damage_picture2"])

    recond = ET.SubElement(condition, "RecondCost")
    ET.SubElement(recond, "estimatedCostOfReconditioning", {
        "UOM": str(row["estimatedCostOfReconditioning_UOM"]),
        "xmlns": ""
    }).text = str(row["estimatedCostOfReconditioning"])
    ET.SubElement(recond, "recoCostRefCountry", {
        "LANG": str(row["recoCostRefCountry_LANG"]),
        "TRANS": str(row["recoCostRefCountry_TRANS"]),
        "xmlns": ""
    }).text = str(row["recoCostRefCountry"])

    prices = ET.SubElement(unit, "Prices")
    ref_price = ET.SubElement(prices, "ReferencePrice")
    ET.SubElement(ref_price, "referencePriceAmount", {
        "UOM": str(row["referencePriceAmount_UOM"]),
        "xmlns": ""
    }).text = str(row["referencePriceAmount"])
    ET.SubElement(ref_price, "referenceSource", {"xmlns": ""}).text = str(row["referenceSource"])

    return root
