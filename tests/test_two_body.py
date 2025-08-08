import numpy as np
from solar_flyby_sim.sim.integrator import make_sim, add_bodies
from solar_flyby_sim.physics.initial_conditions import BodyState


def test_earth_1yr_period():
    sim = make_sim(dt_yr=1.0/365.25)
    earth = BodyState("Earth", 3.003e-6, np.array([1.0,0,0]), np.array([0,2*np.pi,0]))
    sun = BodyState("Sun", 1.0, np.zeros(3), np.zeros(3))
    add_bodies(sim, [sun, earth])
    t0 = sim.t
    sim.integrate(t0 + 1.0)
    p = sim.particles[1]
    assert abs(p.x-1.0) < 1e-3 and abs(p.y) < 1e-3