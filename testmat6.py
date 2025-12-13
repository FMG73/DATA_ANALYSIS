import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Segoe UI"

# ---------------------------
# Datos de ejemplo
# ---------------------------
data = {
    "fecha": pd.date_range("2025-01-01", periods=6),
    "marca": ["Volvo", "Kia", "Hyundai", "Volvo", "Kia", "Hyundai"],
    "modelo": ["XC60","Sportage","Tucson","XC90","Ceed","Kona"],
    "gasolina": [3,2,1,2,1,2],
    "diesel": [1,1,0,1,2,0],
    "electrico": [0,0,0,1,0,1]
}
df = pd.DataFrame(data)
df["ventas"] = df["gasolina"] + df["diesel"] + df["electrico"]

# ---------------------------
# Calcular ventas por marca
# ---------------------------
ventas = {
    "Volvo": df[df["marca"]=="Volvo"]["ventas"].sum(),
    "Kia": df[df["marca"]=="Kia"]["ventas"].sum(),
    "Hyundai": df[df["marca"]=="Hyundai"]["ventas"].sum()
}

# ---------------------------
# Crear figura y layout
# ---------------------------
fig, axes = plt.subplots(3, 3, figsize=(16, 12))
fig.patch.set_facecolor("#F3F4F6")

# Primera fila: título general
ax_title = axes[0,0]
ax_title.axis("off")
ax_title.text(0.5, 0.5, "Dashboard Ventas Coches",
              ha="center", va="center",
              fontsize=30, fontweight="bold",
              color="#111827", transform=ax_title.transAxes)
axes[0,1].axis("off")
axes[0,2].axis("off")

# ---------------------------
# Función para tarjeta KPI
# ---------------------------
def draw_card(ax, title, value):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")
    # sombra
    ax.add_patch(FancyBboxPatch(
        (4,4), 92, 52, boxstyle="round,pad=0.02,rounding_size=12",
        linewidth=0, facecolor="black", alpha=0.12
    ))
    # tarjeta
    ax.add_patch(FancyBboxPatch(
        (2,6), 92, 52, boxstyle="round,pad=0.02,rounding_size=12",
        linewidth=1.5, edgecolor="#E5E7EB", facecolor="white"
    ))
    # texto
    ax.text(50, 35, title, ha="center", fontsize=14, color="#6B7280")
    ax.text(50, 20, value, ha="center", fontsize=28, fontweight="bold", color="#111827")

# ---------------------------
# Segunda franja: KPIs
# ---------------------------
draw_card(axes[1,0], "Ventas Volvo", ventas["Volvo"])
draw_card(axes[1,1], "Ventas Kia", ventas["Kia"])
draw_card(axes[1,2], "Ventas Hyundai", ventas["Hyundai"])

# ---------------------------
# Tercera franja: gráficos
# ---------------------------
def draw_sales_graph(ax, marca, color):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")
    # tarjeta
    ax.add_patch(FancyBboxPatch(
        (2,6), 92, 52, boxstyle="round,pad=0.02,rounding_size=12",
        linewidth=1.5, edgecolor="#E5E7EB", facecolor="white"
    ))
    # título gráfico
    ax.text(50, 55, f"Ventas {marca}", ha="center", fontsize=14, color="#111827")
    # preparar datos
    df_marca = df[df["marca"]==marca].groupby("fecha")["ventas"].sum().reset_index()
    # coordenadas para gráfico
    x = list(range(len(df_marca)))
    y = df_marca["ventas"].tolist()
    # normalizar a la tarjeta
    max_y = max(y) if max(y)>0 else 1
    y_scaled = [v/max_y*40 for v in y]  # escala 0-40 dentro de tarjeta
    x_scaled = [10 + i*20 for i in x]   # distribuye barras horizontal
    # dibujar barras
    for xi, yi in zip(x_scaled, y_scaled):
        ax.add_patch(FancyBboxPatch(
            (xi, 10), 12, yi,
            boxstyle="round,pad=0.02",
            facecolor=color, linewidth=0
        ))

# dibujar gráficos
draw_sales_graph(axes[2,0], "Volvo", "#2563EB")
draw_sales_graph(axes[2,1], "Kia", "#10B981")
draw_sales_graph(axes[2,2], "Hyundai", "#F59E0B")

# ---------------------------
# Guardar y mostrar
# ---------------------------
plt.tight_layout()
plt.savefig("dashboard_con_graficos.png", dpi=200, bbox_inches="tight")
plt.show()