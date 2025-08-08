import pandas as pd
import matplotlib.pyplot as plt

# Load the elements file
df = pd.read_parquet("outputs/smoke/elements.parquet")

# Filter out the Sun (we don't plot it)
df = df[df["name"] != "Sun"]

# Group by body
bodies = df["name"].unique()

fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

for body in bodies:
    sub = df[df["name"] == body]
    axes[0].plot(sub["t"], sub["a"], label=body)
    axes[1].plot(sub["t"], sub["e"], label=body)

axes[0].set_ylabel("a [AU]")
axes[1].set_ylabel("e")
axes[1].set_xlabel("Time [yr]")

axes[0].legend()
plt.suptitle("Smoke Test — Orbital Elements")
plt.tight_layout()
plt.show()
