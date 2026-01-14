import pandas as pd
import re

def limpiar_texto_usuario(df, columnas, permitidos=CARACTERES_PERMITIDOS):
    """
    Limpia texto pegado por usuarios usando whitelist de caracteres.
    """

    patron_permitidos = (
        permitidos["letras"]
        + permitidos["numeros"]
        + permitidos["espacios"]
        + permitidos["puntuacion"]
        + permitidos["moneda"]
        + permitidos["porcentaje"]
    )

    patron_regex = rf"[^{patron_permitidos}]"

    df = df.copy()

    for col in columnas:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r'[\r\n\t]', ' ', regex=True)
            .str.replace('\xa0', ' ', regex=False)
            .str.replace(patron_regex, '', regex=True)
            .str.replace(r'\s+', ' ', regex=True)
            .str.strip()
        )

    return df