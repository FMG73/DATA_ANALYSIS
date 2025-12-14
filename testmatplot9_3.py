import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ======================================================
# CONFIGURACIÓN DE ESTILO DE TARJETAS POR FILA
# ======================================================
CARD_STYLES = {
    "row_usuarios": {  # fila 2
        "card_bg": "#FFFFFF",
        "border_color": "#D0D5DD",
        "border_width": 1.2,
        "shadow": {
            "enabled": True,
            "dx": 0.01,
            "dy": -0.01,
            "color": "#000000",
            "alpha": 0.12
        },
        "font": "DejaVu Sans",
        "title_color": "#475467",
        "value_color": "#101828",
        "title_size": 12,
        "value_size": 26,
        "border_radius": 18
    },
    "row_vehiculos": {  # fila 3
        "card_bg": "#111827",
        "border_color": "#334155",
        "border_width": 1.5,
        "shadow": {
            "enabled": True,
            "dx": 0.01,
            "dy": -0.01,
            "color": "#000000",
            "alpha": 0.30
        },
        "font": "DejaVu Sans Mono",
        "title_color": "#CBD5E1",
        "value_color": "#F9FAFB",
        "title_size": 12,
        "value_size": 26,
        "border_radius": 20
    }
}

# ======================================================
# FUNCIONES DE DIBUJO
# ======================================================
def draw_card(ax, title, value, card_style):
    """
    Dibuja una tarjeta usando el estilo definido en card_style
    """
    ax.axis("off")

    # ---------------------------
    # Sombra
    # ---------------------------
    if card_style["shadow"]["enabled"]:
        shadow = FancyBboxPatch(
            (0.05 + card_style["shadow"]["dx"], 0.05 + card_style["shadow"]["dy"]),
            0.9, 0.9,
            boxstyle="round,pad=0.02",
            linewidth=0,
            facecolor=card_style["shadow"]["color"],
            alpha=card_style["shadow"]["alpha"]
        )
        ax.add_patch(shadow)

    # ---------------------------
    # Tarjeta principal
    # ---------------------------
    card = FancyBboxPatch(
        (0.05, 0.05),
        0.9, 0.9,
        boxstyle="round,pad=0.02",
        linewidth=card_style["border_width"],
        edgecolor=card_style["border_color"],
        facecolor=card_style["card_bg"]
    )
    ax.add_patch(card)

    # ---------------------------
    # Texto título
    # ---------------------------
    ax.text(
        0.5, 0.62,
        title,
        ha="center", va="center",
        fontsize=card_style["title_size"],
        color=card_style["title_color"],
        fontname=card_style["font"]
    )

    # ---------------------------
    # Texto KPI
    # ---------------------------
    value = 0 if pd.isna(value) else value
    ax.text(
        0.5, 0.38,
        f"{int(value):,}".replace(",", "."),
        ha="center", va="center",
        fontsize=card_style["value_size"],
        color=card_style["value_color"],
        fontname=card_style["font"],
        fontweight="bold"
    )

def draw_row(fig, y, height, cards, row_name):
    """
    Dibuja una fila completa de tarjetas usando CARD_STYLES
    """
    # Fondo de fila
    bg_ax = fig.add_axes([0, y, 1, height])
    bg_ax.set_facecolor("#F4F6FA")  # color de fondo fila, opcional
    bg_ax.axis("off")

    # Seleccionamos el estilo de tarjeta según fila
    card_style = CARD_STYLES[row_name]

    # Distribución automática
    n_cards = len(cards)
    card_width = 1 / n_cards

    for i, card in enumerate(cards):
        ax = fig.add_axes([
            i * card_width,
            y,
            card_width,
            height
        ])
        draw_card(ax, card["title"], card["value"], card_style)

# ======================================================
# CARGA DE DATOS
# ======================================================
df = pd.read_csv("html_test.csv")
data = df.iloc[0]  # solo la primera fila para KPIs

# ======================================================
# TARJETAS POR FILA
# ======================================================
ROW_2_CARDS = [
    {"title": "Nº Lista", "value": data["n_lista"]},
    {"title": "Usuarios", "value": data["usuarios"]},
    {"title": "Conectados", "value": data["usuarios_conectados"]},
    {"title": "Con Oferta", "value": data["usuarios_con_oferta"]},
    {"title": "Con Adjudicación", "value": data["usuarios_con_adjudicacion"]}
]

ROW_3_CARDS = [
    {"title": "Vehículos Publicados", "value": data["vehiculos_publicados"]},
    {"title": "Con Oferta", "value": data["vehiculos_oferta"]},
    {"title": "Adjudicados", "value": data["vehiculos_adjudicados"]},
    {"title": "Plazo Medio", "value": data["plazo_medio"]},
    {"title": "KM Medio", "value": data["km_medio"]}
]

# ======================================================
# CREAR DASHBOARD
# ======================================================
fig = plt.figure(figsize=(18, 10))

TITLE_HEIGHT = 0.18
ROW_HEIGHT = (1 - TITLE_HEIGHT)/2

# ---------------------------
# TÍTULO
# ---------------------------
title_ax = fig.add_axes([0, 1 - TITLE_HEIGHT, 1, TITLE_HEIGHT])
title_ax.axis("off")
title_ax.text(
    0.5, 0.5,
    "Dashboard Ventas",
    ha="center", va="center",
    fontsize=30,
    fontweight="bold"
)

# ---------------------------
# FILAS
# ---------------------------
draw_row(fig, 1 - TITLE_HEIGHT - ROW_HEIGHT, ROW_HEIGHT, ROW_2_CARDS, "row_usuarios")
draw_row(fig, 0, ROW_HEIGHT, ROW_3_CARDS, "row_vehiculos")

plt.show()

# ======================================================
# OPCIONAL: GUARDAR PARA OUTLOOK
# ======================================================
# plt.savefig("dashboard.png", dpi=150, bbox_inches="tight")