import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ======================================================
# CONFIGURACIÓN VISUAL POR FILA (TOCAR SOLO AQUÍ)
# ======================================================

ROW_STYLES = {
    "fila_usuarios": {
        "row_bg": "#F4F6FA",
        "card_bg": "#FFFFFF",
        "border_color": "#D0D5DD",
        "border_width": 1.2,
        "border_radius": 18,

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
        "value_size": 26
    },

    "fila_vehiculos": {
        "row_bg": "#0F172A",
        "card_bg": "#111827",
        "border_color": "#334155",
        "border_width": 1.5,
        "border_radius": 20,

        "shadow": {
            "enabled": True,
            "dx": 0.012,
            "dy": -0.012,
            "color": "#000000",
            "alpha": 0.35
        },

        "font": "DejaVu Sans Mono",
        "title_color": "#CBD5E1",
        "value_color": "#F9FAFB",
        "title_size": 12,
        "value_size": 26
    }
}

# ======================================================
# FUNCIONES DE DIBUJO
# ======================================================

def draw_card(ax, title, value, style):
    """
    Dibuja una tarjeta KPI con estilo configurable
    """
    ax.axis("off")

    # ---------------------------
    # Sombra
    # ---------------------------
    if style["shadow"]["enabled"]:
        shadow = FancyBboxPatch(
            (0.05 + style["shadow"]["dx"], 0.05 + style["shadow"]["dy"]),
            0.9, 0.9,
            boxstyle=f"round,pad=0.02,rounding_size={style['border_radius']}",
            linewidth=0,
            facecolor=style["shadow"]["color"],
            alpha=style["shadow"]["alpha"]
        )
        ax.add_patch(shadow)

    # ---------------------------
    # Tarjeta principal
    # ---------------------------
    card = FancyBboxPatch(
        (0.05, 0.05),
        0.9, 0.9,
        boxstyle=f"round,pad=0.02,rounding_size={style['border_radius']}",
        linewidth=style["border_width"],
        edgecolor=style["border_color"],
        facecolor=style["card_bg"]
    )
    ax.add_patch(card)

    # ---------------------------
    # Texto título
    # ---------------------------
    ax.text(
        0.5, 0.65,
        title,
        ha="center", va="center",
        fontsize=style["title_size"],
        color=style["title_color"],
        fontname=style["font"]
    )

    # ---------------------------
    # Texto KPI
    # ---------------------------
    value = 0 if pd.isna(value) else value

    ax.text(
        0.5, 0.35,
        f"{int(value):,}".replace(",", "."),
        ha="center", va="center",
        fontsize=style["value_size"],
        color=style["value_color"],
        fontname=style["font"],
        fontweight="bold"
    )


def draw_row(fig, y, height, cards, row_style):
    """
    Dibuja una fila completa de tarjetas KPI
    """

    # Fondo de fila
    bg_ax = fig.add_axes([0, y, 1, height])
    bg_ax.set_facecolor(row_style["row_bg"])
    bg_ax.axis("off")

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

        draw_card(
            ax,
            card["title"],
            card["value"],
            row_style
        )

# ======================================================
# CARGA DE DATOS
# ======================================================

df = pd.read_csv("html_test.csv")
data = df.iloc[0]  # KPIs únicos

# ======================================================
# DEFINICIÓN DE TARJETAS
# ======================================================

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

# ======================================================
# DASHBOARD
# ======================================================

fig = plt.figure(figsize=(18, 10))

# Alturas relativas
TITLE_HEIGHT = 0.18
ROW_HEIGHT = (1 - TITLE_HEIGHT) / 2

# ---------------------------
# Título
# ---------------------------
title_ax = fig.add_axes([0, 1 - TITLE_HEIGHT, 1, TITLE_HEIGHT])
title_ax.axis("off")
title_ax.text(
    0.5, 0.5,
    "Dashboard de Ventas – KPIs Operativos",
    ha="center", va="center",
    fontsize=30,
    fontweight="bold"
)

# ---------------------------
# Filas
# ---------------------------
draw_row(
    fig,
    1 - TITLE_HEIGHT - ROW_HEIGHT,
    ROW_HEIGHT,
    ROW_2_CARDS,
    ROW_STYLES["fila_usuarios"]
)

draw_row(
    fig,
    0,
    ROW_HEIGHT,
    ROW_3_CARDS,
    ROW_STYLES["fila_vehiculos"]
)

plt.show()

# ======================================================
# GUARDAR PARA OUTLOOK (OPCIONAL)
# ======================================================
# plt.savefig("dashboard.png", dpi=150, bbox_inches="tight")