import pandas as pd

def obtener_ultimo_evento_por_nombre(df, columna_nombre, columna_evento, orden_eventos):
    """
    Retorna un DataFrame con el último evento por nombre según el orden lógico definido.

    Parámetros:
    - df: DataFrame de entrada
    - columna_nombre: nombre de la columna que contiene los nombres
    - columna_evento: nombre de la columna que contiene los eventos
    - orden_eventos: diccionario con el orden lógico de los eventos, ej. {'despegar': 1, 'comer': 2, 'dormir': 3}

    Retorna:
    - DataFrame con columnas [columna_nombre, columna_evento] filtrado por el evento más avanzado por nombre
    """
    df = df.copy()
    df['OrdenEvento'] = df[columna_evento].map(orden_eventos)

    if df['OrdenEvento'].isna().any():
        eventos_invalidos = df[df['OrdenEvento'].isna()][columna_evento].unique()
        raise ValueError(f"Eventos no reconocidos: {eventos_invalidos}")

    resultado = df.loc[df.groupby(columna_nombre)['OrdenEvento'].idxmax()].reset_index(drop=True)
    return resultado[[columna_nombre, columna_evento]]
