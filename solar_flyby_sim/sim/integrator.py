"""REBOUND simulation factory using IAS15 with optional GR/J2 via REBOUNDx."""
from __future__ import annotations
import logging
import rebound
from ..physics.constants import C_AU_PER_YR, J2_SUN_DEFAULT

log = logging.getLogger("solar_flyby_sim.integrator")

def make_sim(dt_yr: float, gr: bool = True, j2_on: bool = True, j2_value: float = J2_SUN_DEFAULT):
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
                    rx.add_force(grmod)
                    grmod.params["c"] = C_AU_PER_YR
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
