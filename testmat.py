import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots()
ax.add_patch(
    FancyBboxPatch((0, 0), 1, 1, boxstyle="round")
)
plt.show()