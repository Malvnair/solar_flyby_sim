import numpy as np
import pandas as pd


def _rv_to_kepler(mu, r, v):
    # Minimal osculating elements conversion; refined later
    rnorm = np.linalg.norm(r)
    vnorm = np.linalg.norm(v)
    h = np.cross(r, v)
    hnorm = np.linalg.norm(h)
    evec = ((vnorm**2 - mu/rnorm)*r - np.dot(r, v)*v)/mu
    e = np.linalg.norm(evec)
    a = 1.0 / (2.0/rnorm - vnorm**2/mu)
    inc = np.arccos(h[2]/hnorm)
    n = np.cross([0,0,1], h)
    nnorm = np.linalg.norm(n)
    Omega = 0.0 if nnorm == 0 else np.arctan2(n[1], n[0])
    omega = 0.0 if e < 1e-12 else (np.arccos(np.dot(n, evec)/(nnorm*e)) if nnorm>0 else 0.0)
    if evec[2] < 0: omega = 2*np.pi - omega
    # Mean anomaly requires E (elliptic). We'll approximate via true anomaly f.
    rdotv = np.dot(r, v)
    cosf = np.dot(evec, r)/(e*rnorm) if e>1e-12 else 1.0
    cosf = np.clip(cosf, -1.0, 1.0)
    f = np.arccos(cosf)
    if rdotv < 0: f = 2*np.pi - f
    # Eccentric anomaly
    E = 2*np.arctan(np.tan(f/2.0)*np.sqrt((1-e)/(1+e))) if e>1e-12 else f
    M = (E - e*np.sin(E)) % (2*np.pi)
    varpi = (Omega + omega) % (2*np.pi)
    return a, e, inc, Omega, varpi, M


def compute_elements(sim) -> pd.DataFrame:
    ps = sim.particles
    mu0 = 4*np.pi**2  # GM_sun in code units
    rows = []
    for i, p in enumerate(ps):
        if i == 0:
            rows.append({"name": "Sun", "a": np.nan, "e": np.nan, "i": 0.0, "Omega": np.nan, "varpi": np.nan, "M": np.nan})
            continue
        r = np.array([p.x, p.y, p.z]) - np.array([ps[0].x, ps[0].y, ps[0].z])
        v = np.array([p.vx, p.vy, p.vz]) - np.array([ps[0].vx, ps[0].vy, ps[0].vz])
        a,e,inc,Omega,varpi,M = _rv_to_kepler(mu0, r, v)
        rows.append({"name": p.hash or f"b{i}", "a": a, "e": e, "i": inc, "Omega": Omega, "varpi": varpi, "M": M})
    return pd.DataFrame(rows)