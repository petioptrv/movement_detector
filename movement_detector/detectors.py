from abc import ABC, abstractmethod
from typing import Union, Any, Optional, List
import time

import numpy as np
import pandas as pd
import cv2
from scipy import stats

from movement_detector.video import AbstractVideo


class AbstractMovementDetector(ABC):
    """Abstract class for all movement detectors.

    Contains a `metadata` data frame. Each row holds the the metadata for
    a single video frame.

    Metadata data frames contain the following fields:

    **moving**: Set to True if there is movement in the frame.

    **outlier**: Set to True if the frame is detected to be an outlier according
    to the detection method. If the detection method does not hold the concept
    of "outliers", then all fields must be set to False.

    **manual_set**: Set to True if the `moving` filed has been manually
    overwritten.

    **flagged**: Set to True for frames flagged as outliers by the detector, and
    changed to False if the `moving` filed value is manually overwritten.

    **interval**: Which interval this frame belongs to.
    """

    _default_cols = [
        'moving',
        'outlier',
        'manual_set',
        'flagged',
        'interval'
    ]

    def __init__(
            self,
            video: AbstractVideo,
            # settings
            interval_start_times: List[float],
    ):
        """
        Parameters
        ----------
        video : AbstractVideo
            The video object.
        interval_start_times : list of floats
            Refer to the :func:`AbstractAnalyzerSettings<movement_detector
            .analysis.AbstractAnalyzerSettings._blank_settings>`
            documentation.
        """
        self.video = video
        self.interval_start_times = interval_start_times
        self.metadata = pd.DataFrame(
            columns=self._default_cols + self._additional_columns,
            index=range(len(self.video))
        )
        self.meta_fields = self.metadata.columns
        self._analysis_performed = False

    @property
    def analysis_performed(self) -> bool:
        """
        Returns True if the video analysis is completed and the
        data is available.

        Returns
        -------
        bool
            Whether the analysis has been already performed.
        """
        return self._analysis_performed

    @property
    def _additional_columns(self) -> list:
        """
        Additional meta-data columns to add to the default set.

        Returns
        -------
        list
            A list of the additional meta-data columns.
        """
        return []

    @abstractmethod
    def run(self):
        """
        Process the video and extract the meta-data.
        See the concrete class' documentation for more details.
        """

    def meta(
            self,
            start: int,
            end: Optional[int] = None,
            field: Optional[Union[str, list]] = None
    ) -> Union[pd.DataFrame, pd.Series, Any]:
        """
        Returns a Pandas DataFrame of the required analysis metadata.

        Parameters
        ----------
        start : int
            Start index (inclusive).
        end : int, optional
            The end index of the query (exclusive).
        field : string or list, optional
            Name of field data.

        Returns
        -------
        pandas DataFrame, pandas Series, or any other
            Can return a Pandas DataFrame, Series, or any other type,
            depending on specified indexing.
        """
        if field is None:
            field = self.metadata.columns
        return self.metadata.loc[start:end, field]

    def set_freezing(self, index: int):
        """
        Set metadata of specified frame to freezing.
        Frame is marked as user-verified, and flagging is removed.

        Parameters
        ----------
        index : int
            Index of frame which to set as freezing.
        """
        self.metadata.loc[
            index,
            ['moving', 'manual_set', 'flagged']
        ] = False, True, False

    def set_moving(self, index: int):
        """
        Set metadata of specified frame to moving.
        Frame is marked as user-verified, and flagging is removed.

        Parameters
        ----------
        index : int
            Index of frame which to set as moving.
        """
        self.metadata.loc[
            index,
            ['moving', 'manual_set', 'flagged']
        ] = True, True, False

    def get_movement_percentages(self) -> np.ndarray:
        """
        Calculates the percentage movement for each interval.

        Returns
        -------
        NumPy array
            The percentage movement for each interval.
        """
        self.metadata.loc[0, 'interval'] = 0
        interval = 1
        for start_time in self.interval_start_times:
            if start_time == 0:
                continue
            start_frame = np.round(
                start_time * self.video.frame_rate
            ).astype(int)
            self.metadata.loc[start_frame, 'interval'] = interval
            interval += 1
        self.metadata.loc[:, 'interval'] = self.metadata['interval'].ffill()
        intervals = self.metadata.groupby('interval')
        return intervals['moving'].mean().values
        pass


class PixelChangeDetector(AbstractMovementDetector):
    """Detects movement based on pixel changes from frame to frame.

    References
    ----------
    [1] https://github.com/WillBrennan/MotionDetector
    """
    def __init__(
            self,
            video: AbstractVideo,
            # settings
            interval_start_times: List[float],
            outlier_change_threshold: int,
            flag_outliers_rolling_window: int,
    ):
        AbstractMovementDetector.__init__(self, video, interval_start_times)

    def run(self, _timeit: bool = False):
        """
        Computes the contours-area sizes of each frame in the video.

        Parameters
        ----------
        _timeit : boolean
            If set to True, prints out the time to analyze the video.
        """
        prev_frame = None
        freezing_frames = 0
        i = 0
        t1 = time.time() if _timeit else None
        for frame in self.video:
            frame = self._frame_preprocessing(frame)
            if prev_frame is None:
                contours_area = 0
            else:
                diff = cv2.absdiff(prev_frame, frame)
                diff = self._frame_postprocessing(diff)
                contours = cv2.findContours(diff, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)[1]
                contours_area = self._get_contours_area(contours)
            if contours_area == 0:
                freezing_frames += 1
            else:
                freezing_frames = 0
            self.metadata.loc[i, 'contours_area'] = contours_area
            if freezing_frames == freezing_window:
                for j in range(freezing_window):
                    self.metadata.loc[i - j, 'freezing'] = True
            elif freezing_frames > freezing_window:
                self.metadata.loc[i, 'freezing'] = True
            else:
                self.metadata.loc[i, 'freezing'] = False
            self.metadata.loc[i, 'manual_set'] = False
            prev_frame = frame
            i += 1
        self.metadata.loc[:, 'freezing'] = self.metadata['freezing'].astype(
            bool)
        self.metadata.loc[:, 'manual_set'] = self.metadata[
            'manual_set'].astype(bool)
        self._update_meta()
        if _timeit:
            print('Video {} analyzed in {:.2f}s'.format(self.video.vid_name,
                                                        time.time() - t1))
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
        output = cv2.GaussianBlur(output, (ksize, ksize),
                                  0)  # blur the image to remove high freq noise
        return output

    def _update_meta(self):
        """
        Updates the meta-data fields according to contours-area calculations.
        Fields modified by the user are left un-flagged.
        The method is synchronised with respect to meta-data access.
        """
        outlier_threshold = self._settings.get_value('outlier_change_threshold')
        flag_outliers_window = self._settings.get_value('flag_outliers_window')
        self.metadata.loc[:, 'outlier'] = (
                stats.zscore(
                    self.metadata['contours_area']) > outlier_threshold
        )
        virgin_indexes = ~self.metadata['manual_set']
        self.metadata.loc[virgin_indexes, 'flagged'] = (np.round(
            self.metadata['outlier'].rolling(flag_outliers_window,
                                             min_periods=0).mean()
        ) == 1)[virgin_indexes]
        flagged_backfill = self.metadata['flagged'].copy()
        for i in range(1, flag_outliers_window + 1):
            flagged_backfill.loc[
                self.metadata['flagged'].shift(-i, fill_value=False)] = True
        self.metadata.loc[:, 'flagged'] = flagged_backfill
