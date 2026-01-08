import pandas as pd

def expandir_valores_y_grupos(df, col, diccionario_grupos):
    """
    Expande una columna con valores separados por '/' en:
    1) Columnas binarias por cada valor individual.
    2) Columnas binarias por cada grupo definido en un diccionario.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame original.
    col : str
        Nombre de la columna que contiene valores separados por '/'.
    diccionario_grupos : dict
        Diccionario donde cada clave es un grupo y cada valor es una lista
        de valores individuales que pertenecen a ese grupo.

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas adicionales para valores individuales y grupos.
    """

    df = df.copy()

    # --- 1. Separar valores individuales ---
    df["__lista_valores__"] = df[col].fillna("").apply(lambda x: [v.strip() for v in x.split("/") if v.strip()])

    # Obtener todos los valores posibles
    todos_los_valores = sorted({v for lista in df["__lista_valores__"] for v in lista})

    # Crear columnas binarias por valor individual
    for valor in todos_los_valores:
        df[valor] = df["__lista_valores__"].apply(lambda lista: 1 if valor in lista else 0)

    # --- 2. Crear columnas por grupo ---
    for grupo, valores in diccionario_grupos.items():
        valores_limpios = [v.strip() for v in valores]
        df[grupo] = df["__lista_valores__"].apply(
            lambda lista: 1 if any(v in lista for v in valores_limpios) else 0
        )

    # Limpiar columna auxiliar
    df.drop(columns=["__lista_valores__"], inplace=True)

    return df
