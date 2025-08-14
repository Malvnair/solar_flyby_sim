import numpy as np
from solar_flyby_sim.analysis.elements import _rv_to_kepler


def test_elements_circular():
    mu = 4*np.pi**2
    r = np.array([1.0,0,0])
    v = np.array([0,2*np.pi,0])
    elems = _rv_to_kepler(r, v, mu)
    assert abs(elems["a"]-1.0) < 1e-6
    assert elems["e"] < 1e-6

