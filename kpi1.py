import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# --- 1️⃣ Inputs del usuario ---
fecha_inicio_input = input("Introduce fecha inicio (dd/mm/yyyy): ")
fecha_fin_input = input("Introduce fecha fin (dd/mm/yyyy): ")

fecha_inicio = pd.to_datetime(fecha_inicio_input, dayfirst=True)
fecha_fin = pd.to_datetime(fecha_fin_input, dayfirst=True)

# --- 2️⃣ DataFrame de ejemplo (ventas) ---
df_ventas = pd.DataFrame({
    "fecha": pd.to_datetime([
        "2025-06-15", "2025-07-10", "2025-08-03", "2025-09-20",
        "2025-10-25", "2025-10-28", "2025-11-01", "2025-11-02", "2025-11-03"
    ]),
    "vehiculo": [1,2,3,4,5,6,7,8,9]
})

# --- 3️⃣ Diccionario maestro de columnas ---
columnas_maestro = {
    "kpi": "KPI",
    "fecha_kpi": "FECHA KPI",
    "etiqueta_fecha": "ETIQUETA FECHA",
    "fecha_inicio": "FECHA INICIO",
    "fecha_fin": "FECHA FIN",
    "vehiculos": "VEHICULOS",
    "buyer": "BUYER",
    "cantidad": "CANTIDAD",
    "equipo": "EQUIPO",
    "tipo_lista": "TIPO LISTA",
    "n_lista": "Nª LISTA",
    "n_vehiculos": "Nª VEHICULOS",
    "adjudicados": "ADJUDICADOS",
    "pct_adjudicados": "% ADJUDICADOS"
}

# --- 4️⃣ Lista para acumular resultados ---
filas_resultado = []

# === KPI 1: VENDIDO DÍA ===
df_dia = df_ventas[
    (df_ventas["fecha"] >= fecha_inicio) & (df_ventas["fecha"] <= fecha_fin)
]
vendido_dia = {
    "kpi": "Vendido día",
    "fecha_inicio": fecha_inicio,
    "fecha_fin": fecha_fin,
    "cantidad": len(df_dia)
}
filas_resultado.append(vendido_dia)

# === KPI 2: VENDIDO MES ===
inicio_mes = datetime(fecha_fin.year, fecha_fin.month, 1)
df_mes = df_ventas[
    (df_ventas["fecha"] >= inicio_mes) & (df_ventas["fecha"] <= fecha_fin)
]
vendido_mes = {
    "kpi": "Vendido mes",
    "fecha_inicio": inicio_mes,
    "fecha_fin": fecha_fin,
    "cantidad": len(df_mes)
}
filas_resultado.append(vendido_mes)

# === KPI 3: EVOLUCIÓN VENTAS ===
primer_dia_mes = datetime(fecha_fin.year, fecha_fin.month, 1)
ultimo_dia_mes = (primer_dia_mes + relativedelta(months=1)) - timedelta(days=1)

for dia in pd.date_range(primer_dia_mes, ultimo_dia_mes):
    ventas_dia = df_ventas[df_ventas["fecha"] == dia]
    fila = {
        "kpi": "Evolución ventas",
        "fecha_inicio": dia,
        "fecha_fin": dia,
        "cantidad": len(ventas_dia)
    }
    filas_resultado.append(fila)

# === KPI 4: VENTAS SEIS MESES ===
for i in range(6):
    mes_actual = fecha_fin - relativedelta(months=i)
    inicio_mes = datetime(mes_actual.year, mes_actual.month, 1)
    fin_mes = (inicio_mes + relativedelta(months=1)) - timedelta(days=1)
    
    df_mes_i = df_ventas[
        (df_ventas["fecha"] >= inicio_mes) & (df_ventas["fecha"] <= fin_mes)
    ]
    fila = {
        "kpi": "Ventas seis meses",
        "fecha_inicio": inicio_mes,
        "fecha_fin": inicio_mes,  # fecha fin igual al inicio según tu definición
        "cantidad": len(df_mes_i)
    }
    filas_resultado.append(fila)

# --- 5️⃣ Crear DataFrame final usando nombres del diccionario maestro ---
df_final = pd.DataFrame([
    {columnas_maestro.get(k, k): v for k, v in fila.items()} for fila in filas_resultado
])

print(df_final)