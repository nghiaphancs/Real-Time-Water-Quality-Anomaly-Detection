from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np
from edge.schemas import Prediction, DetectorSummary


class BaseDetector(ABC):
    @property
    @abstractmethod
    def info(self) -> DetectorSummary:
        pass

    @abstractmethod
    def warmup(self) -> None:
        pass

    @abstractmethod
    def predict(self, window_data: np.ndarray, feature_names: List[str]) -> Prediction:
        pass

    def close(self) -> None:
        pass
