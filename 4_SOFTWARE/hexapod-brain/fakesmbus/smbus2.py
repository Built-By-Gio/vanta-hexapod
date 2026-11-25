"""Fake smbus2 for running `sim.py --robot` without a Pi. Dev only: it lives in its own folder so it can never
shadow the real smbus2 on the robot. Use:  PYTHONPATH=fakesmbus python sim.py --robot --no-camera
Every 300th block write is dumped to fakesmbus/last_<bus>.json."""
import json
import time
from pathlib import Path

HERE = Path(__file__).parent
LOG = {"writes": 0}


class SMBus:
    def __init__(self, n): self.n = n
    def write_byte_data(self, a, r, v): pass
    def close(self): pass

    def write_i2c_block_data(self, a, r, d):
        LOG["writes"] += 1
        if LOG["writes"] % 300 == 0:
            (HERE / f"last_{self.n}.json").write_text(json.dumps({"reg": r, "data": d, "t": time.time(), "n": LOG["writes"]}))
