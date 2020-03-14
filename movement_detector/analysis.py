import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Callable

import pandas as pd
import numpy as np

from movement_detector.detectors import AbstractMovementDetector
from movement_detector.utils import get_video_mapped_path


class AbstractMetaAnalyzer(ABC):
    def __init__(self, detector: AbstractMovementDetector):
        self.detector = detector
        self.analysis_path = self.get_analysis_path(
            vid_path=self.detector.video.vid_path
        )

    @abstractmethod
    def _analyze_meta(self, df: pd.DataFrame):
        pass

    def run(self):
        if not os.path.exists(self.analysis_path):
            analysis = self._analyze_meta(df=self.detector._metadata)
            self._save_analysis(analysis=analysis)

    @staticmethod
    def get_analysis_path(vid_path) -> Path:
        path = get_video_mapped_path(
            vid_path=vid_path,
            dir_suffix='analysis',
            file_extension='.csv',
        )
        return path

    def _save_analysis(self, analysis):
        parent = self.analysis_path.parent
        if not os.path.exists(parent):
            os.makedirs(parent)
        analysis.to_csv(self.analysis_path)


class IntervalAggregatorMA(AbstractMetaAnalyzer):
    def __init__(
            self,
            detector: AbstractMovementDetector,
            intervals: List[float],
            aggregation: Callable = np.mean,
    ):
        super().__init__(detector=detector)
        self.intervals = intervals
        self.aggregation = aggregation

    def _analyze_meta(self, df: pd.DataFrame):
        last_timestamp = self.intervals[-1]
        vid_len = self.detector.video.vid_duration
        if vid_len > last_timestamp:
            self.intervals.append(vid_len)
        df = df.groupby(pd.cut(df['time'], bins=self.intervals))
        df = df.mean()['moving']
        return df
