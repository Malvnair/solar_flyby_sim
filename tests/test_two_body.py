import math
import numpy as np
import pytest

try:
    import rebound
except ImportError:  # pragma: no cover
    rebound = None

from solar_flyby_sim.analysis.elements import compute_elements

@pytest.mark.skipif(rebound is None, reason="REBOUND not installed")
def test_kepler_period_earth_like():
    sim = rebound.Simulation()
    sim.G = 4.0 * math.pi**2  # AU^3 / (yr^2 Msun)
    sim.integrator = "ias15"

    # Sun + Earth-like planet
    sim.add(m=1.0)  # Sun
    sim.add(m=3.003e-6, a=1.0, e=0.0167, inc=0.0, Omega=0.0, omega=0.0, f=0.0, primary=sim.particles[0])
    sim.move_to_com()

    elems = compute_elements(sim)
    P = elems[0]["P"]
    assert abs(P - 1.0) < 3e-6, f"Kepler period not ~1 yr; got {P}"

@pytest.mark.skipif(rebound is None, reason="REBOUND not installed")
def test_energy_and_L_conservation_over_10yrs():
    sim = rebound.Simulation()
    sim.G = 4.0 * math.pi**2
    sim.integrator = "ias15"
    sim.add(m=1.0)  # Sun
    sim.add(m=3.003e-6, a=1.0, e=0.0167, inc=0.0, Omega=0.0, omega=0.0, f=0.0, primary=sim.particles[0])
    sim.move_to_com()

    E0 = sim.energy()
    L0 = np.array(sim.angular_momentum())
    L0_norm = np.linalg.norm(L0)

    # Integrate for 10 years with regular output cadence
    t_end = 10.0
    for t in np.linspace(0.0, t_end, 201):
        sim.integrate(t)

    E1 = sim.energy()
    L1 = np.array(sim.angular_momentum())
    L1_norm = np.linalg.norm(L1)

    rel_dE = abs((E1 - E0) / E0)
    rel_dL = abs((L1_norm - L0_norm) / L0_norm)

    assert rel_dE < 1e-11, f"Energy drift too large: {rel_dE}"
    assert rel_dL < 1e-11, f"Angular momentum drift too large: {rel_dL}"

