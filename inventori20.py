import pandas as pd
import numpy as np

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
    - Columna de grupo asignado (vectorizado)
    - Columnas multi_stage y multi_grupo (Y/N)
    - Columnas lista_stages y lista_grupos con exclusiones condicionales
    """

    df = df.copy()

    # Normalizar exclusiones a listas
    if isinstance(stages_excluir, str):
        stages_excluir = [stages_excluir]
    if isinstance(grupos_excluir, str):
        grupos_excluir = [grupos_excluir]

    # --- 1. Convertir stages en listas (split vectorizado) ---
    df["__lista_stages__"] = (
        df[col_stages]
        .fillna("")
        .str.split("/")
        .apply(lambda lst: [v.strip() for v in lst if v.strip()])
    )

    # --- 2. Expandir a formato largo ---
    df_long = df.explode("__lista_stages__").rename(
        columns={"__lista_stages__": "stage"}
    )

    # --- 3. Asignar grupo (optimizado con map) ---
    map_stage_grupo = {
        stage: grupo
        for grupo, lista in diccionario_grupos.items()
        for stage in lista
    }

    df_long["grupo"] = df_long["stage"].map(map_stage_grupo)

    # --- 4. Calcular listas completas por matrícula ---
    df_listas = df_long.groupby(col_matricula).agg({
        "stage": lambda x: sorted(set(x)),
        "grupo": lambda x: sorted({g for g in x if isinstance(g, str) and g.strip()})
    }).reset_index()

    # --- 5. Limpiar listas según tu lógica ---
    def limpiar_lista(lista, excluir):
        # Si todos los valores están en excluir → se mantienen
        if all(v in excluir for v in lista):
            return lista
        # Si hay excluidos mezclados con otros → se eliminan
        return [v for v in lista if v not in excluir]

    df_listas["stage_limpio"] = df_listas["stage"].apply(
        lambda lst: limpiar_lista(lst, stages_excluir)
    )

    df_listas["grupo_limpio"] = df_listas["grupo"].apply(
        lambda lst: limpiar_lista(lst, grupos_excluir)
    )

    # --- 6. Detectar multi_stage ---
    df_listas["multi_stage"] = df_listas["stage_limpio"].apply(
        lambda lst: "Y" if len(lst) > 1 else "N"
    )

    # --- 7. Detectar multi_grupo ---
    df_listas["multi_grupo"] = df_listas["grupo_limpio"].apply(
        lambda lst: "Y" if len(lst) > 1 else "N"
    )

    # --- 8. Convertir listas a texto ---
    df_listas["lista_stages"] = df_listas["stage_limpio"].apply(lambda lst: ", ".join(lst))
    df_listas["lista_grupos"] = df_listas["grupo_limpio"].apply(lambda lst: ", ".join(lst))

    # --- 9. Unir listas y flags al dataset largo ---
    df_final = df_long.merge(
        df_listas[[col_matricula, "lista_stages", "lista_grupos",
                   "multi_stage", "multi_grupo"]],
        on=col_matricula,
        how="left"
    )

    return df_final
