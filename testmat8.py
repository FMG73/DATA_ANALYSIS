import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# =========================
# CONFIGURACIÓN GLOBAL
# =========================
DASHBOARD_CONFIG = {
    "figsize": (18, 10),
    "background": "#F3F4F6",
    "font_family": "Segoe UI",
    "title": {
        "text": "Dashboard Actividad Plataforma",
        "fontsize": 32,
        "color": "#111827",
        "height": 0.18
    },
    "rows": {
        "row_2_height": 0.41,
        "row_3_height": 0.41
    },
    "card_style": {
        "radius": 18,
        "shadow_alpha": 0.12,
        "border_color": "#E5E7EB",
        "background": "white",
        "title_color": "#6B7280",
        "value_color": "#111827"
    }
}

plt.rcParams["font.family"] = DASHBOARD_CONFIG["font_family"]

# =========================
# DEFINICIÓN DE TARJETAS
# =========================
ROW_2_CARDS = [
    {"col": "n_lista", "title": "Nº Listas"},
    {"col": "usuarios", "title": "Usuarios"},
    {"col": "usuarios_conectados", "title": "Usuarios conectados"},
    {"col": "usuarios_oferta", "title": "Usuarios con oferta"},
    {"col": "usuarios_adjudicacion", "title": "Usuarios con adjudicación"},
]

ROW_3_CARDS = [
    {"col": "vehiculos_publicados", "title": "Vehículos publicados"},
    {"col": "vehiculos_oferta", "title": "Vehículos con oferta"},
    {"col": "vehiculos_adjudicados", "title": "Vehículos adjudicados"},
    {"col": "plazo_medio", "title": "Plazo medio (días)"},
    {"col": "km_medio", "title": "KM medio"},
]

# =========================
# CARGA DATOS
# =========================
df = pd.read_csv("html_test.csv")
data = df.iloc[0]

# =========================
# FUNCIONES DE DIBUJO
# =========================
def draw_card(ax, title, value):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")

    # sombra
    ax.add_patch(FancyBboxPatch(
        (5, 4), 90, 52,
        boxstyle=f"round,pad=0.02,rounding_size={DASHBOARD_CONFIG['card_style']['radius']}",
        linewidth=0,
        facecolor="black",
        alpha=DASHBOARD_CONFIG["card_style"]["shadow_alpha"]
    ))

    # tarjeta
    ax.add_patch(FancyBboxPatch(
        (3, 6), 90, 52,
        boxstyle=f"round,pad=0.02,rounding_size={DASHBOARD_CONFIG['card_style']['radius']}",
        linewidth=1.4,
        edgecolor=DASHBOARD_CONFIG["card_style"]["border_color"],
        facecolor=DASHBOARD_CONFIG["card_style"]["background"]
    ))

    ax.text(50, 36, title,
            ha="center", fontsize=13,
            color=DASHBOARD_CONFIG["card_style"]["title_color"])

    ax.text(50, 20, f"{int(value):,}".replace(",", "."),
            ha="center", fontsize=28,
            fontweight="bold",
            color=DASHBOARD_CONFIG["card_style"]["value_color"])

def draw_row(fig, y_start, height, cards):
    n = len(cards)
    for i, card in enumerate(cards):
        ax = fig.add_axes([
            i / n,
            y_start,
            1 / n,
            height
        ])
        draw_card(ax, card["title"], data[card["col"]])

# =========================
# CREAR FIGURA
# =========================
fig = plt.figure(figsize=DASHBOARD_CONFIG["figsize"])
fig.patch.set_facecolor(DASHBOARD_CONFIG["background"])

# =========================
# TÍTULO
# =========================
ax_title = fig.add_axes([0, 1 - DASHBOARD_CONFIG["title"]["height"], 1, DASHBOARD_CONFIG["title"]["height"]])
ax_title.axis("off")
ax_title.text(
    0.5, 0.5,
    DASHBOARD_CONFIG["title"]["text"],
    ha="center",
    va="center",
    fontsize=DASHBOARD_CONFIG["title"]["fontsize"],
    fontweight="bold",
    color=DASHBOARD_CONFIG["title"]["color"]
)

# =========================
# FILAS KPI
# =========================
draw_row(
    fig,
    y_start=DASHBOARD_CONFIG["rows"]["row_3_height"],
    height=DASHBOARD_CONFIG["rows"]["row_2_height"],
    cards=ROW_2_CARDS
)

draw_row(
    fig,
    y_start=0,
    height=DASHBOARD_CONFIG["rows"]["row_3_height"],
    cards=ROW_3_CARDS
)

# =========================
# GUARDAR
# =========================
plt.savefig("dashboard_kpi_premium.png", dpi=200, bbox_inches="tight")
plt.show()