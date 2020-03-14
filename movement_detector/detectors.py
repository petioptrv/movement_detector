import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Any, Optional, Tuple
import time

import numpy as np
import pandas as pd
import cv2
from scipy import stats

from movement_detector.analysis import AbstractMetaAnalyzer
from movement_detector.utils import get_video_mapped_path
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
    """

    _default_cols = (
        'time',
        'moving',
        'outlier',
        'manual_set',
        'flagged',
    )

    def __init__(
            self,
            video: AbstractVideo,
            meta_analyzer: AbstractMetaAnalyzer
    ):
        """
        Parameters
        ----------
        video : AbstractVideo
            The video object.
        """
        self._video = video
        self._meta_analyzer = meta_analyzer
        self._meta_path = None
        self.meta_fields = self._default_cols
        self.meta_fields += self._additional_columns
        self._meta_built = False

    @property
    def video(self) -> AbstractVideo:
        return self._video

    @video.setter
    def video(self, other):
        raise AttributeError('Cannot set the video attribute.')

    @property
    def meta_analyzer(self) -> AbstractMetaAnalyzer:
        return self._meta_analyzer

    @meta_analyzer.setter
    def meta_analyzer(self, other):
        raise AttributeError('Cannot set the meta_analyzer attribute.')

    @property
    def meta_built(self) -> bool:
        """
        Returns True if the video has been processed and the
        metadata is available.

        Returns
        -------
        bool
            Whether the metadata has been already built.
        """
        return self._meta_built

    @property
    def meta_path(self) -> Path:
        if self._meta_path is None:
            self._meta_path = get_video_mapped_path(
                vid_path=self.video.vid_path,
                dir_suffix='meta',
                file_extension='.csv',
            )
        return self._meta_path

    @property
    def _additional_columns(self) -> Tuple[str]:
        """
        Additional meta-data columns to add to the default set.

        Returns
        -------
        list
            A list of the additional meta-data columns.
        """
        return tuple()

    @abstractmethod
    def _build_meta(self):
        pass

    def run(self):
        """
        Process the video and extract the meta-data.
        See the concrete class' documentation for more details.
        """

        if os.path.exists(self.meta_path):
            self._load_meta()
        else:
            self._create_empty_meta()
            self._build_meta()
            self._save_meta()
        self.meta_analyzer.run(df=self._metadata)

    def meta(
            self,
            start: int,
            stop: Optional[int] = None,
            field: Optional[Union[str, list]] = None
    ) -> Union[pd.DataFrame, pd.Series, Any]:
        """
        Returns a Pandas DataFrame of the required analysis metadata.

        Parameters
        ----------
        start : int
            Start index (inclusive).
        stop : int, optional
            The end index of the query (exclusive).
        field : string or list, optional
            Name of field data.

        Returns
        -------
        pandas DataFrame, pandas Series, or any other
            Can return a Pandas DataFrame, Series, or any other type,
            depending on specified indexing.
        """
        if stop is None:
            stop = start + 1
        if field is None:
            field = self._metadata.columns
        return self._metadata.iloc[start:stop][field]

    def set_freezing(self, index: int):
        """
        Set metadata of specified frame to freezing.
        Frame is marked as user-verified, and flagging is removed.

        Parameters
        ----------
        index : int
            Index of frame which to set as freezing.
        """
        self._metadata.loc[
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
        self._metadata.loc[
            index,
            ['moving', 'manual_set', 'flagged']
        ] = True, True, False

    def _save_meta(self):
        parent = self.meta_path.parent
        if not os.path.exists(parent):
            os.makedirs(parent)
        self._metadata.to_csv(self.meta_path)

    def _load_meta(self):
        self._metadata = pd.read_csv(self.meta_path)

    def _create_empty_meta(self):
        self._metadata = pd.DataFrame(
            columns=self.meta_fields,
            index=range(len(self.video)),
            dtype='float',
        )


class PixelChangeFD(AbstractMovementDetector):
    """ Pixel Change Freezing Detector

    Detects freezing based on pixel changes from frame to frame.

    References
    ----------
    [1] https://github.com/WillBrennan/MotionDetector
    """

    def __init__(
            self,
            video: AbstractVideo,
            meta_analyzer: AbstractMetaAnalyzer,
            # settings
            outlier_change_threshold: float,
            flag_outliers_buffer: int,
            movement_threshold: float,
            freezing_buffer: int,
            blur_ksize: int,
    ):
        super().__init__(video=video, meta_analyzer=meta_analyzer)
        self.outlier_change_threshold = outlier_change_threshold
        self.flag_outliers_buffer = flag_outliers_buffer
        self.movement_threshold = movement_threshold
        self.freezing_buffer = freezing_buffer
        self.blur_ksize = blur_ksize

    def _build_meta(self, _timeit: bool = False):
        prev_frame = None
        t1 = time.time() if _timeit else None
        freezing_frames = 0
        self._metadata.loc[0, 'moving'] = True
        for i, frame in enumerate(self.video):
            frame = self._frame_preprocessing(frame)
            if prev_frame is None:
                contours_area = 0
            else:
                diff = cv2.absdiff(prev_frame, frame)
                diff = self._frame_postprocessing(diff)
                contours = cv2.findContours(diff, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)[0]
                contours_area = self._get_contours_area(contours)
            self._metadata.loc[i, 'contours_area'] = contours_area
            if contours_area < self.movement_threshold:
                if freezing_frames < self.freezing_buffer:
                    self._metadata.loc[i, 'moving'] = True
                    freezing_frames += 1
                elif freezing_frames == self.freezing_buffer:
                    for j in range(self.freezing_buffer):
                        self._metadata.loc[i - j, 'moving'] = False
                    freezing_frames += 1
                else:
                    self._metadata.loc[i, 'moving'] = False
            else:
                freezing_frames = 0
                self._metadata.loc[i, 'moving'] = True
            self._metadata.loc[i, 'manual_set'] = False
            self._metadata.loc[i, 'time'] = self.video.get_frame_time()
            prev_frame = frame
            i += 1
        self._metadata.loc[:, 'moving'] = self._metadata['moving'].astype(bool)
        self._metadata.loc[:, 'manual_set'] = (
            self._metadata['manual_set'].astype(bool)
        )
        self._update_meta()
        if _timeit:
            print('Video {} analyzed in {:.2f}s'.format(self.video.vid_name,
                                                        time.time() - t1))
        self._meta_built = True

    @property
    def _additional_columns(self) -> Tuple[str]:
        return ('contours_area',)

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
        output = cv2.GaussianBlur(
            output,
            (self.blur_ksize, self.blur_ksize),
            0
        )  # blur the image to remove high freq noise
        return output

    def _update_meta(self):
        """
        Updates the meta-data fields according to contours-area calculations.
        Fields modified by the user are left un-flagged.
        The method is synchronised with respect to meta-data access.
        """
        outlier_threshold = self.outlier_change_threshold
        flag_outliers_window = self.flag_outliers_buffer
        contours_zscore = stats.zscore(self._metadata['contours_area'])
        self._metadata.loc[:, 'outlier'] = contours_zscore > outlier_threshold
        virgin_indexes = ~self._metadata['manual_set']
        self._metadata.loc[virgin_indexes, 'flagged'] = (
                np.round(
                    self._metadata['outlier'].rolling(
                        flag_outliers_window,
                        min_periods=0
                    ).mean()
                ) == 1
        )[virgin_indexes]
        flagged_backfill = self._metadata['flagged'].copy()
        for i in range(1, flag_outliers_window + 1):
            flagged_backfill.loc[
                self._metadata['flagged'].shift(-i, fill_value=False)
            ] = True
        self._metadata.loc[:, 'flagged'] = flagged_backfill
