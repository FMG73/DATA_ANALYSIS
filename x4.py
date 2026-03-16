import pandas as pd

def clean(value):
    """
    Convierte NaN, None o 'nan' en cadena vacía.
    Siempre devuelve un string válido.
    """
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() == "nan":
        return ""
    return value
