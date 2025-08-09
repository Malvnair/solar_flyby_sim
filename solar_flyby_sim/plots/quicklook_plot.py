import os
import pandas as pd
import matplotlib.pyplot as plt

print("RUNNING:", os.path.abspath(__file__))

# Load elements
df = pd.read_parquet("outputs/smoke/elements.parquet").query('name != "Sun"')
bodies = df["name"].unique()

fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)

for body in bodies:
    sub = df[df["name"] == body]
    axes[0].plot(sub["t"], sub["a"], label=body, linewidth=1.5)
    axes[1].plot(sub["t"], sub["e"], label=body, linewidth=1.5)

# Labels
axes[0].set_ylabel("Semi-major axis, a [AU]", fontsize=12)
axes[1].set_ylabel("Eccentricity, e", fontsize=12)
axes[1].set_xlabel("Time [yr]", fontsize=12)

# Styling
for ax in axes:
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.tick_params(axis="both", which="major", labelsize=10)
    ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

axes[0].legend(fontsize=10, loc="best", frameon=True)

# Title
fig.suptitle("Smoke Test — Orbital Elements", fontsize=14, fontweight="bold", y=0.98)

# Save + show
plt.tight_layout(rect=[0, 0, 1, 0.96])
outpath = "outputs/smoke/smoke_test_orbital_elements.png"
plt.savefig(outpath, dpi=300)
print("Saved:", os.path.abspath(outpath))
plt.show()
