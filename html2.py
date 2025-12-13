import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import gridspec
import win32com.client as win32
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================
CSV_PATH = r"C:\ruta\ventas.csv"
MSG_TEMPLATE = r"C:\ruta\plantilla_dashboard.msg"
IMG_PATH = r"C:\ruta\dashboard_ventas.png"

plt.rcParams["font.family"] = "Segoe UI"

# =====================================================
# 1. LEER DATOS
# =====================================================
df = pd.read_csv(CSV_PATH, parse_dates=["fecha"])

total_vendidos = df["vendido"].sum()
facturacion = df["importe"].sum()
pct_adjud = round((df["adjudicado"] == "Sí").mean() * 100, 1)

# =====================================================
# 2. CREAR DASHBOARD (IMAGEN)
# =====================================================
fig = plt.figure(figsize=(16, 9))
fig.patch.set_facecolor("#F3F4F6")

gs = gridspec.GridSpec(
    3, 3,
    height_ratios=[0.6, 1, 2],
    hspace=0.35,
    wspace=0.25
)

def draw_card(ax, title=None, value=None):
    ax.axis("off")

    # sombra
    ax.add_patch(FancyBboxPatch(
        (0.02, -0.02), 0.96, 1.02,
        boxstyle="round,pad=0.02,rounding_size=20",
        linewidth=0,
        facecolor="black",
        alpha=0.08,
        transform=ax.transAxes
    ))

    # card
    ax.add_patch(FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.02,rounding_size=20",
        linewidth=1.2,
        edgecolor="#E5E7EB",
        facecolor="white",
        transform=ax.transAxes
    ))

    if title:
        ax.text(0.5, 0.65, title,
                ha="center", va="center",
                fontsize=13, color="#6B7280",
                transform=ax.transAxes)

    if value is not None:
        ax.text(0.5, 0.35, value,
                ha="center", va="center",
                fontsize=28, fontweight="bold",
                color="#111827",
                transform=ax.transAxes)

# ---------------- TÍTULO ----------------
ax_title = plt.subplot(gs[0, :])
draw_card(ax_title)
ax_title.text(0.5, 0.6, "Dashboard Ventas Coches",
              ha="center", va="center",
              fontsize=30, fontweight="bold",
              color="#111827",
              transform=ax_title.transAxes)
ax_title.text(0.5, 0.3, "Resumen ejecutivo mensual",
              ha="center", va="center",
              fontsize=14, color="#6B7280",
              transform=ax_title.transAxes)

# ---------------- KPIs ----------------
kpis = [
    ("Vendidos", total_vendidos),
    ("Facturación", f"{facturacion:,.0f} €"),
    ("% Adjudicados", f"{pct_adjud}%")
]

for i, (t, v) in enumerate(kpis):
    ax = plt.subplot(gs[1, i])
    draw_card(ax, t, v)

# ---------------- GRÁFICOS ----------------

# Ventas por día
ax1 = plt.subplot(gs[2, 0])
draw_card(ax1)
ventas_dia = df.groupby("fecha")["vendido"].sum()
ax1.plot(ventas_dia.index, ventas_dia.values,
         linewidth=3, color="#2563EB")
ax1.set_title("Ventas diarias", fontsize=14, pad=15)
ax1.grid(alpha=0.2)

# Top modelos
ax2 = plt.subplot(gs[2, 1])
draw_card(ax2)
top_modelos = df.groupby("modelo")["vendido"].sum().sort_values()
ax2.barh(top_modelos.index, top_modelos.values,
         color="#60A5FA")
ax2.set_title("Top modelos", fontsize=14, pad=15)

# Estado ventas
ax3 = plt.subplot(gs[2, 2])
draw_card(ax3)
labels = ["Adjudicados", "No adjudicados"]
sizes = [
    (df["adjudicado"] == "Sí").sum(),
    (df["adjudicado"] == "No").sum()
]
ax3.pie(
    sizes,
    labels=labels,
    autopct="%1.0f%%",
    startangle=90,
    colors=["#2563EB", "#E5E7EB"],
    wedgeprops={"edgecolor": "white", "linewidth": 2}
)
ax3.set_title("Estado ventas", fontsize=14, pad=15)

# ---------------- GUARDAR IMAGEN ----------------
plt.savefig(IMG_PATH, dpi=200, bbox_inches="tight")
plt.close()

# =====================================================
# 3. OUTLOOK – INSERTAR IMAGEN EN .MSG
# =====================================================
outlook = win32.Dispatch("Outlook.Application")
mail = outlook.CreateItemFromTemplate(MSG_TEMPLATE)

# Adjuntar imagen como CID
attachment = mail.Attachments.Add(IMG_PATH)
cid = "dashboard_img"
attachment.PropertyAccessor.SetProperty(
    "http://schemas.microsoft.com/mapi/proptag/0x3712001F",
    cid
)

# Reemplazar marcador
mail.HTMLBody = mail.HTMLBody.replace(
    "#DASHBOARD#",
    f'<img src="cid:{cid}" style="width:100%;">'
)

mail.Display()  # o mail.Send()