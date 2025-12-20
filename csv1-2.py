import os
import glob
import pandas as pd


def unir_csv_validacion_estricta(
    carpetas_ataque,
    mascara_archivos,
    archivo_salida,
    diccionario_columnas=None,
    encoding_csv="ANSI",
    columnas_eliminar=None
):
    """
    Une múltiples archivos CSV en un único CSV final, con validación estricta
    de columnas y limpieza automática de columnas no deseadas.

    Parámetros
    ----------
    carpetas_ataque : str | list[str]
        Ruta de una carpeta o lista de carpetas donde se buscarán los CSV.

    mascara_archivos : str
        Patrón de búsqueda de archivos (ejemplo: "*.csv", "ventas_*.csv").

    archivo_salida : str
        Ruta completa del archivo CSV de salida.

    diccionario_columnas : dict | None, opcional
        Diccionario maestro de columnas para validación estricta.
        Si es None, no se realiza validación.

        Ejemplo:
        {
            "fecha": "FECHA",
            "ventas": "VENTAS"
        }

    encoding_csv : str, opcional
        Encoding de lectura y escritura de los CSV.
        Por defecto "ANSI".

    columnas_eliminar : list[str] | None, opcional
        Lista de nombres EXACTOS de columnas a eliminar si existen.
        Ejemplo: ["OBS", "COMENTARIOS"]

    Retorna
    -------
    pandas.DataFrame
        DataFrame combinado final.
    """

    # ---------------------------------------------------------
    # 1. Normalizar carpetas_ataque a lista
    # ---------------------------------------------------------
    if isinstance(carpetas_ataque, str):
        carpetas_ataque = [carpetas_ataque]

    # ---------------------------------------------------------
    # 2. Buscar todos los CSV en las carpetas indicadas
    # ---------------------------------------------------------
    archivos_csv = []

    for carpeta in carpetas_ataque:
        ruta_busqueda = os.path.join(carpeta, mascara_archivos)
        archivos_encontrados = glob.glob(ruta_busqueda)
        archivos_csv.extend(archivos_encontrados)

    # Si no se encuentra ningún archivo CSV, se detiene el proceso
    if not archivos_csv:
        raise FileNotFoundError(
            "No se encontraron archivos CSV con la máscara indicada "
            "en las carpetas proporcionadas."
        )

    # ---------------------------------------------------------
    # 3. VALIDACIÓN ESTRICTA DE COLUMNAS (si se proporciona diccionario)
    # ---------------------------------------------------------
    if diccionario_columnas is not None:
        # Conjunto de columnas esperadas (nombres reales)
        columnas_esperadas = set(diccionario_columnas.values())

        for archivo in archivos_csv:
            # Leer SOLO la cabecera del CSV (máxima eficiencia)
            cabecera = pd.read_csv(
                archivo,
                sep=";",
                encoding=encoding_csv,
                nrows=0
            ).columns

            columnas_actuales = set(cabecera)

            # Columnas faltantes y sobrantes
            faltantes = columnas_esperadas - columnas_actuales
            sobrantes = columnas_actuales - columnas_esperadas

            # Si hay cualquier diferencia, se aborta todo el proceso
            if faltantes or sobrantes:
                raise ValueError(
                    f"Validación estricta fallida en el archivo:\n{archivo}\n\n"
                    f"Columnas faltantes: {sorted(faltantes)}\n"
                    f"Columnas sobrantes: {sorted(sobrantes)}"
                )

    # ---------------------------------------------------------
    # 4. CARGA Y LIMPIEZA DE CSV + CONCATENACIÓN
    # ---------------------------------------------------------
    dataframes = []

    for archivo in archivos_csv:
        # Leer el CSV completo
        df = pd.read_csv(
            archivo,
            sep=";",
            encoding=encoding_csv,
            decimal=",",
            thousands=".",
            low_memory=False
        )

        # -----------------------------------------------------
        # 4.1 Eliminar columnas que empiecen por 'unnamed'
        #     (sin importar mayúsculas/minúsculas)
        # -----------------------------------------------------
        df = df.loc[:, ~df.columns.str.lower().str.startswith("unnamed")]

        # -----------------------------------------------------
        # 4.2 Eliminar columnas por nombre EXACTO (si se indica)
        # -----------------------------------------------------
        if columnas_eliminar:
            df = df.drop(columns=columnas_eliminar, errors="ignore")

        dataframes.append(df)

    # Concatenar todos los DataFrames
    df_combinado = pd.concat(dataframes, ignore_index=True)

    # ---------------------------------------------------------
    # 5. GUARDAR CSV FINAL
    # ---------------------------------------------------------
    df_combinado.to_csv(
        archivo_salida,
        index=False,
        sep=";",
        encoding=encoding_csv,
        decimal=","
    )

    return df_combinado