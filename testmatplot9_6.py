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
    "card_styles": {  # configurable por fila
        "row_2": {  # fila usuarios
            "radius": 18,
            "shadow_alpha": 0.12,
            "border_color": "#E5E7EB",
            "background": "#FFFFFF",
            "title_color": "#6B7280",
            "value_color": "#111827"
        },
        "row_3": {  # fila vehículos
            "radius": 18,
            "shadow_alpha": 0.18,
            "border_color": "#CBD5E1",
            "background": "#F9FAFB",
            "title_color": "#475467",
            "value_color": "#101828"
        }
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
def draw_card(ax, title, value, style):
    """Dibuja una tarjeta KPI con sombra y bordes redondeados"""
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")

    # sombra
    ax.add_patch(FancyBboxPatch(
        (5, 4), 90, 52,
        boxstyle=f"round,pad=0.02,rounding_size={style['radius']}",
        linewidth=0,
        facecolor="black",
        alpha=style["shadow_alpha"]
    ))

    # tarjeta principal
    ax.add_patch(FancyBboxPatch(
        (3, 6), 90, 52,
        boxstyle=f"round,pad=0.02,rounding_size={style['radius']}",
        linewidth=1.4,
        edgecolor=style["border_color"],
        facecolor=style["background"]
    ))

    # título
    ax.text(50, 36, title,
            ha="center", fontsize=13,
            color=style["title_color"])

    # valor KPI
    value = 0 if pd.isna(value) else value
    ax.text(50, 20, f"{int(value):,}".replace(",", "."),
            ha="center", fontsize=28,
            fontweight="bold",
            color=style["value_color"])

def draw_row_as_image(cards, row_name, filename, width=18, height=3):
    """
    Dibuja una fila de tarjetas y guarda como imagen independiente
    """
    fig = plt.figure(figsize=(width, height))
    style = DASHBOARD_CONFIG["card_styles"][row_name]
    n = len(cards)
    for i, card in enumerate(cards):
        ax = fig.add_axes([
            i / n,
            0,
            1 / n,
            1
        ])
        draw_card(ax, card["title"], data[card["col"]], style)
    fig.patch.set_facecolor(DASHBOARD_CONFIG["background"])
    plt.axis("off")
    plt.savefig(filename, dpi=200, bbox_inches="tight", transparent=True)
    plt.close(fig)

def draw_title_as_image(filename, width=18, height=2):
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.text(
        0.5, 0.5,
        DASHBOARD_CONFIG["title"]["text"],
        ha="center", va="center",
        fontsize=DASHBOARD_CONFIG["title"]["fontsize"],
        fontweight="bold",
        color=DASHBOARD_CONFIG["title"]["color"]
    )
    fig.patch.set_facecolor(DASHBOARD_CONFIG["background"])
    plt.savefig(filename, dpi=200, bbox_inches="tight", transparent=True)
    plt.close(fig)

# =========================
# GENERAR IMÁGENES
# =========================
draw_title_as_image("dashboard_title.png")
draw_row_as_image(ROW_2_CARDS, "row_2", "fila_usuarios.png", height=3)
draw_row_as_image(ROW_3_CARDS, "row_3", "fila_vehiculos.png", height=3)

print("✅ Imágenes generadas: dashboard_title.png, fila_usuarios.png, fila_vehiculos.png")