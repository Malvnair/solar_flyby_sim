from __future__ import annotations
from pathlib import Path
import pandas as pd
import json

class OutputWriter:
    def __init__(self, outdir: Path):
        self.outdir = Path(outdir)
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.snapshots = []
        self.energy = []
        self.angmom = []

    def write_snapshot(self, t, elems_df: pd.DataFrame, energy, angmom):
        # Append to lists; finalize() will write to disk in Parquet/CSV
        elems_df = elems_df.copy()
        elems_df.insert(0, "t", t)
        self.snapshots.append(elems_df)
        self.energy.append({"t": t, "E": float(energy)})
        self.angmom.append({"t": t, "Lx": float(angmom[0]), "Ly": float(angmom[1]), "Lz": float(angmom[2])})

    def finalize(self):
        if self.snapshots:
            all_elems = pd.concat(self.snapshots, ignore_index=True)
            all_elems.to_parquet(self.outdir / "elements.parquet")
        pd.DataFrame(self.energy).to_csv(self.outdir / "energy.csv", index=False)
        pd.DataFrame(self.angmom).to_csv(self.outdir / "angmom.csv", index=False)