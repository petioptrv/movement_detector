from abc import ABC, abstractmethod
from typing import Union, Any, Optional, List
import time

import numpy as np
import pandas as pd
import cv2
from scipy import stats

from movement_detector.video import AbstractVideo


class AbstractAnalyzer(ABC):
    """
    Abstract class for all video analyzers.
    Contains a `meta_data` data frame, each of row of which holds the metadata
    for a single video frame.
    """

    _default_cols = [
        'moving', 'outlier', 'flagged', 'manual_set', 'interval'
    ]

    def __init__(
            self,
            video: AbstractVideo,
            # settings
            interval_start_times: List[float],
    ):
        """
        :param video: The video object.
        :param interval_start_times: Refer to the
               :func:`AbstractAnalyzerSettings<movement_detector.analysis.AbstractAnalyzerSettings._blank_settings>`
               documentation.
        """
        self.vid = video
        self.interval_start_times = interval_start_times
        self.meta_data = pd.DataFrame(
            columns=self._default_cols + self._additional_columns,
            index=range(len(self.vid))
        )
        self.meta_fields = self.meta_data.columns
        self._analysis_performed = False

    @property
    def analysis_performed(self) -> bool:
        """
        Returns True if the video analysis is completed and the
        data is available.
        :return:
        """
        return self._analysis_performed

    @property
    def _additional_columns(self) -> list:
        """
        Additional meta-data columns to add to the default set.
        :return:
        """
        return []

    def meta(
            self,
            start: int,
            end: Optional[int] = None,
            field: Optional[str, list] = None
    ) -> Union[pd.DataFrame, pd.Series, Any]:
        """
        Returns a Pandas DataFrame of the required analysis metadata.
        :param start: Start index (inclusive).
        :param end: The end index of the query.
        :param field: Name of field data.
        :return: Can return a Pandas DataFrame, Series, or any other type,
                 depending on specified indexing.
        """
        if field is None:
            field = self.meta_data.columns
        return self.meta_data.loc[start:end, field]

    def set_freezing(self, index: int):
        """
        Set metadata of specified frame to freezing.
        Frame is marked as user-verified, and flagging is removed.
        :param index: Index of frame which to set as freezing.
        :return:
        """
        self.meta_data.loc[
            index,
            ['moving', 'manual_set', 'flagged']
        ] = False, True, False

    def set_moving(self, index: int):
        """
        Set metadata of specified frame to moving.
        Frame is marked as user-verified, and flagging is removed.
        :param index: Index of frame which to set as moving.
        :return:
        """
        self.meta_data.loc[
            index,
            ['moving', 'manual_set', 'flagged']
        ] = True, True, False

    def get_movement_percentages(self) -> np.ndarray:
        self.meta_data.loc[0, 'interval'] = 0
        interval = 1
        for start_time in self.interval_start_times:
            if start_time == 0:
                continue
            start_frame = np.round(
                start_time * self.vid.frame_rate
            ).astype(int)
            self.meta_data.loc[start_frame, 'interval'] = interval
            interval += 1
        self.meta_data.loc[:, 'interval'] = self.meta_data['interval'].ffill()
        intervals = self.meta_data.groupby('interval')
        return intervals['moving'].mean().values

    @abstractmethod
    def process_video(self):
        """
        Process the video and extract the meta-data.
        See the concrete class' documentation for more details.
        :return:
        """
        pass


class PixelChangeDetector(AbstractAnalyzer):
    def __init__(
            self,
            video: AbstractVideo,
            # settings
            interval_start_times: List[float],
            outlier_change_threshold: int,
            flag_outliers_window: int,

    ):
        AbstractAnalyzer.__init__(self, video, interval_start_times)

    def process_video(self, timit=False):
        """
        Computes the contours-area sizes of each frame in the video.
        The method is synchronised with respect to meta-data access.
        :param timit: If set to True, prints out the time to analyze the video.
        """
        freezing_window = self._settings.get_value('freezing_window')
        prev_frame = None
        freezing_frames = 0
        i = 0
        t1 = time.time()
        for frame in self.vid:
            frame = self._frame_preprocessing(frame)
            if prev_frame is None:
                contours_area = 0
            else:
                diff = cv2.absdiff(prev_frame, frame)
                diff = self._frame_postprocessing(diff)
                contours = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
                contours_area = self._get_contours_area(contours)
            if contours_area == 0:
                freezing_frames += 1
            else:
                freezing_frames = 0
            self.meta_data.loc[i, 'contours_area'] = contours_area
            if freezing_frames == freezing_window:
                for j in range(freezing_window):
                    self.meta_data.loc[i - j, 'freezing'] = True
            elif freezing_frames > freezing_window:
                self.meta_data.loc[i, 'freezing'] = True
            else:
                self.meta_data.loc[i, 'freezing'] = False
            self.meta_data.loc[i, 'manual_set'] = False
            prev_frame = frame
            i += 1
        self.meta_data.loc[:, 'freezing'] = self.meta_data['freezing'].astype(bool)
        self.meta_data.loc[:, 'manual_set'] = self.meta_data['manual_set'].astype(bool)
        self._update_meta()
        if timit:
            print('Video {} analyzed in {:.2f}s'.format(self.vid.vid_name, time.time() - t1))
        self._analysis_performed = True

    @property
    def _additional_columns(self) -> list:
        return ['contours_area']

    @staticmethod
    def _frame_postprocessing(frame: np.ndarray) -> np.ndarray:
        """
        Applies postprocessing to frame. Applies a threshold and then dilates the result.
        :param frame: The frame to process.
        :return: The processed frame.
        """
        output = cv2.threshold(frame, 15, 255, cv2.THRESH_BINARY)[1]
        output = cv2.dilate(output, None, iterations=2)
        return output

    @staticmethod
    def _get_contours_area(contours: np.ndarray) -> float:
        """
        Calculates the total contours area.
        :param contours: Numpy arrays containing the contours.
        :return: The total combined area of the contours.
        """
        area = 0
        for contour in contours:
            area += cv2.contourArea(contour)
        return area

    def _frame_preprocessing(self, frame: np.ndarray) -> np.ndarray:
        """
        Applies preprocessing to a frame. Converts to greyscale and applies a blur.
        :param frame: The frame to process.
        :return: The processed frame.
        """
        output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to GreyScale
        ksize = self._settings.get_value('blur_ksize')
        output = cv2.GaussianBlur(output, (ksize, ksize), 0)  # blur the image to remove high freq noise
        return output

    def _update_meta(self):
        """
        Updates the meta-data fields according to contours-area calculations.
        Fields modified by the user are left un-flagged.
        The method is synchronised with respect to meta-data access.
        """
        outlier_threshold = self._settings.get_value('outlier_change_threshold')
        flag_outliers_window = self._settings.get_value('flag_outliers_window')
        self.meta_data.loc[:, 'outlier'] = (
                stats.zscore(self.meta_data['contours_area']) > outlier_threshold
        )
        virgin_indexes = ~self.meta_data['manual_set']
        self.meta_data.loc[virgin_indexes, 'flagged'] = (np.round(
            self.meta_data['outlier'].rolling(flag_outliers_window, min_periods=0).mean()
        ) == 1)[virgin_indexes]
        flagged_backfill = self.meta_data['flagged'].copy()
        for i in range(1, flag_outliers_window + 1):
            flagged_backfill.loc[self.meta_data['flagged'].shift(-i, fill_value=False)] = True
        self.meta_data.loc[:, 'flagged'] = flagged_backfill
