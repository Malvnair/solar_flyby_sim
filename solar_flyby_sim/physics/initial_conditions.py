"""J2000 initial conditions from JPL Horizons.

This module will:
- query (or load cached) J2000 osculating elements for Sun+planets+Moon+Pluto
  plus Ceres, Vesta, Pallas, Hygiea, and {Eris, Haumea, Makemake, Quaoar,
  Gonggong, Sedna}.
- convert to barycentric Cartesian state vectors in AU, AU/yr, Msun units.
- apply micro-jitter (~±2 cm) in Cartesian coordinates for mean anomaly randomization.

Implementation note: in Step 2 we’ll fill this with real conversions and a
local cache file, avoiding live web calls inside the core simulation.
"""
from dataclasses import dataclass
import numpy as np
from ..units import AU, YR

@dataclass
class BodyState:
    name: str
    m: float
    r: np.ndarray  # AU
    v: np.ndarray  # AU/yr


def load_default_body_list():
    """Return canonical body names to include in the simulation.
    Sun, 8 planets, Moon, Pluto, 4 MBAs, 6 KBOs.
    """
    return [
        # Sun & planets
        "Sun", "Mercury", "Venus", "Earth", "Moon", "Mars",
        "Jupiter", "Saturn", "Uranus", "Neptune",
        # Dwarfs / MBAs
        "Pluto", "Ceres", "Vesta", "Pallas", "Hygiea",
        # KBOs
        "Eris", "Haumea", "Makemake", "Quaoar", "Gonggong", "Sedna",
    ]


def get_initial_states(config, rng) -> list[BodyState]:
    # TODO (Step 2): Replace with real Horizons data & conversion
    # For now, stub: Sun + Earth on circular orbit for smoke test.
    bodies = ["Sun", "Earth"] if config.get("smoke_stub") else load_default_body_list()

    states: list[BodyState] = []
    for name in bodies:
        if name == "Sun":
            states.append(BodyState(name, 1.0, np.zeros(3), np.zeros(3)))
        elif name == "Earth":
            r = np.array([1.0, 0.0, 0.0])
            v = np.array([0.0, (2.0*np.pi), 0.0])  # AU/yr
            states.append(BodyState(name, 3.003e-6, r, v))
        else:
            # Placeholder zeros (will be replaced in Step 2)
            states.append(BodyState(name, 0.0, np.zeros(3), np.zeros(3)))
    return states