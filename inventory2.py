import pandas as pd

def procesar_stages_largo(
    df, col_matricula, col_stages, diccionario_grupos, stage_excluir="SPAIN"
):
    """
    Genera un dataset largo con:
    - Una fila por matrícula y stage
    - Columna de grupo asignado
    - Columnas multi_stage y multi_grupo (Y/N)
    - Columnas lista_stages y lista_grupos
    - Lógica especial: un stage excluido (SPAIN) no cuenta para repetición

    Parámetros
    ----------
    df : pd.DataFrame
    col_matricula : str
    col_stages : str
    diccionario_grupos : dict
    stage_excluir : str (default "SPAIN")

    Retorna
    -------
    pd.DataFrame
    """

    df = df.copy()

    # --- 1. Convertir stages en listas ---
    df["__lista_stages__"] = df[col_stages].fillna("").apply(
        lambda x: [v.strip() for v in x.split("/") if v.strip()]
    )

    # --- 2. Expandir a formato largo ---
    df_long = df.explode("__lista_stages__").rename(
        columns={"__lista_stages__": "stage"}
    )

    # --- 3. Asignar grupo por stage ---
    def asignar_grupo(stage):
        for grupo, lista in diccionario_grupos.items():
            if stage in lista:
                return grupo
        return None

    df_long["grupo"] = df_long["stage"].apply(asignar_grupo)

    # --- 4. Calcular listas completas por matrícula ---
    df_listas = df_long.groupby(col_matricula).agg({
        "stage": lambda x: sorted(set(x)),
        "grupo": lambda x: sorted({g for g in x if g is not None})
    }).reset_index()

    df_listas["lista_stages"] = df_listas["stage"].apply(lambda lst: ", ".join(lst))
    df_listas["lista_grupos"] = df_listas["grupo"].apply(lambda lst: ", ".join(lst))

    # --- 5. Detectar multi_stage (ignorando SPAIN) ---
    df_listas["multi_stage"] = df_listas["stage"].apply(
        lambda lst: "Y" if len([s for s in lst if s != stage_excluir]) > 1 else "N"
    )

    # --- 6. Detectar multi_grupo ---
    df_listas["multi_grupo"] = df_listas["grupo"].apply(
        lambda lst: "Y" if len(lst) > 1 else "N"
    )

    # --- 7. Unir listas y flags al dataset largo ---
    df_final = df_long.merge(df_listas[[col_matricula, "lista_stages", "lista_grupos",
                                        "multi_stage", "multi_grupo"]],
                             on=col_matricula, how="left")

    return df_final
