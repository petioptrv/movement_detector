import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Callable

import pandas as pd
import numpy as np

from movement_detector.utils import get_video_mapped_path


class AbstractMetaAnalyzer(ABC):
    def __init__(self, vid_path: Path):
        self.analysis_path = self.get_analysis_path(vid_path=vid_path)

    @abstractmethod
    def _analyze_meta(self, df: pd.DataFrame):
        pass

    def run(self, df: pd.DataFrame):
        if not os.path.exists(self.analysis_path):
            self._analyze_meta(df=df)

    @staticmethod
    def get_analysis_path(vid_path) -> Path:
        path = get_video_mapped_path(
            vid_path=vid_path,
            dir_suffix='output',
            file_extension='.csv',
        )
        return path


class IntervalAggregatorMA(AbstractMetaAnalyzer):
    def __init__(
            self,
            vid_path: Path,
            intervals: List[float],
            aggregation: Callable = np.mean,
    ):
        super().__init__(vid_path=vid_path)
        self.intervals = intervals
        self.aggregation = aggregation

    def _analyze_meta(self, df: pd.DataFrame):
        pass
