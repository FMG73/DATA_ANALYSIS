import os
import pandas as pd
from typing import Dict


def guardar_excel(
    ruta: str,
    dataframes: Dict[str, pd.DataFrame],
    modo: str = "auto",
    reemplazar_hoja: bool = True,
    index: bool = False,
) -> None:
    """
    Guarda uno o varios DataFrames en un archivo Excel, cada uno en una hoja distinta.

    Parameters
    ----------
    ruta : str
        Ruta completa del archivo Excel de salida.

    dataframes : Dict[str, pd.DataFrame]
        Diccionario donde:
            - key   -> nombre de la hoja
            - value -> DataFrame a guardar

    modo : str, optional (default="auto")
        Modo de escritura:
            - "w"     -> sobrescribe el archivo completo.
            - "a"     -> añade hojas al archivo existente.
            - "auto"  -> crea el archivo si no existe, si existe añade hojas.

    reemplazar_hoja : bool, optional (default=True)
        Si la hoja ya existe:
            - True  -> la reemplaza.
            - False -> lanza error.

    index : bool, optional (default=False)
        Indica si se guarda el índice del DataFrame.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        Si el modo no es válido.
    """

    if modo not in {"w", "a", "auto"}:
        raise ValueError("El parámetro 'modo' debe ser 'w', 'a' o 'auto'.")

    # Determinar modo real
    if modo == "auto":
        modo_real = "a" if os.path.exists(ruta) else "w"
    else:
        modo_real = modo

    # Configuración si la hoja existe
    if modo_real == "a":
        if_sheet_exists = "replace" if reemplazar_hoja else "error"
    else:
        if_sheet_exists = None

    with pd.ExcelWriter(
        ruta,
        engine="openpyxl",
        mode=modo_real,
        if_sheet_exists=if_sheet_exists
    ) as writer:

        for nombre_hoja, df in dataframes.items():
            df.to_excel(writer, sheet_name=nombre_hoja, index=index)

    print(f"✔ Archivo guardado correctamente en: {ruta}")