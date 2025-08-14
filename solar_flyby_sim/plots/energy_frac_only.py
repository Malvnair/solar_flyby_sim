from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === CONFIG ===
# Change this if you want a different run folder
DEFAULT_OUTDIR = Path("outputs/smoke")

def _load_table(outdir: Path, stem: str) -> pd.DataFrame:
    pqt, csv = outdir / f"{stem}.parquet", outdir / f"{stem}.csv"
    if pqt.exists():
        return pd.read_parquet(pqt)
    if csv.exists():
        return pd.read_csv(csv)
    raise FileNotFoundError(f"Missing {stem}.parquet/csv in {outdir}")

def _extract_energy(df: pd.DataFrame):
    if {"t","E"}.issubset(df.columns):
        return df["t"].to_numpy(), df["E"].to_numpy()
    if {"time","total_energy"}.issubset(df.columns):
        return df["time"].to_numpy(), df["total_energy"].to_numpy()
    raise ValueError("Energy needs (t,E) or (time,total_energy)")

def _extract_L(df: pd.DataFrame):
    t = df["time"].to_numpy() if "time" in df.columns else df["t"].to_numpy()
    for c in ("Lx","Ly","Lz"):
        if c not in df.columns:
            raise ValueError("AngMom needs Lx,Ly,Lz")
    L = np.sqrt(df["Lx"]**2 + df["Ly"]**2 + df["Lz"]**2).to_numpy()
    return t, L

def main():
    outdir = DEFAULT_OUTDIR
    if not outdir.exists():
        raise FileNotFoundError(f"Default output folder {outdir} does not exist. Change DEFAULT_OUTDIR in the script.")

    # Load data
    energy_df = _load_table(outdir, "energy")
    angmom_df = _load_table(outdir, "angmom")
    tE, E = _extract_energy(energy_df)
    tL, L = _extract_L(angmom_df)

    # Fractional Energy
    E0 = E[0]
    fracE = (E - E0) / (abs(E0) if E0 != 0 else 1.0)
    plt.figure()
    plt.plot(tE, fracE)
    plt.axhline(0, lw=0.8, color="k")
    plt.xlabel("Time [yr]")
    plt.ylabel("ΔE / |E₀|")
    plt.title("Fractional Energy Conservation")
    plt.grid(True)

    # Fractional Angular Momentum
    L0 = L[0]
    fracL = (L - L0) / (abs(L0) if L0 != 0 else 1.0)
    plt.figure()
    plt.plot(tL, fracL)
    plt.axhline(0, lw=0.8, color="k")
    plt.xlabel("Time [yr]")
    plt.ylabel("Δ|L| / |L₀|")
    plt.title("Fractional Angular Momentum Conservation")
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    main()
