import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Segoe UI"

fig, ax = plt.subplots(figsize=(4, 2))
fig.patch.set_facecolor("#F3F4F6")

# Sistema de coordenadas estable
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.set_aspect("equal")
ax.axis("off")

# sombra
shadow = FancyBboxPatch(
    (5, 5), 90, 40,
    boxstyle="round,pad=0.02,rounding_size=12",
    linewidth=0,
    facecolor="black",
    alpha=0.12
)
ax.add_patch(shadow)

# card
card = FancyBboxPatch(
    (3, 7), 90, 40,
    boxstyle="round,pad=0.02,rounding_size=12",
    linewidth=1.5,
    edgecolor="#E5E7EB",
    facecolor="white"
)
ax.add_patch(card)

# texto
ax.text(50, 32, "VENDIDOS",
        ha="center", va="center",
        fontsize=12, color="#6B7280")

ax.text(50, 20, "123",
        ha="center", va="center",
        fontsize=28, fontweight="bold",
        color="#111827")

plt.show()