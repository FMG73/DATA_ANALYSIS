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
    # Estilo por defecto de todas las tarjetas
    "card_style_default": {
        "radius": 18,
        "shadow_alpha": 0.12,
        "border_color": "#E5E7EB",
        "background": "white",
        "title_color": "#6B7280",
        "value_color": "#111827"
    },
    # NUEVO: Estilos específicos por fila (sobrescriben el default)
    # Puedes modificar o eliminar cualquiera de estos bloques según necesites
    "row_styles": {
        "row_2": {  # Fila superior → tono azul elegante
            "background": "#EFF6FF",
            "border_color": "#3B82F6",
            "title_color": "#1E40AF",
            "value_color": "#1E3A8A",
            "shadow_alpha": 0.18,
            "radius": 20
        },
        "row_3": {  # Fila inferior → tono verde suave
            "background": "#F0FDF4",
            "border_color": "#10B981",
            "title_color": "#065F46",
            "value_color": "#064E3B",
            "shadow_alpha": 0.15,
            "radius": 16
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
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")

    # Extraer valores con fallback al default
    radius = style.get("radius", DASHBOARD_CONFIG["card_style_default"]["radius"])
    shadow_alpha = style.get("shadow_alpha", DASHBOARD_CONFIG["card_style_default"]["shadow_alpha"])
    border_color = style.get("border_color", DASHBOARD_CONFIG["card_style_default"]["border_color"])
    background = style.get("background", DASHBOARD_CONFIG["card_style_default"]["background"])
    title_color = style.get("title_color", DASHBOARD_CONFIG["card_style_default"]["title_color"])
    value_color = style.get("value_color", DASHBOARD_CONFIG["card_style_default"]["value_color"])

    # Sombra
    ax.add_patch(FancyBboxPatch(
        (5, 4), 90, 52,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=0,
        facecolor="black",
        alpha=shadow_alpha
    ))

    # Tarjeta principal
    ax.add_patch(FancyBboxPatch(
        (3, 6), 90, 52,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=1.4,
        edgecolor=border_color,
        facecolor=background
    ))

    # Título
    ax.text(50, 36, title,
            ha="center", fontsize=13,
            color=title_color)

    # Valor grande
    ax.text(50, 20, f"{int(value):,}".replace(",", "."),
            ha="center", fontsize=28,
            fontweight="bold",
            color=value_color)


def draw_row(fig, y_start, height, cards, row_key=None):
    n = len(cards)
    
    # Determinar estilo de la fila
    row_style = DASHBOARD_CONFIG["row_styles"].get(row_key, {})
    
    # Combinar default + estilo específico de fila (la fila sobrescribe)
    card_style = {**DASHBOARD_CONFIG["card_style_default"], **row_style}
    
    for i, card in enumerate(cards):
        ax = fig.add_axes([
            i / n,
            y_start,
            1 / n,
            height
        ])
        draw_card(ax, card["title"], data[card["col"]], card_style)


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
    cards=ROW_2_CARDS,
    row_key="row_2"          # Aplica el estilo definido para row_2
)

draw_row(
    fig,
    y_start=0,
    height=DASHBOARD_CONFIG["rows"]["row_3_height"],
    cards=ROW_3_CARDS,
    row_key="row_3"          # Aplica el estilo definido para row_3
)

# =========================
# GUARDAR Y MOSTRAR
# =========================
plt.savefig("dashboard_kpi_premium.png", dpi=200, bbox_inches="tight")
plt.show()