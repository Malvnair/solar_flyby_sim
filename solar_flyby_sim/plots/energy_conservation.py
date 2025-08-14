# solar_flyby_sim/plots/energy_conservation.py
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def _load_table(outdir: Path, stem: str) -> pd.DataFrame:
    pqt, csv = outdir / f"{stem}.parquet", outdir / f"{stem}.csv"
    if pqt.exists(): return pd.read_parquet(pqt)
    if csv.exists(): return pd.read_csv(csv)
    raise FileNotFoundError(f"Missing {stem}.parquet/csv in {outdir}")

def _extract_energy(df: pd.DataFrame):
    if {"t","E"}.issubset(df.columns):   return df["t"].to_numpy(), df["E"].to_numpy()
    if {"time","total_energy"}.issubset(df.columns): return df["time"].to_numpy(), df["total_energy"].to_numpy()
    raise ValueError("Energy needs (t,E) or (time,total_energy)")

def _extract_L(df: pd.DataFrame):
    t = df["time"].to_numpy() if "time" in df.columns else df["t"].to_numpy()
    for c in ("Lx","Ly","Lz"):
        if c not in df.columns:
            raise ValueError("AngMom needs Lx,Ly,Lz")
    L = np.sqrt(df["Lx"]**2 + df["Ly"]**2 + df["Lz"]**2).to_numpy()
    return t, L

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()
    outdir: Path 
    outdir.mkdir(parents=True, exist_ok=True)

    energy_df = _load_table(outdir, "energy")
    angmom_df = _load_table(outdir, "angmom")
    tE, E = _extract_energy(energy_df)
    tL, L = _extract_L(angmom_df)

    figs = []

    # Absolute Energy
    f1, a1 = plt.subplots()
    a1.plot(tE, E); a1.set(xlabel="Time [yr]", ylabel="Total Energy", title="Energy (absolute)"); a1.grid(True)
    f1.savefig(outdir / "energy_abs.png", dpi=200, bbox_inches="tight"); figs.append(f1)

    # Fractional Energy
    E0 = E[0]; fracE = (E - E0) / (abs(E0) if E0 != 0 else 1.0)
    f2, a2 = plt.subplots()
    a2.plot(tE, fracE); a2.axhline(0, lw=0.8, color="k")
    a2.set(xlabel="Time [yr]", ylabel="ΔE/|E0|", title="Energy (fractional)"); a2.grid(True)
    f2.savefig(outdir / "energy_frac.png", dpi=200, bbox_inches="tight"); figs.append(f2)

    # Absolute |L|
    f3, a3 = plt.subplots()
    a3.plot(tL, L); a3.set(xlabel="Time [yr]", ylabel="|L|", title="Angular Momentum (absolute)"); a3.grid(True)
    f3.savefig(outdir / "L_abs.png", dpi=200, bbox_inches="tight"); figs.append(f3)

    # Fractional |L|
    L0 = L[0]; fracL = (L - L0) / (abs(L0) if L0 != 0 else 1.0)
    f4, a4 = plt.subplots()
    a4.plot(tL, fracL); a4.axhline(0, lw=0.8, color="k")
    a4.set(xlabel="Time [yr]", ylabel="Δ|L|/|L0|", title="Angular Momentum (fractional)"); a4.grid(True)
    f4.savefig(outdir / "L_frac.png", dpi=200, bbox_inches="tight"); figs.append(f4)

    if args.show:
        plt.show()
    else:
        for f in figs: plt.close(f)

if __name__ == "__main__":
    main()
