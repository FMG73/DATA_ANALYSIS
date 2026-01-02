import pandas as pd
import numpy as np
import re
from melvive.claseoffice import TablaGenerator
from melvive.funciones import imp_mensaje_inicial, imp_mensaje_final
from melvive.motortrade import EventLists

# =============================================================================
# INICIO
# =============================================================================

nombre_script = 'FORMATEAR REPORTING DE LISTAS - EVENTS LISTS'
imp_mensaje_inicial(nombre_script)

ruta_ataque = EventLists.event_lists_consolidado
ruta_descarga_csv = r'C:\Users\pepe\AT_EVENTLISTS_py.csv'
ruta_descarga_xlsx = r'C:\Users\pepe\AT_EVENTLISTS_py.xlsx'

# =============================================================================
# LECTURA
# =============================================================================

df_list_report = pd.read_csv(
    ruta_ataque,
    sep=';',
    encoding='utf-8',
    low_memory=False
)

# =============================================================================
# VARIABLES SEMANTICAS
# =============================================================================

grupo = 'GRUPO_USUARIO'
numero_lista = 'NUMERO_LISTA'
nombre_lista = 'NOMBRE_DE_LA_LISTA'
creador_lista = 'CREADOR_LISTA'
equipo = 'EQUIPO'

sourcing = 'SOURCING'
b2b = 'B2B'
particulares = 'PARTICULARES'

# =============================================================================
# CLASIFICACION EQUIPO (VECTORIZADA)
# =============================================================================

equipo_sourcing = ['SMartin', 'LChapatte', 'FMelero']
equipo_b2b = ['CMontes', 'OMartin', 'CHamon']
equipo_particulares = ['GFerriz', 'CGuerrero', 'CHamon']

grupo_b2b = ['Spain']
grupo_particulares = ['Spain >Particulares']

listas_sourcing = [1, 2]
listas_b2b = [293242, 285232, 286502, 294968, 305757, 305847, 306046]
listas_particulares = [291404]

condiciones_equipo = [
    df_list_report[creador_lista].isin(equipo_sourcing)
    | df_list_report[numero_lista].isin(listas_sourcing),

    df_list_report[creador_lista].isin(equipo_b2b)
    & df_list_report[grupo].isin(grupo_b2b),

    df_list_report[creador_lista].isin(equipo_particulares)
    & df_list_report[grupo].isin(grupo_particulares)
]

valores_equipo = [
    sourcing,
    b2b,
    particulares
]

df_list_report[equipo] = np.select(
    condiciones_equipo,
    valores_equipo,
    default='MULDER-SCULLY'
)

# =============================================================================
# NORMALIZAR NOMBRE LISTA
# =============================================================================

df_list_report[nombre_lista] = (
    df_list_report[nombre_lista]
    .astype(str)
    .str.upper()
)

# =============================================================================
# TIPO LISTA (VECTORIZADO)
# =============================================================================

condiciones_tipo_lista = [
    # SOURCING
    (df_list_report[equipo] == sourcing)
    & df_list_report[nombre_lista].str.contains(r'SUB.*TAR', regex=True, na=False),

    (df_list_report[equipo] == sourcing)
    & df_list_report[nombre_lista].str.contains(r'SUB.*TUR', regex=True, na=False),

    (df_list_report[equipo] == sourcing)
    & df_list_report[nombre_lista].str.contains(r'SUB.*IND', regex=True, na=False),

    (df_list_report[equipo] == sourcing)
    & df_list_report[nombre_lista].str.contains(r'ESPECIAL', regex=True, na=False),

    # B2B
    (df_list_report[equipo] == b2b)
    & df_list_report[nombre_lista].str.contains(r'KI.*EXCLU', regex=True, na=False),

    (df_list_report[equipo] == b2b)
    & df_list_report[nombre_lista].str.contains(r'HYU.*EXCLU', regex=True, na=False),

    (df_list_report[equipo] == b2b)
    & df_list_report[nombre_lista].str.contains(r'VOL.*EXCLU', regex=True, na=False),
]

valores_tipo_lista = [
    'TARDE',
    'TURISMOS',
    'INDUSTRIAL',
    'ESPECIAL',
    'KIA_EXCLUSIVA',
    'HYUNDAI_EXCLUSIVA',
    'VOLVO_EXCLUSIVA'
]

df_list_report['TIPO_LISTA'] = np.select(
    condiciones_tipo_lista,
    valores_tipo_lista,
    default='MULDER'
)

# =============================================================================
# EXPORTES
# =============================================================================

list_report = TablaGenerator(ruta_descarga_xlsx)

list_report.to_tabla(
    df_list_report,
    ruta_descarga_xlsx,
    nombre_hoja='EVENTS_LIST',
    nombre_Tabla='EVENTSLIST'
)

df_list_report.to_csv(
    ruta_descarga_csv,
    sep=';',
    encoding='utf-8',
    index=False,
    na_rep='0'
)

print(f'{nombre_script} OK')
input()