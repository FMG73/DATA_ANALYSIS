import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import gridspec

plt.rcParams["font.family"] = "Segoe UI"

# ---------------------------
# DATOS
# ---------------------------
df = pd.read_csv("ventas.csv", parse_dates=["fecha"])

total_vendidos = df["vendido"].sum()
facturacion = df["importe"].sum()
pct_adj = round((df["adjudicado"] == "Sí").mean() * 100, 1)

# ---------------------------
# FIGURA PRINCIPAL
# ---------------------------
fig = plt.figure(figsize=(16, 9))
fig.patch.set_facecolor("#F3F4F6")

gs = gridspec.GridSpec(
    3, 3,
    height_ratios=[0.7, 1, 2],
    hspace=0.4,
    wspace=0.3
)

# ---------------------------
# FUNCIÓN CARD (CORRECTA)
# ---------------------------
def card(ax):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")

    ax.add_patch(FancyBboxPatch(
        (4, 4), 92, 52,
        boxstyle="round,pad=0.02,rounding_size=14",
        linewidth=0,
        facecolor="black",
        alpha=0.12
    ))

    ax.add_patch(FancyBboxPatch(
        (2, 6), 92, 52,
        boxstyle="round,pad=0.02,rounding_size=14",
        linewidth=1.4,
        edgecolor="#E5E7EB",
        facecolor="white"
    ))

# ---------------------------
# TÍTULO
# ---------------------------
ax_title = plt.subplot(gs[0, :])
card(ax_title)
ax_title.text(50, 38, "Dashboard Ventas Coches",
              ha="center", fontsize=30, fontweight="bold",
              color="#111827")
ax_title.text(50, 22, "Resumen ejecutivo mensual",
              ha="center", fontsize=14, color="#6B7280")

# ---------------------------
# KPIs
# ---------------------------
kpis = [
    ("VENDIDOS", total_vendidos),
    ("FACTURACIÓN", f"{facturacion:,.0f} €"),
    ("% ADJUDICADOS", f"{pct_adj}%")
]

for i, (t, v) in enumerate(kpis):
    ax = plt.subplot(gs[1, i])
    card(ax)
    ax.text(50, 35, t, ha="center",
            fontsize=13, color="#6B7280")
    ax.text(50, 20, v, ha="center",
            fontsize=28, fontweight="bold",
            color="#111827")

# ---------------------------
# GRÁFICOS
# ---------------------------

# Ventas por día
ax1 = plt.subplot(gs[2, 0])
card(ax1)
ventas_dia = df.groupby("fecha")["vendido"].sum()
ax1.plot(ventas_dia.index, ventas_dia.values,
         linewidth=3, color="#2563EB")
ax1.set_title("Ventas diarias", fontsize=14, pad=15)

# Top modelos
ax2 = plt.subplot(gs[2, 1])
card(ax2)
top = df.groupby("modelo")["vendido"].sum().sort_values()
ax2.barh(top.index, top.values, color="#60A5FA")
ax2.set_title("Top modelos", fontsize=14, pad=15)

# Estado
ax3 = plt.subplot(gs[2, 2])
card(ax3)
sizes = [(df["adjudicado"] == "Sí").sum(),
         (df["adjudicado"] == "No").sum()]
ax3.pie(sizes, colors=["#2563EB", "#E5E7EB"],
        autopct="%1.0f%%", startangle=90)
ax3.set_title("Estado ventas", fontsize=14, pad=15)

# ---------------------------
# GUARDAR
# ---------------------------
plt.savefig("dashboard_ventas.png", dpi=200, bbox_inches="tight")
plt.close()