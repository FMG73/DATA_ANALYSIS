import pandas as pd
import re
from melvive.claseoffice import TablaGenerator
from melvive.funciones import imp_mensaje_inicial, imp_mensaje_final
from melvive.motortrade import EventLists

# =========================================================
# CONFIGURACIÓN INICIAL
# =========================================================

nombre_script = 'FORMATEAR REPORTING DE LISTAS - EVENTS LISTS'
imp_mensaje_inicial(nombre_script)

ruta_ataque = EventLists.event_lists_consolidado
ruta_descarga_csv = r'C:\Users\pepe\AT_EVENTLISTS_py.csv'
ruta_descarga_xlsx = r'C:\Users\ pepe \AT_EVENTLISTS_py.xlsx'

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def limpiar_columna(columnas, nuevos_nombres_columna):
    columnas = [col.strip().replace(' ', '_') for col in columnas]
    return [nuevos_nombres_columna.get(col, col) for col in columnas]

# =========================================================
# DEFINICIÓN DE COLUMNAS
# =========================================================

columnas_fechas = ['Fin']

columnas_decimales = [
    'antiguedad media (mes)',
    'Plazo maxi de adjudicados',
    'Palzo maxi de no adjudicados',
    'Plazo medio adjudicados',
    'Plazo medio no adjudicados'
]

columnas_enteros = [
    'publicado durante (h)',
    'Nº de Compradores',
    '% compraventas en lista',
    'Nº de compraventas con ofertas',
    'Nº de compraventas con adjudicación',
    'Nº de Vehículos',
    'kilometraje medio',
    'Daños medios',
    'Nº total de pujas',
    'Nº de vehículos con oferta',
    '% de vehículos con oferta',
    'Nº Veh adjudicados',
    '% de vehículos asignados en la misma lista',
    'Perf./Ref',
    'Pujas Pendientes',
    'Nr veh pendientes',
    'Numero de elementos no vendidos aun ',
    '!NumOfBuyerConnected:es_ES:TEXT!'
]

# =========================================================
# NOMBRES DE COLUMNAS
# =========================================================

grupo = 'GRUPO_USUARIO'
numero_lista = 'NUMERO_LISTA'
nombre_lista = 'NOMBRE_DE_LA_LISTA'
creador_lista = 'CREADOR_LISTA'
equipo = 'EQUIPO'

sourcing = 'SOURCING'
b2b = 'B2B'
particulares = 'PARTICULARES'

nuevos_nombres_columna = {
    'Grupo_de_Usuario': grupo,
    'Nº_de_lista': numero_lista,
    'Nombre_de_la_lista': nombre_lista,
    'Fin': 'FIN',
    'publicado_durante_(h)': 'PUBLICADO_DURANTE_(H)',
    'Nº_de_Compradores': 'Nº_DE_COMPRADORES',
    '%_compraventas_en_lista': '%_COMPRAVENTAS_EN_LISTA',
    'Nº_de_compraventas_con_ofertas': 'Nº_DE_COMPRAVENTAS_CON_OFERTAS',
    'Nº_de_compraventas_con_adjudicación': 'Nº_DE_COMPRAVENTAS_CON_ADJUDICACIÓN',
    'Nº_de_Vehículos': 'Nº_DE_VEHÍCULOS',
    'kilometraje_medio': 'KILOMETRAJE_MEDIO',
    'antiguedad_media_(mes)': 'ANTIGUEDAD_MEDIA_(MES)',
    'Daños_medios': 'DAÑOS_MEDIOS',
    'Nº_total_de_pujas': 'Nº_TOTAL_DE_PUJAS',
    'Nº_de_vehículos_con_oferta': 'Nº_DE_VEHÍCULOS_CON_OFERTA',
    '%_de_vehículos_con_oferta': '%_DE_VEHÍCULOS_CON_OFERTA',
    'Nº_Veh_adjudicados': 'Nº_VEH_ADJUDICADOS',
    '%_de_vehículos_asignados_en_la_misma_lista': '%_ASIGNADOS',
    'Perf./Ref': 'PERF./REF',
    'Pujas_Pendientes': 'PUJAS_PENDIENTES',
    'Nr_veh_pendientes': 'NR_VEH_PENDIENTES',
    'Plazo_maxi_de_adjudicados': 'PLAZO_MAXI_DE_ADJUDICADOS',
    'Palzo_maxi_de_no_adjudicados': 'PALZO_MAXI_DE_NO_ADJUDICADOS',
    'Plazo_medio_adjudicados': 'PLAZO_MEDIO_ADJUDICADOS',
    'Plazo_medio_no_adjudicados': 'PLAZO_MEDIO_NO_ADJUDICADOS',
    'Numero_de_elementos_no_vendidos_aun': 'NUMERO_DE_ELEMENTOS_NO_VENDIDOS_AUN',
    '!ListerCreationBy:es_ES:TEXT!': creador_lista,
    '!InvitationBy:es_ES:TEXT!': 'INVITACION_LISTA',
    '!NumOfBuyerConnected:es_ES:TEXT!': '!NUMOFBUYERCONNECTED:ES_ES:TEXT!'
}

# =========================================================
# PUNTO 1 – CARGA CSV
# =========================================================

df = pd.read_csv(
    ruta_ataque,
    sep=';',
    encoding='utf-8',
    low_memory=False
)

df.columns = limpiar_columna(df.columns, nuevos_nombres_columna)

# =========================================================
# PUNTO 2 – CONVERSIÓN DE TIPOS (VECTORIAL)
# =========================================================

for col in columnas_enteros:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(',', '.', regex=False)
            .pipe(pd.to_numeric, errors='coerce')
            .astype('Int64')
        )

for col in columnas_decimales:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(',', '.', regex=False)
            .pipe(pd.to_numeric, errors='coerce')
        )

for col in columnas_fechas:
    if col in df.columns:
        df[col] = pd.to_datetime(
            df[col],
            format='%d.%m.%Y %H:%M',
            errors='coerce'
        )

# =========================================================
# PUNTO 3 – ASIGNACIÓN DE EQUIPO (SIN APPLY)
# =========================================================

condiciones_equipo = {
    'equipo_sourcing': ['SMartin', 'LChapatte', 'FMelero'],
    'equipo_b2b': ['CMontes', 'OMartin', 'CHamon'],
    'equipo_particulares': ['GFerriz', 'CGuerrero', 'CHamon'],
    'grupo_b2b': ['Spain'],
    'grupo_particulares': ['Spain >Particulares'],
    'listas_sourcing': [1, 2],
    'listas_b2b': [
        293242, 285232, 286502, 294968, 294968, 305757, 305847,
        306046, 302065, 305914, 252111, 295547, 301153, 303443,
        305689, 304840, 305314, 306067, 306275, 306588, 308988,
        315880, 315926, 319741, 319630
    ],
    'listas_particulares': [291404],
}

df[equipo] = 'MULDER-SCULLY'

mask_sourcing = (
    df[creador_lista].isin(condiciones_equipo['equipo_sourcing']) |
    df[numero_lista].isin(condiciones_equipo['listas_sourcing'])
)

df.loc[mask_sourcing, equipo] = sourcing

mask_b2b = (
    (
        df[creador_lista].isin(condiciones_equipo['equipo_b2b']) &
        df[grupo].isin(condiciones_equipo['grupo_b2b'])
    ) |
    df[numero_lista].isin(condiciones_equipo['listas_b2b'])
)

df.loc[mask_b2b & ~mask_sourcing, equipo] = b2b

mask_particulares = (
    (
        df[creador_lista].isin(condiciones_equipo['equipo_particulares']) &
        df[grupo].isin(condiciones_equipo['grupo_particulares'])
    ) |
    df[numero_lista].isin(condiciones_equipo['listas_particulares'])
)

df.loc[
    mask_particulares & ~mask_sourcing & ~mask_b2b,
    equipo
] = particulares

# =========================================================
# PUNTO 4 – ASIGNACIÓN TIPO_LISTA (SIN APPLY)
# =========================================================

df['TIPO_LISTA'] = 'MULDER'

# --- SOURCING → POR NÚMERO ---
mask_sourcing = df[equipo] == sourcing

for tipo, numeros in condiciones_publicacion['tipo_lista_sourcing_por_numero'].items():
    if numeros:
        df.loc[
            mask_sourcing & df[numero_lista].isin(numeros),
            'TIPO_LISTA'
        ] = tipo

# --- SOURCING → POR REGEX ---
for tipo, patrones in condiciones_publicacion['tipo_lista_sourcing'].items():
    for patron in patrones:
        df.loc[
            mask_sourcing &
            (df['TIPO_LISTA'] == 'MULDER') &
            df[nombre_lista].str.contains(patron, case=False, na=False, regex=True),
            'TIPO_LISTA'
        ] = tipo

# --- B2B → POR NÚMERO ---
mask_b2b = df[equipo] == b2b

for tipo, numeros in condiciones_publicacion['tipo_lista_b2b_por_numero'].items():
    if numeros:
        df.loc[
            mask_b2b & df[numero_lista].isin(numeros),
            'TIPO_LISTA'
        ] = tipo

# --- B2B → POR REGEX ---
for tipo, patrones in condiciones_publicacion['tipo_lista_b2b'].items():
    for patron in patrones:
        df.loc[
            mask_b2b &
            (df['TIPO_LISTA'] == 'MULDER') &
            df[nombre_lista].str.contains(patron, case=False, na=False, regex=True),
            'TIPO_LISTA'
        ] = tipo

# =========================================================
# SALIDA FINAL (IDÉNTICA AL ORIGINAL)
# =========================================================

df[nombre_lista] = df[nombre_lista].str.upper()

tabla = TablaGenerator(ruta_descarga_xlsx)
tabla.to_tabla(
    df,
    ruta_descarga_xlsx,
    nombre_hoja='EVENTS_LIST',
    nombre_Tabla='EVENTSLIST'
)

df.to_csv(
    ruta_descarga_csv,
    sep=';',
    encoding='UTF-8',
    index=False,
    na_rep='0'
)

print(f'{nombre_script} GUARDADO EN\n{ruta_descarga_xlsx}\n{ruta_descarga_csv}\n')
print(f'{nombre_script} OK, PRESIONA UNA TECLA PARA TERMINAR\n')
input()