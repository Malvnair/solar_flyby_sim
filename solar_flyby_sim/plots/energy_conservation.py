import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
angmom = pd.read_csv("outputs/control/angmom.csv")
energy = pd.read_csv("outputs/control/energy.csv")

# Compute L_tot from components
L_tot = np.sqrt(angmom["Lx"]**2 + angmom["Ly"]**2 + angmom["Lz"]**2)

# Angular momentum plot
plt.figure()
plt.plot(angmom["t"], L_tot)
plt.xlabel("Time [yr]")
plt.ylabel("Total Angular Momentum L_tot")
plt.title("Angular Momentum Conservation")
plt.grid()

# Energy plot
plt.figure()
plt.plot(energy["t"], energy["E"])
plt.xlabel("Time [yr]")
plt.ylabel("Total Energy")
plt.title("Energy Conservation")
plt.grid()

plt.savefig("Energy Conservation")
plt.show()
