from dataclasses import dataclass
from pathlib import Path
import numpy as np
import random


@dataclass
class Seeds:
    master: int
    run_id: int = 0

    def derive(self, k: int) -> int:
        return int((self.master + k + 1664525) % (2**31 - 1))


def set_all_seeds(seed: int):
    random.seed(seed)
    np.random.seed(seed & 0x7FFFFFFF)