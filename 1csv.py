"""
csv_utils.py

Función utilitaria para consolidar múltiples archivos CSV provenientes
de distintas fuentes con posibles encodings diferentes.

Características:
- Detecta encoding individual por archivo.
- Permite encodings distintos en origen.
- Lee cada archivo con su encoding detectado.
- Valida estructura estricta de columnas.
- Elimina encabezado repetido si aparece como primera fila.
- Permite definir encoding de salida (por defecto UTF-8).
- Devuelve el DataFrame consolidado.

Requiere:
    pandas
    chardet
"""

from pathlib import Path
from typing import Union, List, Dict, Optional
import pandas as pd
import chardet


PathLike = Union[str, Path]


def detectar_encoding(ruta: Path, bytes_muestra: int = 10000) -> str:
    """
    Detecta el encoding probable de un archivo CSV.

    Parameters
    ----------
    ruta : Path
        Ruta del archivo.
    bytes_muestra : int
        Número de bytes utilizados para la detección.

    Returns
    -------
    str
        Encoding detectado.

    Raises
    ------
    ValueError
        Si no se puede detectar el encoding.
    """

    with ruta.open("rb") as archivo:
        contenido: bytes = archivo.read(bytes_muestra)
        resultado: Dict[str, Optional[str]] = chardet.detect(contenido)

    encoding: Optional[str] = resultado.get("encoding")

    if encoding is None:
        raise ValueError(
            f"No se pudo detectar el encoding del archivo: {ruta}"
        )

    return encoding


def concatenar_csv_validado(
    lista_rutas: List[PathLike],
    ruta_salida: PathLike,
    sep: str = ",",
    guardar: bool = True,
    encoding_salida: str = "utf-8"
) -> pd.DataFrame:
    """
    Consolida múltiples CSV permitiendo encodings distintos en origen.

    Validaciones realizadas
    -----------------------
    1. La lista de archivos no puede estar vacía.
    2. Todos los archivos deben existir.
    3. No se permiten columnas duplicadas.
    4. Las columnas deben coincidir exactamente en nombre y orden.
    5. Se elimina encabezado repetido si aparece como primera fila.
    6. Todos los datos se leen como texto (dtype=str).

    Parameters
    ----------
    lista_rutas : List[PathLike]
        Lista de rutas a consolidar.
    ruta_salida : PathLike
        Ruta de salida del CSV consolidado.
    sep : str
        Separador del CSV.
    guardar : bool
        Si True guarda el CSV resultante.
    encoding_salida : str
        Encoding del archivo consolidado (default="utf-8").

    Returns
    -------
    pd.DataFrame
        DataFrame consolidado.

    Raises
    ------
    ValueError
        Si la lista está vacía o hay inconsistencias estructurales.
    FileNotFoundError
        Si algún archivo no existe.
    """

    if not lista_rutas:
        raise ValueError("La lista de archivos está vacía.")

    rutas: List[Path] = [Path(r) for r in lista_rutas]

    print("\n=== DETECCIÓN DE ENCODING POR ARCHIVO ===")

    dataframes: List[pd.DataFrame] = []
    columnas_base: Optional[List[str]] = None
    total_filas_original: int = 0
    encabezados_eliminados: int = 0

    for ruta in rutas:

        if not ruta.exists():
            raise FileNotFoundError(f"No existe el archivo: {ruta}")

        encoding_detectado: str = detectar_encoding(ruta)
        print(f"{ruta.name} → {encoding_detectado}")

        df: pd.DataFrame = pd.read_csv(
            ruta,
            sep=sep,
            encoding=encoding_detectado,
            dtype=str,
            keep_default_na=False
        )

        total_filas_original += len(df)

        # Validar columnas duplicadas
        if len(set(df.columns)) != len(df.columns):
            raise ValueError(
                f"El archivo {ruta.name} contiene columnas duplicadas."
            )

        # Validar estructura estricta
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

    df_final: pd.DataFrame = pd.concat(dataframes, ignore_index=True)

    print("\n=== RESUMEN ===")
    print(f"Archivos consolidados: {len(rutas)}")
    print(f"Filas originales: {total_filas_original}")
    print(f"Encabezados eliminados: {encabezados_eliminados}")
    print(f"Filas finales: {len(df_final)}")
    print(f"Encoding de salida: {encoding_salida}")

    if guardar:
        ruta_salida_path: Path = Path(ruta_salida)
        ruta_salida_path.parent.mkdir(parents=True, exist_ok=True)

        df_final.to_csv(
            ruta_salida_path,
            index=False,
            sep=sep,
            encoding=encoding_salida
        )

        print(f"\nArchivo guardado en: {ruta_salida_path}")

    return df_final