import numpy as np
from solar_flyby_sim.analysis.elements import _rv_to_kepler


def test_elements_circular():
    mu = 4*np.pi**2
    r = np.array([1.0,0,0])
    v = np.array([0,2*np.pi,0])
    a,e,i,Om,varpi,M = _rv_to_kepler(mu, r, v)
    assert abs(a-1.0) < 1e-6
    assert e < 1e-6
