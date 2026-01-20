import pandas as pd

# -------------------------------
# 1️⃣ Cargar primer archivo CSV
# -------------------------------
ruta_csv = "archivo.csv"
df = pd.read_csv(ruta_csv)

# -------------------------------
# 2️⃣ Limpiar columna 'comprador'
# -------------------------------
# eliminar espacios y mantener vacíos como ''
df["comprador"] = df["comprador"].astype(str).str.strip()

# -------------------------------
# 3️⃣ Filtrar filas con comprador vacío
# -------------------------------
df_vacios = df[
    df["comprador"].isna() | (df["comprador"] == "")
]

# -------------------------------
# 4️⃣ Seleccionar columnas deseadas
# -------------------------------
columnas_seleccionadas = ["List id", "comprador", "matricula"]
df_final = df_vacios[columnas_seleccionadas]

# -------------------------------
# 5️⃣ Cargar archivo histórico
# -------------------------------
ruta_historico = "historico.xlsx"
df_historico = pd.read_excel(ruta_historico)

# -------------------------------
# 6️⃣ Limpiar 'matricula' y 'List id' por si hay espacios
# -------------------------------
df_final["matricula"] = df_final["matricula"].astype(str).str.strip()
df_historico["matricula"] = df_historico["matricula"].astype(str).str.strip()
df_final["List id"] = df_final["List id"].astype(str).str.strip()
df_historico["List id"] = df_historico["List id"].astype(str).str.strip()

# -------------------------------
# 7️⃣ Obtener List id únicos del primer archivo
# -------------------------------
list_ids_primer_archivo = df_final["List id"].unique()

# -------------------------------
# 8️⃣ Filtrar histórico eliminando filas con esos List id
# -------------------------------
df_historico_filtrado = df_historico[
    ~df_historico["List id"].isin(list_ids_primer_archivo)
]

# -------------------------------
# 9️⃣ Quedarse con filas del primer archivo cuya matricula
#     NO esté en el histórico filtrado
# -------------------------------
df_resultado = df_final[
    ~df_final["matricula"].isin(df_historico_filtrado["matricula"])
]

# -------------------------------
# 10️⃣ Mostrar resultado
# -------------------------------
print(df_resultado)

# -------------------------------
# 11️⃣ (Opcional) Guardar resultado en CSV
# -------------------------------
df_resultado.to_csv("resultado_filtrado.csv", index=False)