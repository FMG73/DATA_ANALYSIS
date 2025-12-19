import os
import glob
import pandas as pd
from typing import Union, List


def unir_csv_validando_columnas(
    carpetas_ataque: Union[str, List[str]],
    mascara_archivos: str,
    archivo_salida: str,
    diccionario_columnas: dict
):
    """
    Une múltiples archivos CSV ubicados en una o varias carpetas,
    validando previamente que TODOS los CSV tienen exactamente las
    mismas columnas definidas en un diccionario maestro.

    La validación se realiza leyendo SOLO la cabecera de cada archivo
    (nrows=0), lo que garantiza un rendimiento óptimo incluso con
    grandes volúmenes de CSV.

    Si algún archivo no cumple la estructura esperada:
        - NO se realiza la concatenación
        - Se informa detalladamente al usuario

    Parámetros
    ----------
    carpetas_ataque : str | list[str]
        Ruta o lista de rutas donde se encuentran los archivos CSV.

    mascara_archivos : str
        Máscara de búsqueda para los CSV (ej: '*.csv', 'ventas_*.csv').

    archivo_salida : str
        Ruta completa del archivo CSV resultante.

    diccionario_columnas : dict
        Diccionario maestro de columnas.
        IMPORTANTE: se validan los VALORES del diccionario
        (nombres reales de las columnas).

    Retorna
    -------
    pandas.DataFrame | None
        DataFrame concatenado si la validación es correcta.
        None si falla la validación de columnas.
    """

    # ------------------------------------------------------------------
    # 1. Normalizar entrada: siempre trabajar con lista de carpetas
    # ------------------------------------------------------------------
    if isinstance(carpetas_ataque, str):
        carpetas_ataque = [carpetas_ataque]

    # ------------------------------------------------------------------
    # 2. Localizar TODOS los CSV en TODAS las carpetas
    # ------------------------------------------------------------------
    archivos_csv = []

    for carpeta in carpetas_ataque:
        archivos_csv.extend(
            glob.glob(os.path.join(carpeta, mascara_archivos))
        )

    if not archivos_csv:
        print("❌ No se encontraron archivos CSV en las carpetas indicadas.")
        return None

    # ------------------------------------------------------------------
    # 3. Definir columnas esperadas (uso de SET para máxima velocidad)
    # ------------------------------------------------------------------
    columnas_esperadas = set(diccionario_columnas.values())

    # ------------------------------------------------------------------
    # 4. Validar columnas leyendo SOLO cabeceras
    # ------------------------------------------------------------------
    errores = []

    for archivo in archivos_csv:
        try:
            columnas_csv = set(
                pd.read_csv(
                    archivo,
                    sep=';',
                    encoding='ANSI',
                    nrows=0
                ).columns
            )

            if columnas_csv != columnas_esperadas:
                errores.append(
                    {
                        "archivo": archivo,
                        "faltan": columnas_esperadas - columnas_csv,
                        "sobran": columnas_csv - columnas_esperadas
                    }
                )

        except Exception as e:
            errores.append(
                {
                    "archivo": archivo,
                    "error": str(e)
                }
            )

    # ------------------------------------------------------------------
    # 5. Si hay errores → abortar proceso
    # ------------------------------------------------------------------
    if errores:
        print("❌ VALIDACIÓN DE COLUMNAS FALLIDA\n")

        for err in errores:
            print(f"Archivo: {err['archivo']}")

            if "error" in err:
                print(f"  Error al leer cabecera: {err['error']}")
            else:
                if err["faltan"]:
                    print(f"  Faltan columnas: {sorted(err['faltan'])}")
                if err["sobran"]:
                    print(f"  Sobran columnas: {sorted(err['sobran'])}")

            print("-" * 60)

        print("⛔ No se ha realizado la concatenación.")
        return None

    # ------------------------------------------------------------------
    # 6. Lectura completa y concatenación (solo si todo está OK)
    # ------------------------------------------------------------------
    df_combinado = pd.concat(
        [
            pd.read_csv(
                archivo,
                sep=';',
                encoding='ANSI',
                decimal=',',
                thousands='.',
                low_memory=False
            )
            for archivo in archivos_csv
        ],
        ignore_index=True
    )

    # ------------------------------------------------------------------
    # 7. Guardar CSV final
    # ------------------------------------------------------------------
    df_combinado.to_csv(
        archivo_salida,
        index=False,
        encoding='utf-8',
        sep=';',
        decimal=','
    )

    print("✅ CSV unidos correctamente.")
    return df_combinado