"""REBOUND simulation factory: WHFast core, optional GR/J2 via REBOUNDx (graceful)."""
from __future__ import annotations
import logging
import numpy as np
import rebound

log = logging.getLogger("solar_flyby_sim.integrator")

def make_sim(dt_yr: float, gr: bool = True, j2_on: bool = True, j2_value: float = 2.2e-7):
    sim = rebound.Simulation()
    sim.units = ("AU", "yr", "Msun")
    sim.integrator = "ias15"
    sim.dt = dt_yr

    # Only bring in REBOUNDx if we actually need it
    sim.contents = {}
    if gr or j2_on:
        try:
            import reboundx
            rx = reboundx.Extras(sim)
            sim.contents["reboundx"] = rx
            if gr:
                try:
                    grmod = rx.load_force("gr")
                    grmod.params["c"] = 63239.7263
                    rx.add_force(grmod)
                except Exception as e:
                    log.warning("GR force not available in this REBOUNDx build; continuing without GR. (%s)", e)
            if j2_on:
                try:
                    obl = rx.load_force("gravitational_harmonics")
                    rx.add_force(obl)
                    sim.contents["obl"] = obl
                except Exception as e:
                    log.warning("Gravitational Harmonics not available; continuing without J2. (%s)", e)
        except Exception as e:
            log.warning("REBOUNDx not available; continuing without GR/J2. (%s)", e)

    # store J2 value for later (if available)
    sim.contents["j2_value"] = j2_value
    return sim


def add_bodies(sim: rebound.Simulation, states: list):
    for i, bs in enumerate(states):
        sim.add(m=bs.m, x=bs.r[0], y=bs.r[1], z=bs.r[2],
                vx=bs.v[0], vy=bs.v[1], vz=bs.v[2])
    sim.move_to_com()

    # If oblateness active and available, set parameters on central body
    rx = sim.contents.get("reboundx")
    obl = sim.contents.get("obl")
    if rx is not None and obl is not None:
        try:
            ps = sim.particles
            primary = ps[0]
            rebx_particle = rx.get_particle(primary)
            rebx_particle.params["J2"] = sim.contents.get("j2_value", 2.2e-7)
            rebx_particle.params["R_eq"] = 0.00465047  # AU (R_sun ≈ 0.00465 AU)
        except Exception as e:
            log.warning("Failed to set J2 params; continuing without J2. (%s)", e)

    return sim
