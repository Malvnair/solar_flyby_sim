"""Draw stellar flybys following Kaib & Raymond (Icarus 2025)-style pipeline.

Step 4 will implement:
- sub-populations (densities, dispersions, peculiar solar velocity)
- Rickman speed sampling; 1 pc injection; impact b≤0.1 pc
- return list of passages with (t, M*, v_inf, b, direction) + impulse gradient
"""
from dataclasses import dataclass
import numpy as np

@dataclass
class Flyby:
    t: float      # years
    m: float      # Msun
    v_inf: float  # AU/yr
    b_pc: float   # pc
    nhat: np.ndarray  # direction vector
    impulse_grad: float


def draw_flybys(config, duration_yr: float, rng: np.random.Generator) -> list[Flyby]:
    if not config.get("enabled", False):
        return []
    # TODO (Step 4): implement real sampling; for now return empty
    return []