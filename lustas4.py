import pandas as pd

# -------------------------------
# 1️⃣ Cargar primer archivo CSV
# -------------------------------
df = pd.read_csv("archivo.csv")

# -------------------------------
# 2️⃣ Limpiar columnas importantes
# -------------------------------
for col in ["comprador", "matricula", "List id"]:
    df[col] = df[col].astype(str).str.strip()

# -------------------------------
# 3️⃣ Filtrar filas con comprador vacío
# -------------------------------
df_final = df[df["comprador"] == ""]

# -------------------------------
# 4️⃣ Cargar archivo histórico
# -------------------------------
df_historico = pd.read_excel("historico.xlsx")
for col in ["matricula", "List id"]:
    df_historico[col] = df_historico[col].astype(str).str.strip()

# -------------------------------
# 5️⃣ Filtrar histórico eliminando List id presentes en primer archivo
# -------------------------------
list_ids_set = set(df_final["List id"])
df_historico_filtrado = df_historico[~df_historico["List id"].isin(list_ids_set)]

# -------------------------------
# 6️⃣ Anti-join usando merge (mantiene todas las columnas de df_final)
# -------------------------------
df_merge = df_final.merge(
    df_historico_filtrado[["matricula"]],
    on="matricula",
    how="left",
    indicator=True
)

df_resultado = df_merge[df_merge["_merge"] == "left_only"].drop(columns="_merge")

# -------------------------------
# 7️⃣ Mostrar resultado y guardar CSV
# -------------------------------
print(df_resultado)
df_resultado.to_csv("resultado_filtrado.csv", index=False)