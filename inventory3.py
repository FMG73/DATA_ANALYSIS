import pandas as pd


def procesar_stages_largo(
    df,
    col_matricula,
    col_stages,
    diccionario_grupos,
    stages_excluir="SPAIN",
    grupos_excluir="SPAIN"
):
    """
    Genera un dataset largo con:
    - Una fila por matrícula y stage
    - Columna de grupo asignado
    - Columnas multi_stage y multi_grupo (Y/N)
    - Columnas lista_stages y lista_grupos
    - Lógica especial: valores excluidos no cuentan para repetición
      y se eliminan de las listas si aparecen junto con otros valores.
    """

    # ------------------------------------------------------------------
    # 0. Copia defensiva del DataFrame de entrada
    # ------------------------------------------------------------------
    df = df.copy()

    # ------------------------------------------------------------------
    # 1. Normalizar parámetros de exclusión a listas
    # ------------------------------------------------------------------
    if isinstance(stages_excluir, str):
        stages_excluir = [stages_excluir]

    if isinstance(grupos_excluir, str):
        grupos_excluir = [grupos_excluir]

    # ------------------------------------------------------------------
    # 2. Convertir la columna de stages a lista
    #    Ejemplo: "SPAIN / FRANCE" -> ["SPAIN", "FRANCE"]
    # ------------------------------------------------------------------
    df["_stages_list"] = (
        df[col_stages]
        .fillna("")
        .apply(lambda x: [v.strip() for v in x.split("/") if v.strip()])
    )

    # ------------------------------------------------------------------
    # 3. Expandir el DataFrame a formato largo (explode)
    # ------------------------------------------------------------------
    df_long = (
        df
        .explode("_stages_list")
        .rename(columns={"_stages_list": "stage"})
    )

    # ------------------------------------------------------------------
    # 4. Crear diccionario stage -> grupo (optimización)
    # ------------------------------------------------------------------
    stage_to_grupo = {
        stage: grupo
        for grupo, lista_stages in diccionario_grupos.items()
        for stage in lista_stages
    }

    # Asignar grupo usando map (más rápido que apply)
    df_long["grupo"] = df_long["stage"].map(stage_to_grupo)

    # ------------------------------------------------------------------
    # 5. Calcular listas completas de stages y grupos por matrícula
    # ------------------------------------------------------------------
    df_listas = (
        df_long
        .groupby(col_matricula)
        .agg(
            stage=("stage", lambda x: sorted(set(x))),
            grupo=("grupo", lambda x: sorted({g for g in x if g is not None}))
        )
        .reset_index()
    )

    # ------------------------------------------------------------------
    # 6. Función para limpiar valores excluidos
    #    - Se eliminan solo si hay otros valores
    # ------------------------------------------------------------------
    def limpiar_lista(lista, excluir):
        lista_filtrada = [v for v in lista if v not in excluir]
        return lista_filtrada if lista_filtrada else lista

    df_listas["stage_limpio"] = df_listas["stage"].apply(
        lambda lst: limpiar_lista(lst, stages_excluir)
    )

    df_listas["grupo_limpio"] = df_listas["grupo"].apply(
        lambda lst: limpiar_lista(lst, grupos_excluir)
    )

    # ------------------------------------------------------------------
    # 7. Detectar multi_stage y multi_grupo
    # ------------------------------------------------------------------
    df_listas["multi_stage"] = df_listas["stage_limpio"].apply(
        lambda lst: "Y" if len(lst) > 1 else "N"
    )

    df_listas["multi_grupo"] = df_listas["grupo_limpio"].apply(
        lambda lst: "Y" if len(lst) > 1 else "N"
    )

    # ------------------------------------------------------------------
    # 8. Convertir listas a texto
    # ------------------------------------------------------------------
    df_listas["lista_stages"] = df_listas["stage_limpio"].apply(
        lambda lst: ", ".join(lst)
    )

    df_listas["lista_grupos"] = df_listas["grupo_limpio"].apply(
        lambda lst: ", ".join(lst)
    )

    # ------------------------------------------------------------------
    # 9. Unir información agregada al dataset largo
    # ------------------------------------------------------------------
    df_final = df_long.merge(
        df_listas[
            [
                col_matricula,
                "lista_stages",
                "lista_grupos",
                "multi_stage",
                "multi_grupo",
            ]
        ],
        on=col_matricula,
        how="left",
    )

    # ------------------------------------------------------------------
    # 10. Optimización de tipos (category)
    # ------------------------------------------------------------------
    for col in ["grupo", "multi_stage", "multi_grupo"]:
        if col in df_final.columns:
            df_final[col] = df_final[col].astype("category")

    return df_final