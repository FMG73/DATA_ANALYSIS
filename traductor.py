import pandas as pd
from typing import Dict

def traducir_columnas(
    df: pd.DataFrame,
    mapeo_columnas: Dict[str, str],
    idioma_destino: str = "español",
    eliminar_unnamed: bool = True,
    elevar_error: bool = True
) -> pd.DataFrame:
    """
    Traduce las columnas del DataFrame según el diccionario proporcionado.
    Elimina columnas que empiezan por "Unnamed" y valida que todas las columnas estén en el diccionario.

    Args:
        df: DataFrame de pandas.
        mapeo_columnas: Diccionario de mapeo {ingles: español}.
        idioma_destino: "ingles" o "español" (por defecto "español").
        eliminar_unnamed: Si True, elimina columnas que empiezan por "Unnamed".
        elevar_error: Si True, eleva un error si hay columnas no encontradas en el diccionario.

    Returns:
        DataFrame con las columnas traducidas.

    Raises:
        ValueError: Si `elevar_error=True` y hay columnas no encontradas en el diccionario.
    """

    # Copia para evitar modificar el original
    df = df.copy()

    # Eliminar columnas que empiezan por "Unnamed" (robusto ante tipos raros)
    if eliminar_unnamed:
        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

    # Definir columnas válidas y mapeo según idioma destino
    if idioma_destino == "español":
        columnas_validas = set(mapeo_columnas.keys())
        mapeo_a_aplicar = mapeo_columnas

    elif idioma_destino == "ingles":
        columnas_validas = set(mapeo_columnas.values())
        mapeo_a_aplicar = {v: k for k, v in mapeo_columnas.items()}

    else:
        raise ValueError("Idioma destino no válido. Usa 'ingles' o 'español'.")

    # Validación de columnas (más eficiente y pythonic)
    columnas_no_encontradas = [
        col for col in df.columns if col not in columnas_validas
    ]

    if columnas_no_encontradas and elevar_error:
        raise ValueError(
            f"Columnas no encontradas en el diccionario: {columnas_no_encontradas}"
        )

    # Renombrado
    df_traducido = df.rename(columns=mapeo_a_aplicar)

    return df_traducido