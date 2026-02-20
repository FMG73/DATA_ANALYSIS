"""
csv_utils.py

Función utilitaria para consolidar múltiples archivos CSV aplicando
validaciones estrictas antes de la concatenación.

Funcionalidades:
- Detección automática de encoding por archivo.
- Validación de que todos los archivos tengan el mismo encoding.
- Validación estricta de columnas (mismo nombre y mismo orden).
- Detección de columnas duplicadas.
- Lectura como texto (dtype=str) sin conversión automática a NaN.
- Eliminación de encabezado repetido si aparece como primera fila.
- Opción de guardar o no el resultado.
- Devuelve el DataFrame consolidado.

Dependencias:
    pandas
    chardet
"""

from pathlib import Path
from typing import Union, List, Dict
import pandas as pd
import chardet


def detectar_encoding(ruta: Path, bytes_muestra: int = 10000) -> str:
    """
    Detecta el encoding probable de un archivo CSV leyendo una muestra binaria.

    Parameters
    ----------
    ruta : Path
        Ruta del archivo a analizar.
    bytes_muestra : int, optional
        Cantidad de bytes a utilizar para la detección.

    Returns
    -------
    str
        Encoding detectado.

    Raises
    ------
    ValueError
        Si no se puede determinar el encoding.
    """

    with ruta.open("rb") as archivo:
        contenido = archivo.read(bytes_muestra)
        resultado = chardet.detect(contenido)

    encoding = resultado.get("encoding")

    if encoding is None:
        raise ValueError(
            f"No se pudo detectar el encoding del archivo: {ruta}"
        )

    return encoding


def concatenar_csv_validado(
    lista_rutas: List[Union[str, Path]],
    ruta_salida: Union[str, Path],
    sep: str = ",",
    guardar: bool = True
) -> pd.DataFrame:
    """
    Consolida múltiples archivos CSV aplicando validaciones estructurales
    y de encoding antes de realizar la concatenación.

    Validaciones realizadas
    -----------------------
    1. La lista de archivos no puede estar vacía.
    2. Todos los archivos deben existir.
    3. Todos los archivos deben tener el mismo encoding.
    4. No se permiten columnas duplicadas.
    5. Todas las columnas deben coincidir exactamente en nombre y orden.
    6. Se elimina automáticamente un encabezado repetido si aparece
       como primera fila de datos.
    7. Los datos se leen como texto (dtype=str) sin conversión automática a NaN.

    Parameters
    ----------
    lista_rutas : List[str | Path]
        Lista de rutas de los archivos CSV a consolidar.
    ruta_salida : str | Path
        Ruta donde se guardará el archivo consolidado.
    sep : str, optional
        Separador del CSV (default=",").
    guardar : bool, optional
        Si True guarda el CSV consolidado.
        Si False solo devuelve el DataFrame en memoria.

    Returns
    -------
    pd.DataFrame
        DataFrame consolidado final.

    Raises
    ------
    ValueError
        Si:
        - La lista está vacía.
        - Los encodings no coinciden.
        - Las columnas no coinciden.
        - Existen columnas duplicadas.
    FileNotFoundError
        Si algún archivo no existe.
    """

    if not lista_rutas:
        raise ValueError("La lista de archivos está vacía.")

    rutas: List[Path] = [Path(r) for r in lista_rutas]

    print("\n=== DETECCIÓN DE ENCODING ===")

    encodings_detectados: Dict[str, str] = {}

    for ruta in rutas:
        if not ruta.exists():
            raise FileNotFoundError(f"No existe el archivo: {ruta}")

        encoding = detectar_encoding(ruta)
        encodings_detectados[ruta.name] = encoding
        print(f"{ruta.name} → {encoding}")

    encodings_unicos = set(encodings_detectados.values())

    if len(encodings_unicos) != 1:
        raise ValueError(
            f"""
Los archivos no tienen el mismo encoding.

Encodings detectados:
{encodings_detectados}

No se puede consolidar.
"""
        )

    encoding_final = encodings_unicos.pop()
    print(f"\nEncoding validado: {encoding_final}")

    print("\n=== CONSOLIDACIÓN ===")

    dataframes: List[pd.DataFrame] = []
    columnas_base = None
    total_filas_original = 0
    encabezados_eliminados = 0

    for ruta in rutas:

        print(f"Procesando: {ruta.name}")

        df = pd.read_csv(
            ruta,
            sep=sep,
            encoding=encoding_final,
            dtype=str,
            keep_default_na=False
        )

        total_filas_original += len(df)

        # Validar columnas duplicadas
        if len(set(df.columns)) != len(df.columns):
            raise ValueError(
                f"El archivo {ruta.name} contiene columnas duplicadas."
            )

        # Validar estructura de columnas
        if columnas_base is None:
            columnas_base = df.columns.tolist()
        else:
            if df.columns.tolist() != columnas_base:
                raise ValueError(
                    f"""
Las columnas no coinciden en el archivo: {ruta.name}

Columnas esperadas:
{columnas_base}

Columnas encontradas:
{df.columns.tolist()}
"""
                )

        # Eliminar encabezado repetido
        if not df.empty and df.iloc[0].tolist() == columnas_base:
            df = df.iloc[1:]
            encabezados_eliminados += 1
            print("Encabezado repetido eliminado.")

        dataframes.append(df)

    print("\nConcatenando DataFrames...")

    df_final = pd.concat(dataframes, ignore_index=True)

    print("\n=== RESUMEN ===")
    print(f"Archivos consolidados: {len(rutas)}")
    print(f"Filas originales: {total_filas_original}")
    print(f"Encabezados eliminados: {encabezados_eliminados}")
    print(f"Filas finales: {len(df_final)}")

    if guardar:
        ruta_salida = Path(ruta_salida)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)

        df_final.to_csv(
            ruta_salida,
            index=False,
            sep=sep,
            encoding=encoding_final
        )

        print(f"\nArchivo guardado en: {ruta_salida}")

    return df_final