import pandas as pd

def limpiar_comillas(
    df: pd.DataFrame,
    columnas: list[str],
    eliminar_comillas_internas: bool = False
) -> pd.DataFrame:
    """
    Limpia comillas en columnas de texto de un DataFrame.

    - Elimina comillas al inicio y final del texto
    - Opcionalmente elimina comillas internas
    - Mantiene NaN
    """

    df = df.copy()

    for col in columnas:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip('"')
        )

        if eliminar_comillas_internas:
            df[col] = df[col].str.replace('"', '', regex=False)

    return df