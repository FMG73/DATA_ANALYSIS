import pandas as pd
import tomllib
from pathlib import Path
from crear_xml import crear_xml, pretty_xml


def validar_fila(row, required_fields):
    for field in required_fields:
        if pd.isna(row[field]) or str(row[field]).strip() == "":
            print(f"⚠️  Campo obligatorio vacío en {row['registrationNumber']}: {field}")


def main():

    # Cargar config
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    OUTPUT = Path(config["output_folder"])
    OUTPUT.mkdir(exist_ok=True)

    REQUIRED = config["required_fields"]
    NAMESPACE = config["namespace_unit"]

    df = pd.read_excel("vehiculos.xlsx")

    # Para detectar duplicados
    seen = {}

    for _, row in df.iterrows():

        matricula = str(row["registrationNumber"]).replace(" ", "").upper()

        validar_fila(row, REQUIRED)

        # Detectar duplicados
        if matricula not in seen:
            seen[matricula] = 1
            filename = f"{matricula}.xml"
        else:
            seen[matricula] += 1
            filename = f"{matricula}_{seen[matricula]}.xml"
            print(f"⚠️  Matrícula duplicada detectada: {matricula}. Generando {filename}")

        xml_root = crear_xml(row, NAMESPACE)
        xml_text = pretty_xml(xml_root)

        path = OUTPUT / filename
        path.write_text(xml_text, encoding="utf-8")

        print(f"✅ XML generado: {path}")


if __name__ == "__main__":
    main()
