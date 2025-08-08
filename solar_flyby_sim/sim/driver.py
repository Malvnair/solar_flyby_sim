from __future__ import annotations
import logging
from pathlib import Path
import numpy as np

from .integrator import make_sim, add_bodies
from ..physics.initial_conditions import get_initial_states
from ..physics.stellar_passages import draw_flybys
from ..analysis.elements import compute_elements
from ..analysis.diagnostics import Diagnostics
from ..io.storage import OutputWriter
from ..utils import set_all_seeds

log = logging.getLogger("solar_flyby_sim.driver")


def run_simulation(cfg: dict):
    run = cfg["run"]; phys = cfg["physics"]; fb = cfg["flybys"]; io = cfg["io"]
    set_all_seeds(int(run.get("seed_master", 20250808)))

    # --- Build simulation (integrator, GR, J2 flags) ---
    sim = make_sim(
        dt_yr=run["dt_yr"],
        gr=phys.get("gr", True),
        j2_on=phys.get("solar_j2", True),
        j2_value=phys.get("j2_value", 2.2e-7),
    )
    # Pass J2 value to integrator/add_bodies via sim.contents
    sim.contents["j2_value"] = phys.get("j2_value", 2.2e-7)

    # --- Initial states ---
    rng = np.random.default_rng(run.get("seed_master", 20250808))
    states = get_initial_states({"smoke_stub": run.get("smoke_stub", False)}, rng)
    add_bodies(sim, states)

    # --- Outputs ---
    outdir = Path(io.get("outdir", "outputs/run"))
    outdir.mkdir(parents=True, exist_ok=True)
    writer = OutputWriter(outdir)

    duration = float(run["duration_yr"])
    dt = float(run["dt_yr"])
    steps = int(duration / dt)
    every = int(run.get("output_every_steps", 100))

    diag = Diagnostics(sim)

    # --- Flybys (placeholder until Step 4) ---
    flyby_list = draw_flybys(fb, duration, rng)  # currently returns []
    _next_flyby_idx = 0

    log.info("Starting integration: duration=%.3e yr, steps=%d", duration, steps)
    t0 = sim.t
    for i in range(steps + 1):
        sim.integrate(t0 + i * dt)

        if i % every == 0:
            elems = compute_elements(sim)
            energy, angmom = diag.energy(), diag.angular_momentum()
            writer.write_snapshot(sim.t, elems, energy, angmom)

    writer.finalize()
    log.info("Run complete. Output in %s", outdir)