from __future__ import annotations
import math
import numpy as np

_EPS = 1e-12
_TWO_PI = 2.0 * math.pi

def _normalize_angle(theta: float) -> float:
    """Wrap angle to [0, 2π)."""
    x = theta % _TWO_PI
    return x if x >= 0.0 else x + _TWO_PI

def _rv_to_kepler(r: np.ndarray, v: np.ndarray, mu: float) -> dict:
    """
    Convert (r, v) to osculating Kepler elements relative to the central body.

    Returns dict with:
      a [AU], e, i [rad], Omega [rad], omega [rad], M [rad], n [rad/yr], P [yr or nan],
      varpi [rad], f [rad]
    """
    r = np.asarray(r, dtype=float)
    v = np.asarray(v, dtype=float)

    r_norm = np.linalg.norm(r)
    v_norm = np.linalg.norm(v)
    if r_norm < _EPS:
        raise ValueError("Position magnitude ~ 0; cannot compute elements.")

    h = np.cross(r, v); h_norm = np.linalg.norm(h)
    k_hat = np.array([0.0, 0.0, 1.0])
    n_vec = np.cross(k_hat, h); n_norm = np.linalg.norm(n_vec)

    e_vec = (np.cross(v, h) / mu) - (r / r_norm)
    e = float(np.linalg.norm(e_vec))

    eps = 0.5 * v_norm**2 - mu / r_norm  # specific orbital energy
    a = -mu / (2.0 * eps) if abs(eps) > _EPS else np.inf

    i = 0.0 if h_norm < _EPS else float(math.acos(np.clip(h[2] / h_norm, -1.0, 1.0)))

    if n_norm < _EPS:
        Omega = 0.0
    else:
        Omega = math.atan2(n_vec[1], n_vec[0])
        Omega = _normalize_angle(Omega)

    if e > _EPS:
        cosf = np.dot(e_vec, r) / (e * r_norm)
        cosf = float(np.clip(cosf, -1.0, 1.0))
        rf_dot = np.dot(r, v)
        sinf = float(np.sign(rf_dot)) * math.sqrt(max(0.0, 1.0 - cosf**2))
        f = _normalize_angle(math.atan2(sinf, cosf))

        if n_norm < _EPS:
            ex, ey = e_vec[0], e_vec[1]
            omega = math.atan2(ey, ex)
        else:
            cosw = np.dot(n_vec, e_vec) / (n_norm * e)
            cosw = float(np.clip(cosw, -1.0, 1.0))
            sinw = np.dot(np.cross(n_vec, e_vec), h) / (n_norm * e * h_norm + _EPS)
            omega = math.atan2(sinw, cosw)
        omega = _normalize_angle(omega)
    else:
        f = 0.0
        omega = 0.0

    if e < 1.0 - 1e-10:
        cosE = (e + math.cos(f)) / (1.0 + e * math.cos(f))
        cosE = float(np.clip(cosE, -1.0, 1.0))
        sinE = math.sqrt(max(0.0, 1.0 - e**2)) * math.sin(f) / (1.0 + e * math.cos(f) + _EPS)
        E = math.atan2(sinE, cosE)
        M = E - e * math.sin(E)
        n = math.sqrt(mu / (a**3))
        P = _TWO_PI / n
    elif e > 1.0 + 1e-10:
        a_abs = abs(a)
        coshH = (r_norm / a_abs + 1.0) / max(e, 1.0 + 1e-12)
        coshH = max(coshH, 1.0)
        H = math.acosh(coshH)
        if np.dot(r, v) < 0.0:
            H = -H
        M = e * math.sinh(H) - H
        n = math.sqrt(mu / (a_abs**3))
        P = float("nan")
    else:
        D = math.tan(0.5 * f)
        M = D + (D**3) / 3.0
        n = float("nan")
        P = float("nan")

    varpi = _normalize_angle(Omega + omega)

    return {
        "a": float(a),
        "e": float(e),
        "i": float(i),
        "Omega": float(Omega),
        "omega": float(omega),
        "M": _normalize_angle(float(M)),
        "n": float(n),
        "P": float(P),
        "varpi": float(varpi),
        "f": float(f),
    }

def compute_elements(sim, central_index: int = 0):
    """
    Compute osculating elements for all bodies relative to the central body.
    Returns a list of dicts (one per non-central body).
    """
    parts = sim.particles
    if central_index < 0 or central_index >= len(parts):
        raise IndexError("central_index out of range.")
    pc = parts[central_index]

    out = []
    for j, p in enumerate(parts):
        if j == central_index:
            continue
        r = np.array([p.x - pc.x, p.y - pc.y, p.z - pc.z], dtype=float)
        v = np.array([p.vx - pc.vx, p.vy - pc.vy, p.vz - pc.vz], dtype=float)
        mu = sim.G * (pc.m + p.m)
        elems = _rv_to_kepler(r, v, mu)
        elems["index"] = j
        out.append(elems)
    return out

