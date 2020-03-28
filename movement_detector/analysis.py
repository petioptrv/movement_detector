import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Callable

import pandas as pd
import numpy as np

from movement_detector.detectors import AbstractMovementDetector
from movement_detector.utils import get_video_mapped_path


class AbstractMetaAnalyzer(ABC):
    """Metadata analyzer.

    A group of classes that can analyze metadata produced by a detector object.

    Parameters
    ----------
    detector : AbstractMovementDetector
        The detector who's metadata to analyze.
    """

    def __init__(self, detector: AbstractMovementDetector):
        self.detector = detector
        # TODO: this violates the open-closed principle
        self.analysis_path = self.get_analysis_path(
            vid_path=self.detector.video.vid_path
        )

    def run(self):
        """Run the analysis.

        Applies the analysis to the metadata and saves the results
        as a CSV file.

        If the detector hasn't been ran, `self.detector.run()` is called.
        """
        if not os.path.exists(self.analysis_path):
            if not self.detector.meta_built:
                self.detector.run()
            analysis = self._analyze_meta(df=self.detector._metadata)
            self._save_analysis(analysis=analysis)
        else:
            analysis = self._load_analysis()
        return analysis

    @staticmethod
    def get_analysis_path(vid_path: Path) -> Path:
        """Returns the path in which to save the analysis file.

        The analysis is saved in a sub-path relative to the analysis folder
        that mimics the sub-path of the detector's video file relative to the
        videos folder.

        Parameters
        ----------
        vid_path : Path
            The path to the video file.

        Returns
        -------
        path : Path
            The path to the analysis file.
        """
        path = get_video_mapped_path(
            vid_path=vid_path,
            dir_suffix='analysis',
            file_extension='.csv',
        )
        return path

    @abstractmethod
    def _analyze_meta(self, df: pd.DataFrame):
        """Overwrite to implement the meta-analysis.

        Should accept a Pandas dataframe produced by a detector object. Refer
        to the documentation of the detector class for more details on the
        available fields.
        """
        pass

    def _save_analysis(self, analysis):
        parent = self.analysis_path.parent
        if not os.path.exists(parent):
            os.makedirs(parent)
        analysis.to_csv(self.analysis_path)

    def _load_analysis(self):
        analysis = pd.read_csv(self.analysis_path)
        return analysis


class IntervalAggregatorMA(AbstractMetaAnalyzer):
    """Interval metadata aggregator.

    The interval aggregator applies an aggregation function to the count
    of the frames containing movement flagged by the detector over the
    specified intervals of time.

    Passing an `np.mean` aggregation will result in the percentage of movement
    frames detected in each interval.

    Parameters
    ----------
    detector : AbstractMovementDetector
        The detector who's metadata to analyze.
    intervals : list of floats
        A list of the interval cut-off points.
    aggregation : Callable, default np.mean
        The aggregation operation that will be applied on the movement-positive
        frames in the specified intervals.
    include_start : bool, default True
        If set to True and the first cut-off point is not zero, the first
        interval will span from the start of the video to the first cut-off.
    include_end : bool, default True
        If set to True and the last cut-off point is lower than the duration
        of the video, the last interval will span from the cut-off point to
        the end of the video.
    """

    def __init__(
            self,
            detector: AbstractMovementDetector,
            intervals: List[float],
            aggregation: Callable = np.mean,
            include_start: bool = True,
            include_end: bool = True,
    ):
        super().__init__(detector=detector)
        self._intervals = intervals
        self._aggregation = aggregation
        self._include_start = include_start
        self._include_end = include_end

    @property
    def intervals(self) -> List[float]:
        """The list of cut-off points for the intervals."""
        return self._intervals

    @property
    def aggregation(self) -> Callable:
        """The aggregation operation."""
        return self._aggregation

    def _analyze_meta(self, df: pd.DataFrame):
        if self._include_start:
            first_timestamp = self.intervals[0]
            if first_timestamp != 0:
                self.intervals.insert(0, 0)
        if self._include_end:
            last_timestamp = self.intervals[-1]
            vid_len = self.detector.video.vid_duration
            if vid_len > last_timestamp:
                self.intervals.append(vid_len)

        df = df.groupby(pd.cut(df['time'], bins=self.intervals))
        df = df.aggregate(self._aggregation)['moving']
        return df
