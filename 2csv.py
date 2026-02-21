"""
csv_utils.py

Función utilitaria para consolidar múltiples archivos CSV provenientes
de distintas fuentes con posibles encodings diferentes.

Características:
- Detecta encoding individual por archivo.
- Permite encodings distintos en origen.
- Valida estructura estricta de columnas.
- Elimina encabezado repetido si aparece como primera fila.
- Permite definir encoding de salida.
- Devuelve el DataFrame consolidado.
- Muestra mensajes en consola con colores por nivel.

Dependencias externas:
    pandas
    chardet
    colorama
"""

from pathlib import Path
from typing import Union, List, Dict, Optional
import pandas as pd
import chardet
from colorama import Fore, Style, init


# Inicializar colorama
init(autoreset=True)

PathLike = Union[str, Path]


# =========================
# Funciones auxiliares print
# =========================

def print_info(msg: str) -> None:
    print(Fore.BLUE + f"[INFO] {msg}")


def print_ok(msg: str) -> None:
    print(Fore.GREEN + f"[OK] {msg}")


def print_warning(msg: str) -> None:
    print(Fore.YELLOW + f"[WARNING] {msg}")


def print_error(msg: str) -> None:
    print(Fore.RED + f"[ERROR] {msg}")


# =========================
# Detección de encoding
# =========================

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
        raise ValueError(f"No se pudo detectar el encoding del archivo: {ruta}")

    return encoding


# =========================
# Función principal
# =========================

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

    Returns
    -------
    pd.DataFrame
        DataFrame consolidado.
    """

    if not lista_rutas:
        raise ValueError("La lista de archivos está vacía.")

    rutas: List[Path] = [Path(r) for r in lista_rutas]

    print_info("Iniciando consolidación de archivos CSV")

    dataframes: List[pd.DataFrame] = []
    columnas_base: Optional[List[str]] = None
    total_filas_original: int = 0
    encabezados_eliminados: int = 0

    for ruta in rutas:

        if not ruta.exists():
            print_error(f"No existe el archivo: {ruta}")
            raise FileNotFoundError(f"No existe el archivo: {ruta}")

        encoding_detectado: str = detectar_encoding(ruta)
        print_info(f"{ruta.name} → Encoding detectado: {encoding_detectado}")

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
            print_error(f"Columnas duplicadas detectadas en {ruta.name}")
            raise ValueError(f"El archivo {ruta.name} contiene columnas duplicadas.")

        # Validar estructura
        if columnas_base is None:
            columnas_base = df.columns.tolist()
            print_info("Columnas base establecidas.")
        else:
            if df.columns.tolist() != columnas_base:
                print_error(f"Las columnas no coinciden en {ruta.name}")
                raise ValueError(
                    f"Las columnas no coinciden en el archivo: {ruta.name}"
                )

        # Eliminar encabezado repetido
        if not df.empty and df.iloc[0].tolist() == columnas_base:
            df = df.iloc[1:]
            encabezados_eliminados += 1
            print_warning(f"Encabezado repetido eliminado en {ruta.name}")

        dataframes.append(df)

    print_info("Concatenando DataFrames")

    df_final: pd.DataFrame = pd.concat(dataframes, ignore_index=True)

    print_info("Resumen del proceso")
    print_ok(f"Archivos consolidados: {len(rutas)}")
    print_ok(f"Filas originales: {total_filas_original}")
    print_warning(f"Encabezados eliminados: {encabezados_eliminados}")
    print_ok(f"Filas finales: {len(df_final)}")
    print_info(f"Encoding de salida configurado: {encoding_salida}")

    if guardar:
        ruta_salida_path: Path = Path(ruta_salida)
        ruta_salida_path.parent.mkdir(parents=True, exist_ok=True)

        df_final.to_csv(
            ruta_salida_path,
            index=False,
            sep=sep,
            encoding=encoding_salida
        )

        print_ok(f"Archivo guardado en: {ruta_salida_path}")

    return df_final