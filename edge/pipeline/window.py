from collections import deque
from typing import Dict, List, Any
import numpy as np


class SlidingWindowManager:
    def __init__(self, window_size: int = 30, warmup_samples: int = 5):
        self.window_size = window_size
        self.warmup_samples = warmup_samples
        self._buffers: Dict[str, deque] = {}

    def set_window_size(self, size: int):
        self.window_size = size
        for k in self._buffers:
            self._buffers[k] = deque(self._buffers[k], maxlen=size)

    def append_sample(self, device_id: str, sample: List[float]) -> np.ndarray:
        if device_id not in self._buffers:
            self._buffers[device_id] = deque(maxlen=self.window_size)
        self._buffers[device_id].append(sample)
        return np.array(self._buffers[device_id])

    def get_status(self, device_id: str) -> Dict[str, Any]:
        buf = self._buffers.get(device_id, deque())
        cur_len = len(buf)
        return {
            "current_size": cur_len,
            "max_size": self.window_size,
            "warming_up": cur_len < self.warmup_samples,
        }
