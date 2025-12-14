import pandas as pd
import matplotlib.pyplot as plt

# =========================
# CARGA DE DATOS
# =========================
df = pd.read_csv("html_test.csv")
data = df.iloc[0]

# =========================
# TARJETAS POR FILA
# =========================
ROW_2_CARDS = [
    {"title": "Nº Lista", "value": data["n_lista"]},
    {"title": "Usuarios", "value": data["usuarios"]},
    {"title": "Conectados", "value": data["usuarios_conectados"]},
    {"title": "Con Oferta", "value": data["usuarios_oferta"]},
    {"title": "Con Adjudicación", "value": data["usuarios_adjudicacion"]}
]

ROW_3_CARDS = [
    {"title": "Vehículos Publicados", "value": data["vehiculos_publicados"]},
    {"title": "Con Oferta", "value": data["vehiculos_oferta"]},
    {"title": "Adjudicados", "value": data["vehiculos_adjudicados"]},
    {"title": "Plazo Medio", "value": data["plazo_medio"]},
    {"title": "KM Medio", "value": data["km_medio"]}
]

# =========================
# DASHBOARD
# =========================
fig = plt.figure(figsize=(18, 10))

# Alturas relativas
title_h = 0.18
row_h = 0.41

# Fila 2
draw_row(fig, 1 - title_h - row_h, row_h, ROW_2_CARDS, ROW_STYLES["fila_usuarios"])

# Fila 3
draw_row(fig, 0, row_h, ROW_3_CARDS, ROW_STYLES["fila_vehiculos"])

plt.show()