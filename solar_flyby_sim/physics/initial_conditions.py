"""J2000 initial conditions loader & converter.

Loads heliocentric osculating elements (J2000 epoch) and converts to
Cartesian state vectors (AU, AU/yr) suitable for REBOUND.

CSV schema (heliocentric, ecliptic of J2000):
    name,a_AU,e,i_deg,Omega_deg,omega_deg,M_deg,m_Msun

Notes
-----
- Sun row is optional; if absent, Sun(m=1) is added at the origin.
- "Moon" is treated as GEOCENTRIC elements and attached to Earth.
- If the CSV is missing, we fall back to a Sun+Earth smoke stub and log instructions.

Usage from driver:
    states = get_initial_states(cfg.get("bodies", {}), rng)
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd

@dataclass
class BodyState:
    name: str
    m: float
    r: np.ndarray  # AU
    v: np.ndarray  # AU/yr

# ------------------------------
# Kepler → Cartesian
# ------------------------------

def kepler_to_cartesian(a, e, i, Omega, omega, M, mu=4*np.pi**2):
    """Convert Keplerian elements (heliocentric) to Cartesian r,v.
    Angles in radians; a in AU; mu in AU^3/yr^2.
    """
    # Solve Kepler's equation M = E - e sin E (Newton iterations)
    E = M if e < 0.8 else np.pi
    for _ in range(50):
        f = E - e*np.sin(E) - M
        fp = 1 - e*np.cos(E)
        dE = -f/fp
        E += dE
        if abs(dE) < 1e-14:
            break
    cosE, sinE = np.cos(E), np.sin(E)
    r_pf = np.array([a*(cosE - e), a*np.sqrt(1-e**2)*sinE, 0.0])
    n = np.sqrt(mu/a**3)
    v_pf = np.array([
        -a*n*sinE/(1 - e*cosE),
        a*n*np.sqrt(1-e**2)*cosE/(1 - e*cosE),
        0.0,
    ])
    cO, sO = np.cos(Omega), np.sin(Omega)
    co, so = np.cos(omega), np.sin(omega)
    ci, si = np.cos(i), np.sin(i)
    R = np.array([
        [ cO*co - sO*so*ci,  -cO*so - sO*co*ci,  sO*si],
        [ sO*co + cO*so*ci,  -sO*so + cO*co*ci, -cO*si],
        [           so*si,             co*si,        ci],
    ])
    r = R @ r_pf
    v = R @ v_pf
    return r, v


def _apply_micro_jitter(r: np.ndarray, v: np.ndarray, rng: np.random.Generator):
    """±2 cm equivalent Cartesian perturbation to randomize mean anomaly."""
    two_cm_AU = 0.02 / 1.495978707e11
    dr = (rng.uniform(-1, 1, 3)) * two_cm_AU
    return r + dr, v

# ------------------------------
# Public API
# ------------------------------

def load_default_body_list() -> list[str]:
    return [
        "Sun", "Mercury", "Venus", "Earth", "Moon", "Mars",
        "Jupiter", "Saturn", "Uranus", "Neptune",
        "Pluto", "Ceres", "Vesta", "Pallas", "Hygiea",
        "Eris", "Haumea", "Makemake", "Quaoar", "Gonggong", "Sedna",
    ]


def _load_elements_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required = ["name","a_AU","e","i_deg","Omega_deg","omega_deg","M_deg","m_Msun"]
    miss = [c for c in required if c not in df.columns]
    if miss:
        raise ValueError(f"Missing columns in {csv_path}: {miss}")
    return df


def _smoke_stub_states() -> list[BodyState]:
    sun = BodyState("Sun", 1.0, np.zeros(3), np.zeros(3))
    r = np.array([1.0, 0.0, 0.0])
    v = np.array([0.0, 2*np.pi, 0.0])
    earth = BodyState("Earth", 3.003e-6, r, v)
    return [sun, earth]


def get_initial_states(cfg_bodies: dict, rng: np.random.Generator) -> list[BodyState]:
    """Load elements → states with optional filtering.

    Config fields (under `bodies`):
      - elements_csv (optional): path to CSV with elements. If omitted, default to
        `solar_flyby_sim/data/j2000_elements.csv`. If missing, use smoke stub.
      - use_default_list (bool): if True (default), filter rows to our canonical list.
    """
    csv_path = cfg_bodies.get("elements_csv")
    csv_path = Path(csv_path) if csv_path else Path("solar_flyby_sim/data/j2000_elements.csv")

    if not csv_path.exists():
        print("[initial_conditions] No elements CSV found at:", csv_path)
        print("  → Using smoke stub (Sun+Earth).")
        print("    Provide columns: name,a_AU,e,i_deg,Omega_deg,omega_deg,M_deg,m_Msun")
        return _smoke_stub_states()

    df = _load_elements_csv(csv_path)

    if cfg_bodies.get("use_default_list", True):
        keep = set(load_default_body_list())
        df = df[df["name"].isin(keep)].copy()

    mu = 4*np.pi**2
    rows: list[BodyState] = []
    earth_state: BodyState | None = None

    # First pass (everything except Moon)
    for _, row in df.iterrows():
        name = str(row["name"]).strip()
        if name == "Moon":
            continue
        a = float(row["a_AU"]); e = float(row["e"])
        inc = np.deg2rad(float(row["i_deg"]))
        Om  = np.deg2rad(float(row["Omega_deg"]))
        om  = np.deg2rad(float(row["omega_deg"]))
        M   = np.deg2rad(float(row["M_deg"]))
        m   = float(row["m_Msun"]) if pd.notna(row["m_Msun"]) else 0.0
        if name == "Sun":
            r = np.zeros(3); v = np.zeros(3)
        else:
            r, v = kepler_to_cartesian(a, e, inc, Om, om, M, mu)
            r, v = _apply_micro_jitter(r, v, rng)
        bs = BodyState(name, m, r, v)
        rows.append(bs)
        if name == "Earth":
            earth_state = bs

    # Second pass (Moon) — attach to Earth if present
    if (df["name"] == "Moon").any():
        if earth_state is None:
            raise ValueError("Moon provided in CSV but Earth is missing.")
        mrow = df[df["name"] == "Moon"].iloc[0]
        a = float(mrow["a_AU"])      # ~0.00257 AU
        e = float(mrow["e"])         # ~0.055
        inc = np.deg2rad(float(mrow["i_deg"]))
        Om  = np.deg2rad(float(mrow["Omega_deg"]))
        om  = np.deg2rad(float(mrow["omega_deg"]))
        M   = np.deg2rad(float(mrow["M_deg"]))
        m   = float(mrow["m_Msun"]) if pd.notna(mrow["m_Msun"]) else 3.694e-8
        mu_rel = 4*np.pi**2 * (3.003e-6 + m)
        r_rel, v_rel = kepler_to_cartesian(a, e, inc, Om, om, M, mu_rel)
        r_rel, v_rel = _apply_micro_jitter(r_rel, v_rel, rng)
        r = earth_state.r + r_rel
        v = earth_state.v + v_rel
        rows.append(BodyState("Moon", m, r, v))

    return rows