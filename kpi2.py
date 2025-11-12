# Lista global donde irán todas las filas de todos los KPIs
todas_las_filas = []

# 🔹 Ejemplo KPI "Top 5 mensual"
mask_mes = (
    (df_ventas["fecha"].dt.month == fecha_fin.month) &
    (df_ventas["fecha"].dt.year == fecha_fin.year)
)
df_filtrado = df_ventas.loc[mask_mes].copy()

if not df_filtrado.empty:
    resumen = df_filtrado.groupby("cliente").agg(
        vehiculos=("cliente", "count"),
        adjudicados=("Awarded", "sum")
    ).sort_values("vehiculos", ascending=False).head(5)

    for cliente, row in resumen.iterrows():
        fila = {
            "kpi": "Top 5 mensual",
            "fecha_kpi": fecha_fin,
            "etiqueta_fecha": f"{fecha_fin.month:02d}/{fecha_fin.year % 100:02d}",
            "fecha_inicio": datetime(fecha_fin.year, fecha_fin.month, 1),
            "fecha_fin": fecha_fin,
            "vehiculos": row["vehiculos"],
            "buyer": cliente,
            "cantidad": row["adjudicados"],
            "equipo": None,
            "tipo_lista": None,
            "n_lista": None,
            "n_vehiculos": None,
            "adjudicados": row["adjudicados"],
            "pct_adjudicados": None
        }
        todas_las_filas.append(fila)

# 🔹 Y así haces con el resto de KPIs (vendido día, vendido mes, etc.)
# ...
# todas_las_filas.append(fila_kpi_x)

# 🔹 Al final del script creas el DataFrame unificado:
df_kpis_final = pd.DataFrame([
    {columnas_maestro[key]: val for key, val in fila.items() if key in columnas_maestro}
    for fila in todas_las_filas
])