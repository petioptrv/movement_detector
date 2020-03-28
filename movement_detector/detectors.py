import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Any, Optional, Tuple
import time

import numpy as np
import pandas as pd
import cv2
from scipy import stats

from movement_detector.utils import get_video_mapped_path
from movement_detector.video import AbstractVideo


class AbstractMovementDetector(ABC):
    """Abstract class for all movement detectors.

    Contains the metadata for all frames in the video.

    Each frame's metadata contains the following fields:

    **time**: The timestamp for the frame in seconds since the start of the
    video.

    **moving**: Set to True if there is movement in the frame.

    **outlier**: Set to True if the frame is detected to be an outlier according
    to the detection method. If the detection method does not hold the concept
    of "outliers", then all fields must be set to False.

    **flagged**: Set to True for flagged outlier frames, and
    changed to False upon manual-set of the `moving` field.

    **manual_set**: Set to True if the `moving` filed has been manually
    overwritten.

    Parameters
    ----------
    video : AbstractVideo
        The video object.
    """

    _default_cols = (
        'time',
        'moving',
        'outlier',
        'flagged',
        'manual_set',
    )

    def __init__(
            self,
            video: AbstractVideo,
    ):
        self._video = video
        self._meta_path = None
        self.meta_fields = self._default_cols
        self.meta_fields += self._additional_columns
        self._meta_built = False

    @property
    def video(self) -> AbstractVideo:
        """The video associated with the detector."""
        return self._video

    @property
    def meta_built(self) -> bool:
        """Set to True if the metadata has been built."""
        return self._meta_built

    @property
    def meta_path(self) -> Path:
        """Path to metadata file."""
        if self._meta_path is None:
            self._meta_path = get_video_mapped_path(
                vid_path=self.video.vid_path,
                dir_suffix='meta',
                file_extension='.csv',
            )
        return self._meta_path

    @property
    def _additional_columns(self) -> Tuple[str]:
        """Additional meta-data columns to add to the default set.

        Must return a tuple of zero or more strings.
        """
        return tuple()

    @abstractmethod
    def _build_meta(self):
        """Overwrite this method to define the metadata generation process."""
        pass

    def run(self):
        """Process the video and extract the meta-data."""
        if os.path.exists(self.meta_path):
            self._load_meta()
        else:
            self._create_empty_meta()
            self._build_meta()
            self.save_meta()
        self._meta_built = True

    def meta(
            self,
            start: int,
            stop: Optional[int] = None,
            field: Optional[Union[str, list]] = None
    ) -> Union[pd.DataFrame, pd.Series, Any]:
        """Returns a Pandas DataFrame of the required analysis metadata.

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
        """Set metadata of specified frame to freezing.

        Frame is marked as user-verified, and flagging is removed.

        Parameters
        ----------
        index : int
            Index of frame which to set as freezing.
        """
        col_names = ['moving', 'manual_set', 'flagged']
        col_vals = [False, True, False]
        self._metadata.loc[index, col_names] = col_vals

    def set_moving(self, index: int):
        """Set metadata of specified frame to moving.

        Frame is marked as user-verified, and flagging is removed.

        Parameters
        ----------
        index : int
            Index of frame which to set as moving.
        """
        col_names = ['moving', 'manual_set', 'flagged']
        col_vals = [True, True, False]
        self._metadata.loc[index, col_names] = col_vals

    def save_meta(self):
        """Save the metadata to file.

        The file path relative to the `meta` folder is the same as the video's
        path relative to the `video` folder.
        """
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

    Detects freezing based on pixel-value change ratio from one frame
    to the next.

    First, a Gaussian blur filter is applied to the images. Next, the pixels
    that have changed between the consecutive frames are detected. Then,
    bounding-boxes are built around those pixels. Finally the ratio of the area
    of the bounding boxes to the total area of the image is analyzed to
    determine if the image should be classified as one containing movement
    or not.

    The exact values for the parameters must be determined on the basis of the
    analyzed videos. The values will be very different depending on factors
    such as the size of the moving object, contrast of the object with its
    background etc.

    Parameters
    ----------
    video : AbstractVideo
        The video to analyze.
    outlier_change_threshold : float
        The number of standard deviations from the mean that the change value
        must be to be considered an outlier.
    flag_outliers_buffer : int
        The number of consecutive frames that must be identified as outliers
        in order to flag all those frames for review.
    movement_threshold : float
        A value between 0 and 1. The ratio of pixel-change areas relative to the
        area of the image above which the frame will be flagged as containing
        movement.
    freezing_buffer : int
        The number of consecutive frames that must be identified as containing
        freezing in order to the `moving` field for all those frames to False.
    blur_ksize : int
        The size of the Gaussian blur filter. For more information refer to:
        https://docs.opencv.org/master/d4/d13/tutorial_py_filtering.html

    References
    ----------
    [1] https://github.com/WillBrennan/MotionDetector
    """

    def __init__(
            self,
            video: AbstractVideo,
            outlier_change_threshold: float,
            flag_outliers_buffer: int,
            movement_threshold: float,
            freezing_buffer: int,
            blur_ksize: int,
    ):
        super().__init__(video=video)
        self.outlier_change_threshold = outlier_change_threshold
        self.flag_outliers_buffer = flag_outliers_buffer
        self.movement_threshold = movement_threshold
        self.freezing_buffer = freezing_buffer
        self.blur_ksize = blur_ksize

    @property
    def _additional_columns(self) -> Tuple[str]:
        return 'change_ratio',

    # todo: improve readability
    def _build_meta(self, _timeit: bool = False):
        prev_frame = None
        t1 = time.time() if _timeit else None
        freezing_frames = 0
        self._metadata.loc[0, 'moving'] = True
        img_area = self.video.frame_shape[0] * self.video.frame_shape[1]
        for i, frame in enumerate(self.video):
            frame = self._frame_preprocessing(frame)
            if prev_frame is None:
                change_ratio = 0
            else:
                diff = cv2.absdiff(prev_frame, frame)
                diff = self._frame_postprocessing(diff)
                contours = cv2.findContours(diff, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)[0]
                contours_area = self._get_contours_area(contours)
                change_ratio = contours_area / img_area
            self._metadata.loc[i, 'change_ratio'] = change_ratio
            if change_ratio < self.movement_threshold:
                if freezing_frames < self.freezing_buffer - 1:
                    self._metadata.loc[i, 'moving'] = True
                    freezing_frames += 1
                elif freezing_frames == self.freezing_buffer - 1:
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
        self._metadata.loc[:, 'moving'] = self._metadata['moving'].astype(bool)
        self._metadata.loc[:, 'manual_set'] = (
            self._metadata['manual_set'].astype(bool)
        )
        self._update_meta()
        if _timeit:
            print('Video {} analyzed in {:.2f}s'.format(self.video.vid_name,
                                                        time.time() - t1))

    @staticmethod
    def _frame_postprocessing(frame: np.ndarray) -> np.ndarray:
        output = cv2.threshold(frame, 15, 255, cv2.THRESH_BINARY)[1]
        output = cv2.dilate(output, None, iterations=2)
        return output

    @staticmethod
    def _get_contours_area(contours: np.ndarray) -> float:
        area = sum([cv2.contourArea(c) for c in contours])
        return area

    def _frame_preprocessing(self, frame: np.ndarray) -> np.ndarray:
        output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to GreyScale
        output = cv2.GaussianBlur(
            output,
            (self.blur_ksize, self.blur_ksize),
            0
        )  # blur the image to remove high freq noise
        return output

    def _update_meta(self):
        outlier_threshold = self.outlier_change_threshold
        flag_outliers_window = self.flag_outliers_buffer
        change_zscore = np.abs(stats.zscore(self._metadata['change_ratio']))
        self._metadata.loc[:, 'outlier'] = change_zscore > outlier_threshold
        virgin_indexes = ~self._metadata['manual_set']
        # ugly, but optimized
        self._metadata.loc[virgin_indexes, 'flagged'] = (
                self._metadata['outlier'].rolling(
                    flag_outliers_window,
                    min_periods=0
                ).sum() == flag_outliers_window
        )[virgin_indexes]
        flagged_backfill = self._metadata['flagged'].copy()
        for i in range(1, flag_outliers_window + 1):
            flagged_backfill.loc[
                self._metadata['flagged'].shift(-i, fill_value=False)
            ] = True
        self._metadata.loc[:, 'flagged'] = flagged_backfill
