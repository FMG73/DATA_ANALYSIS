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

# ---------------------------
# Calcular ventas totales por marca
# ---------------------------
df["ventas"] = df["gasolina"] + df["diesel"] + df["electrico"]
ventas_volvo = df[df["marca"]=="Volvo"]["ventas"].sum()
ventas_kia = df[df["marca"]=="Kia"]["ventas"].sum()
ventas_hyundai = df[df["marca"]=="Hyundai"]["ventas"].sum()

# ---------------------------
# Crear figura
# ---------------------------
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
fig.patch.set_facecolor("#F3F4F6")

# Primera franja: título (ocupa toda la primera fila)
ax_title = axes[0, 0]
ax_title.axis("off")
ax_title.text(0.5, 0.5, "Dashboard Ventas Coches",
              ha="center", va="center",
              fontsize=30, fontweight="bold",
              color="#111827", transform=ax_title.transAxes)

# Ocultar las otras dos celdas de la primera fila
axes[0, 1].axis("off")
axes[0, 2].axis("off")

# ---------------------------
# Función para tarjeta KPI
# ---------------------------
def draw_card(ax, title, value):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")
    # sombra
    ax.add_patch(FancyBboxPatch(
        (4, 4), 92, 52,
        boxstyle="round,pad=0.02,rounding_size=12",
        linewidth=0, facecolor="black", alpha=0.12
    ))
    # tarjeta
    ax.add_patch(FancyBboxPatch(
        (2, 6), 92, 52,
        boxstyle="round,pad=0.02,rounding_size=12",
        linewidth=1.5, edgecolor="#E5E7EB", facecolor="white"
    ))
    # texto
    ax.text(50, 35, title, ha="center", fontsize=14, color="#6B7280")
    ax.text(50, 20, value, ha="center", fontsize=28, fontweight="bold", color="#111827")

# ---------------------------
# Segunda franja: tres tarjetas
# ---------------------------
draw_card(axes[1,0], "Ventas Volvo", ventas_volvo)
draw_card(axes[1,1], "Ventas Kia", ventas_kia)
draw_card(axes[1,2], "Ventas Hyundai", ventas_hyundai)

# ---------------------------
# Guardar imagen
# ---------------------------
plt.tight_layout()
plt.savefig("dashboard_simple.png", dpi=200, bbox_inches="tight")
plt.show()