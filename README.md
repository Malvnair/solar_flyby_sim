# solar_flyby_sim

Research-grade Solar System integrations with stellar flybys, GR perihelion precession, and publishable diagnostics. Python/REBOUND implementation inspired by Kaib & Raymond (Icarus 2025) setup and classical apsidal-precession analyses.

## Features
- Symplectic core (**WHFast**) with automatic switching to **IAS15** near close encounters
- 1PN GR via REBOUNDx; optional solar J2 and mass-loss toggles
- Realistic stellar flyby generator; injection at 1 pc; b≤0.1 pc; impulse-gradient logging
- J2000 (JD 2451545.0 TDB) initial conditions from JPL Horizons
- Outputs: osculating elements (a,e,i,Ω,ϖ,M), E & L, secular spectra, encounter logs
- Artifacts: Parquet/CSV + quicklook plots + HTML run report

## Install
```bash
conda env create -f env.yml
conda activate solar-flyby
python -c "import rebound, reboundx; print(rebound.__version__, reboundx.__version__)"

python run.py --config solar_flyby_sim/configs/control.yaml
python run.py --config solar_flyby_sim/configs/withstars.yaml
python run.py --config solar_flyby_sim/configs/strongpass.yaml