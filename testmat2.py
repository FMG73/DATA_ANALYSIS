import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.family"] = "Segoe UI"

fig, ax = plt.subplots(figsize=(4, 2))
fig.patch.set_facecolor("#F3F4F6")
ax.axis("off")

# sombra
ax.add_patch(FancyBboxPatch(
    (0.05, 0.05), 0.9, 0.85,
    boxstyle="round,pad=0.02,rounding_size=20",
    linewidth=0,
    facecolor="black",
    alpha=0.1,
    transform=ax.transAxes
))

# card
ax.add_patch(FancyBboxPatch(
    (0.03, 0.1), 0.9, 0.85,
    boxstyle="round,pad=0.02,rounding_size=20",
    linewidth=1.2,
    edgecolor="#E5E7EB",
    facecolor="white",
    transform=ax.transAxes
))

ax.text(0.5, 0.6, "VENDIDOS",
        ha="center", va="center",
        fontsize=12, color="#6B7280",
        transform=ax.transAxes)

ax.text(0.5, 0.35, "123",
        ha="center", va="center",
        fontsize=28, fontweight="bold",
        color="#111827",
        transform=ax.transAxes)

plt.show()