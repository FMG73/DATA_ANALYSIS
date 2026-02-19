import pandas as pd
import os


def concatenar_csv_validado(lista_rutas: list,
                            ruta_salida: str,
                            sep: str = ",",
                            encoding: str = "utf-8") -> None:
    """
    Concatena una lista de archivos CSV validando que:
    - Todas las columnas sean exactamente iguales
    - Estén en el mismo orden
    - Los datos se lean como str

    Guarda el resultado en un nuevo CSV.

    Parámetros
    ----------
    lista_rutas : list
        Lista de rutas completas de los archivos CSV.
    ruta_salida : str
        Ruta donde se guardará el CSV final.
    sep : str, opcional
        Separador del CSV.
    encoding : str, opcional
        Codificación del archivo.
    """

    if not lista_rutas:
        raise ValueError("La lista de archivos está vacía.")

    dataframes = []
    columnas_base = None

    for ruta in lista_rutas:

        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No existe el archivo: {ruta}")

        # Leer todo como string
        df = pd.read_csv(
            ruta,
            sep=sep,
            encoding=encoding,
            dtype=str
        )

        # Validar columnas
        if columnas_base is None:
            columnas_base = df.columns.tolist()
        else:
            if df.columns.tolist() != columnas_base:
                raise ValueError(
                    f"Las columnas no coinciden o no están en el mismo orden en el archivo:\n{ruta}"
                )

        dataframes.append(df)

    df_final = pd.concat(dataframes, ignore_index=True)

    # Guardar también como string
    df_final.to_csv(
        ruta_salida,
        index=False,
        sep=sep,
        encoding=encoding
    )

    print(f"Archivo guardado correctamente en: {ruta_salida}")