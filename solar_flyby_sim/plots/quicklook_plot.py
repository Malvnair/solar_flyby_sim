import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUTDIR = Path("outputs/smoke")
EL_PQT = OUTDIR / "elements.parquet"
EL_CSV = OUTDIR / "elements.csv"

def load_elements():
    if EL_PQT.exists(): df = pd.read_parquet(EL_PQT)
    elif EL_CSV.exists(): df = pd.read_csv(EL_CSV)
    else: raise FileNotFoundError(f"No elements.[parquet/csv] in {OUTDIR}")

    # unify time column
    if "time" not in df.columns and "t" in df.columns:
        df = df.rename(columns={"t": "time"})

    # find a name/id column or create one
    name_col = next((c for c in ("name","label","body","id","idx","particle") if c in df.columns), None)
    if name_col is None:
        # make a stable synthetic id based on row order within each time
        df = df.sort_values(["time"]).copy()
        df["body_idx"] = df.groupby("time").cumcount()
        name_col = "body_idx"

    return df, name_col

def plot_elem(df, name_col, col, ylabel, fname, a_cap=None):
    plt.figure(figsize=(9,4))
    for key, grp in df.groupby(name_col):
        plt.plot(grp["time"], grp[col], lw=1, alpha=0.9, label=str(key))
    plt.xlabel("Time [yr]"); plt.ylabel(ylabel); plt.title(f"{col}")
    plt.grid(True)
    if df[name_col].nunique() <= 12: plt.legend(ncol=2, fontsize=8)
    if a_cap is not None and col == "a":
        plt.ylim(0, a_cap)
    plt.tight_layout()
    plt.savefig(OUTDIR / fname, dpi=200, bbox_inches="tight")

def main():
    df, name_col = load_elements()
    keep = ["time"] + [c for c in ("a","e","i") if c in df.columns]
    df = df[[name_col, *keep]].copy()

    # If there is a super-distant body, keep a separate view for inner system
    a_cap = None
    if "a" in df.columns and df["a"].max() > 50:
        a_cap = 50  # AU

    if "a" in df.columns: plot_elem(df, name_col, "a", "a [AU]", "quick_a.png", a_cap=a_cap)
    if "e" in df.columns: plot_elem(df, name_col, "e", "e", "quick_e.png")
    if "i" in df.columns: plot_elem(df, name_col, "i", "i [rad or deg]", "quick_i.png")

    plt.show()

if __name__ == "__main__":
    print(f"RUNNING: {__file__}")
    main()
    print(f"Saved quick plots in {OUTDIR}")
