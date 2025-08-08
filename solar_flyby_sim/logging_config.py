import logging
from logging import StreamHandler


def setup_logging(cfg: dict) -> logging.Logger:
    level = getattr(logging, cfg.get("level", "INFO").upper())
    fmt = cfg.get("format", "[%(asctime)s] %(levelname)s %(name)s: %(message)s")

    logger = logging.getLogger("solar_flyby_sim")
    logger.setLevel(level)
    if not logger.handlers:
        handler = StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    return logger