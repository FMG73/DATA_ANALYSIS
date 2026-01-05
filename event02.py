import pandas as pd

# =========================================================
# CONSTANTES DE COLUMNAS
# =========================================================

EQUIPO = "EQUIPO"
TIPO_LISTA = "TIPO_LISTA"

CREADOR = "CREADOR_LISTA"
GRUPO = "GRUPO_USUARIO"
NUMERO_LISTA = "NUMERO_LISTA"
NOMBRE_LISTA = "NOMBRE_DE_LA_LISTA"

# =========================================================
# CONSTANTES DE NEGOCIO
# =========================================================

SOURCING = "SOURCING"
B2B = "B2B"
PARTICULARES = "PARTICULARES"

DEFAULT_EQUIPO = "MULDER-SCULLY"
DEFAULT_TIPO = "MULDER"

# =========================================================
# REGLAS ORIGINALES (LISTAS EXACTAS)
# =========================================================

condiciones_equipo = {
    "equipo_sourcing": ["SMartin", "LChapatte", "FMelero"],
    "equipo_b2b": ["CMontes", "OMartin", "CHamon"],
    "equipo_particulares": ["GFerriz", "CGuerrero", "CHamon"],

    "grupo_b2b": ["Spain"],
    "grupo_particulares": ["Spain >Particulares"],

    "listas_sourcing": [1, 2],
    "listas_b2b": [
        293242, 285232, 286502, 294968, 294968, 305757, 305847,
        306046, 302065, 305914, 252111, 295547, 301153, 303443,
        305689, 304840, 305314, 306067, 306275, 306588, 308988,
        315880, 315926, 319741, 319630
    ],
    "listas_particulares": [291404],
}

# =========================================================
# REGLAS DE TIPO LISTA (SIGUEN EN PYTHON)
# =========================================================

condiciones_publicacion = {
    "tipo_lista_sourcing_por_numero": {
        "EXCLUSIVA": [1],
        "ABIERTA": [2],
    },
    "tipo_lista_sourcing": {
        "EXCLUSIVA": ["exclusiva"],
        "ABIERTA": ["abierta"],
    },
    "tipo_lista_b2b_por_numero": {
        "B2B_EXCLUSIVA": [293242, 285232],
        "B2B_ABIERTA": [286502],
    },
    "tipo_lista_b2b": {
        "B2B_EXCLUSIVA": ["exclusiva"],
        "B2B_ABIERTA": ["abierta"],
    },
}

# =========================================================
# ASIGNACIÓN DE EQUIPO (VECTORIAL)
# =========================================================

def asignar_equipo(df: pd.DataFrame) -> None:
    df[EQUIPO] = DEFAULT_EQUIPO
    df["_equipo_resuelto"] = False

    # -------- SOURCING --------
    mask_sourcing = (
        (
            df[CREADOR].isin(condiciones_equipo["equipo_sourcing"])
            | df[NUMERO_LISTA].isin(condiciones_equipo["listas_sourcing"])
        )
        & ~df[NUMERO_LISTA].isin(condiciones_equipo["listas_b2b"])
        & ~df[NUMERO_LISTA].isin(condiciones_equipo["listas_particulares"])
    )

    df.loc[mask_sourcing, EQUIPO] = SOURCING
    df.loc[mask_sourcing, "_equipo_resuelto"] = True

    # -------- B2B --------
    mask_b2b = (
        (
            (
                df[CREADOR].isin(condiciones_equipo["equipo_b2b"])
                & df[GRUPO].isin(condiciones_equipo["grupo_b2b"])
            )
            | df[NUMERO_LISTA].isin(condiciones_equipo["listas_b2b"])
        )
        & ~df[NUMERO_LISTA].isin(condiciones_equipo["listas_sourcing"])
        & ~df[NUMERO_LISTA].isin(condiciones_equipo["listas_particulares"])
        & ~df["_equipo_resuelto"]
    )

    df.loc[mask_b2b, EQUIPO] = B2B
    df.loc[mask_b2b, "_equipo_resuelto"] = True

    # -------- PARTICULARES --------
    mask_particulares = (
        (
            (
                df[CREADOR].isin(condiciones_equipo["equipo_particulares"])
                & df[GRUPO].isin(condiciones_equipo["grupo_particulares"])
            )
            | df[NUMERO_LISTA].isin(condiciones_equipo["listas_particulares"])
        )
        & ~df["_equipo_resuelto"]
    )

    df.loc[mask_particulares, EQUIPO] = PARTICULARES
    df.loc[mask_particulares, "_equipo_resuelto"] = True

    df.drop(columns="_equipo_resuelto", inplace=True)

# =========================================================
# ASIGNACIÓN DE TIPO LISTA (FORZADOS + REGEX)
# =========================================================

def asignar_tipo_lista(df: pd.DataFrame, reglas: dict) -> None:
    df[TIPO_LISTA] = DEFAULT_TIPO
    df["_tipo_resuelto"] = False

    # ================= SOURCING =================
    mask_sourcing = df[EQUIPO] == SOURCING

    for tipo, valores in reglas["tipo_lista_sourcing_por_numero"].items():
        mask = mask_sourcing & df[NUMERO_LISTA].isin(valores) & ~df["_tipo_resuelto"]
        df.loc[mask, TIPO_LISTA] = tipo
        df.loc[mask, "_tipo_resuelto"] = True

    for tipo, patrones in reglas["tipo_lista_sourcing"].items():
        for patron in patrones:
            mask = (
                mask_sourcing
                & df[NOMBRE_LISTA].str.contains(patron, case=False, na=False)
                & ~df["_tipo_resuelto"]
            )
            df.loc[mask, TIPO_LISTA] = tipo
            df.loc[mask, "_tipo_resuelto"] = True

    # ================= B2B =================
    mask_b2b = df[EQUIPO] == B2B

    for tipo, valores in reglas["tipo_lista_b2b_por_numero"].items():
        mask = mask_b2b & df[NUMERO_LISTA].isin(valores) & ~df["_tipo_resuelto"]
        df.loc[mask, TIPO_LISTA] = tipo
        df.loc[mask, "_tipo_resuelto"] = True

    for tipo, patrones in reglas["tipo_lista_b2b"].items():
        for patron in patrones:
            mask = (
                mask_b2b
                & df[NOMBRE_LISTA].str.contains(patron, case=False, na=False)
                & ~df["_tipo_resuelto"]
            )
            df.loc[mask, TIPO_LISTA] = tipo
            df.loc[mask, "_tipo_resuelto"] = True

    df.drop(columns="_tipo_resuelto", inplace=True)

# =========================================================
# PIPELINE PRINCIPAL
# =========================================================

def aplicar_reglas_negocio(df: pd.DataFrame) -> pd.DataFrame:
    asignar_equipo(df)
    asignar_tipo_lista(df, condiciones_publicacion)
    return df