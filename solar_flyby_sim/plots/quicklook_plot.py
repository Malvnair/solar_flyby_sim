# solar_flyby_sim/plots/quicklook_plot.py
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUTDIR = Path("outputs/smoke")
ELFILE_PQT = OUTDIR / "elements.parquet"
ELFILE_CSV = OUTDIR / "elements.csv"

def load_elements():
    if ELFILE_PQT.exists():
        df = pd.read_parquet(ELFILE_PQT)
    elif ELFILE_CSV.exists():
        df = pd.read_csv(ELFILE_CSV)
    else:
        raise FileNotFoundError(f"No elements.[parquet/csv] in {OUTDIR}")

    # figure out a name column if present
    name_col = None
    for cand in ("name", "label", "body", "id"):
        if cand in df.columns:
            name_col = cand
            break

    # drop the Sun if we can identify it
    if name_col is not None:
        df = df[df[name_col].astype(str).str.lower() != "sun"]

    # standardize time column
    if "t" in df.columns and "time" not in df.columns:
        df = df.rename(columns={"t": "time"})

    # keep only the columns we need if present
    keep = [c for c in ("time","a","e","i","omega","Omega") if c in df.columns]
    if name_col: keep = [name_col] + keep
    return df[keep].copy(), name_col

def main():
    df, name_col = load_elements()
    if "time" not in df.columns or not any(c in df.columns for c in ("a","e","i")):
        raise ValueError("elements table missing expected columns (need time and a/e/i).")

    plt.figure(figsize=(8,4))
    if "a" in df.columns:
        for key, grp in (df.groupby(name_col) if name_col else [("all", df)]):
            plt.plot(grp["time"], grp["a"], label=str(key))
        plt.title("Semi-major axis a [AU]")
        plt.xlabel("Time [yr]"); plt.ylabel("a [AU]"); plt.grid(True)
        if name_col: plt.legend(ncol=2, fontsize=8)
        plt.tight_layout()
        plt.savefig(OUTDIR / "quick_a.png", dpi=200, bbox_inches="tight")

    plt.figure(figsize=(8,4))
    if "e" in df.columns:
        for key, grp in (df.groupby(name_col) if name_col else [("all", df)]):
            plt.plot(grp["time"], grp["e"], label=str(key))
        plt.title("Eccentricity e")
        plt.xlabel("Time [yr]"); plt.ylabel("e"); plt.grid(True)
        if name_col: plt.legend(ncol=2, fontsize=8)
        plt.tight_layout()
        plt.savefig(OUTDIR / "quick_e.png", dpi=200, bbox_inches="tight")

    plt.show()

if __name__ == "__main__":
    print(f"RUNNING: {__file__}")
    main()
    print(f"Saved: {OUTDIR}/quick_[a|e].png")
