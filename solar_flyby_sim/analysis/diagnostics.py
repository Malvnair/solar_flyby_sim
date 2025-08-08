import numpy as np

class Diagnostics:
    def __init__(self, sim):
        self.sim = sim

    def energy(self):
        # REBOUND API: sim.energy()
        return self.sim.energy()

    def angular_momentum(self):
        # REBOUND API: sim.angular_momentum() -> (Lx, Ly, Lz)
        Lx, Ly, Lz = self.sim.angular_momentum()
        return np.array([Lx, Ly, Lz])
