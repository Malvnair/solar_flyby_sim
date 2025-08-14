import argparse
import yaml
import sys
from pathlib import Path
from solar_flyby_sim.logging_config import setup_logging
from solar_flyby_sim.sim.driver import run_simulation


def main():
    parser = argparse.ArgumentParser(description="solar_flyby_sim runner")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"Config not found: {cfg_path}")
        sys.exit(1)

    with open(cfg_path, "r") as f:
        config = yaml.safe_load(f)

    log = setup_logging(config.get("logging", {}))
    log.info("Loaded config: %s", cfg_path)

    run_simulation(config)


if __name__ == "__main__":
    main()