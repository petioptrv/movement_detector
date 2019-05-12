from abc import ABC, abstractmethod
from typing import Union, Any
from multiprocessing import Lock
import time

import numpy as np
import pandas as pd
import cv2
from scipy import stats
# from skimage.measure import compare_ssim

from src.video.video import AbstractVideo
from src.common.settings import AbstractSettings, PixelChangeSettings, SsimSettings


class AbstractAnalyzer(ABC):
    def __init__(self, video: AbstractVideo, settings: AbstractSettings):
        self._vid = video
        self._settings = settings
        self._meta_data = pd.DataFrame(
            columns=['freezing', 'outlier', 'flagged', 'user_verified', 'interval']+self._additional_columns,
            index=range(len(self._vid))
        )
        self.meta_fields = self._meta_data.columns
        self._meta_data_lock = Lock()
        self._analysis_performed = False

    def meta(
            self, start: int, end: Union[int, str, list] = None, field: Union[str, list] = None
    ) -> Union[pd.DataFrame, pd.Series, Any]:
        """
        Returns a Pandas DataFrame of the required analysis metadata.
        :param start: Start index (inclusive).
        :param end: If end is and integer, it is interpreted as the end index of the query,
        if it is a string or a list, it is interpreted as the column indexer.
        :param field: Name of field data.
        :return: Can return a Pandas DataFrame, Series, or any other type, depending on specified indexing.
        """
        if end is not None:
            if isinstance(end, int):
                if field is not None:
                    return self._meta_data.loc[start:end, field]
                else:
                    return self._meta_data.loc[start:end]
            else:
                return self._meta_data.loc[start, end]
        return self._meta_data.loc[start]

    def set_freezing(self, index: int):
        """
        Set metadata of specified frame to freezing.
        Frame is marked as user-verified, and flagging is removed.
        :param index: Index of frame which to set as freezing.
        :return:
        """
        with self._meta_data_lock:
            self._meta_data.loc[index, ['freezing', 'user_verified', 'flagged']] = (True, True, False)

    def set_moving(self, index: int):
        """
        Set metadata of specified frame to moving.
        Frame is marked as user-verified, and flagging is removed.
        :param index: Index of frame which to set as moving.
        :return:
        """
        with self._meta_data_lock:
            self._meta_data.loc[index, ['freezing', 'user_verified', 'flagged']] = (False, True, False)

    def get_freezing_percentages(self) -> np.ndarray:
        start_times = self._settings.get_value('interval_start_times')
        self._meta_data.loc[0, 'interval'] = 0
        interval = 1
        for start_time in start_times:
            if start_time == 0:
                continue
            start_frame = np.round(start_time * self._vid.frame_rate).astype(int)
            self._meta_data.loc[start_frame, 'interval'] = interval
            interval += 1
        self._meta_data.loc[:, 'interval'] = self._meta_data['interval'].ffill()
        intervals = self._meta_data.groupby('interval')
        return intervals['freezing'].mean().values

    def analysis_performed(self):
        """
        Returns True if the video analysis is completed and the data is available.
        :return:
        """
        return self._analysis_performed

    @abstractmethod
    def process_video(self):
        """
        Process the video and extract the meta-data.
        See the concrete class' documentation for more details.
        :return:
        """
        pass

    @property
    @abstractmethod
    def _additional_columns(self) -> list:
        """
        Additional meta-data columns to add to the default set.
        :return:
        """
        pass


class PixelChangeDetector(AbstractAnalyzer):
    def __init__(self, video: AbstractVideo, settings: PixelChangeSettings = None):
        if settings is None:
            settings = PixelChangeSettings()
        AbstractAnalyzer.__init__(self, video, settings)
        self._settings.register(self._update_meta)

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
        for frame in self._vid:
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
            with self._meta_data_lock:
                self._meta_data.loc[i, 'contours_area'] = contours_area
                if freezing_frames == freezing_window:
                    for j in range(freezing_window):
                        self._meta_data.loc[i-j, 'freezing'] = True
                elif freezing_frames > freezing_window:
                    self._meta_data.loc[i, 'freezing'] = True
                else:
                    self._meta_data.loc[i, 'freezing'] = False
                self._meta_data.loc[i, 'user_verified'] = False
            prev_frame = frame
            i += 1
        with self._meta_data_lock:
            self._meta_data.loc[:, 'freezing'] = self._meta_data['freezing'].astype(bool)
            self._meta_data.loc[:, 'user_verified'] = self._meta_data['user_verified'].astype(bool)
        self._update_meta()
        if timit:
            print('Video {} analyzed in {:.2f}s'.format(self._vid.vid_name, time.time()-t1))
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
        with self._meta_data_lock:
            self._meta_data.loc[:, 'outlier'] = (
                stats.zscore(self._meta_data['contours_area']) > outlier_threshold
            )
            virgin_indexes = ~self._meta_data['user_verified']
            self._meta_data.loc[virgin_indexes, 'flagged'] = (np.round(
                self._meta_data['outlier'].rolling(flag_outliers_window, min_periods=0).mean()
            ) == 1)[virgin_indexes]
            flagged_backfill = self._meta_data['flagged'].copy()
            for i in range(1, flag_outliers_window + 1):
                flagged_backfill.loc[self._meta_data['flagged'].shift(-i, fill_value=False)] = True
            self._meta_data.loc[:, 'flagged'] = flagged_backfill


# class SsimAnalyzer(AbstractAnalyzer):
#     def __init__(self, video: AbstractVideo, settings: SsimSettings = None):
#         if settings is None:
#             settings = SsimSettings()
#         AbstractAnalyzer.__init__(self, video, settings)
#         self._settings.register(self._update_meta)
#
#     def process_video(self, timit=False):
#         """
#         Computes the Structural Similarity Indices (SSIM; https://en.wikipedia.org/wiki/Structural_similarity)
#         between subsequent frames.
#         The method is synchronised with respect to meta-data access.
#         :param timit: If set to True, prints out the time to analyze the video.
#         """
#         freezing_window = self._settings.get_value('freezing_window')
#         freezing_threshold = self._settings.get_value('freezing_threshold')
#         prev_frame = None
#         freezing_frames = 0
#         i = 0
#         t1 = time.time()
#         for frame in self._vid:
#             if prev_frame is None:
#                 ssim = 1
#             else:
#                 ssim = compare_ssim(prev_frame, frame, multichannel=True)
#             if ssim < freezing_threshold:
#                 freezing_frames += 1
#             with self._meta_data_lock:
#                 self._meta_data.loc[i, 'ssim'] = ssim
#                 if freezing_frames == freezing_window:
#                     for j in range(freezing_window):
#                         self._meta_data.loc[i - j, 'freezing'] = True
#                 elif freezing_frames > freezing_window:
#                     self._meta_data.loc[i, 'freezing'] = True
#                 else:
#                     self._meta_data.loc[i, 'freezing'] = False
#                 self._meta_data.loc[i, 'user_verified'] = False
#             prev_frame = frame
#             i += 1
#         with self._meta_data_lock:
#             self._meta_data.loc[:, 'freezing'] = self._meta_data['freezing'].astype(bool)
#             self._meta_data.loc[:, 'user_verified'] = self._meta_data['user_verified'].astype(bool)
#         self._update_meta()
#         if timit:
#             print('Video {} analyzed in {:.2f}s'.format(self._vid.vid_name, time.time()-t1))
#         self._analysis_performed = True
#
#     @property
#     def _additional_columns(self) -> list:
#         return ['ssim']
#
#     def _update_meta(self):
#         """
#         Updates the meta-data fields according to the SSIM thresholds.
#         Fields modified by the user are left un-flagged.
#         The method is synchronised with respect to meta-data access.
#         """
#         outlier_threshold = self._settings.get_value('outlier_change_threshold')
#         flag_outliers_window = self._settings.get_value('flag_outliers_window')
#         with self._meta_data_lock:
#             self._meta_data.loc[:, 'outlier'] = (
#                     stats.zscore(self._meta_data['ssim']) > outlier_threshold
#             )
#             virgin_indexes = ~self._meta_data['user_verified']
#             self._meta_data.loc[virgin_indexes, 'flagged'] = (np.round(
#                 self._meta_data['outlier'].rolling(flag_outliers_window, min_periods=0).mean()
#             ) == 1)[virgin_indexes]
#             flagged_backfill = self._meta_data['flagged'].copy()
#             for i in range(1, flag_outliers_window + 1):
#                 flagged_backfill.loc[self._meta_data['flagged'].shift(-i, fill_value=False)] = True
#             self._meta_data.loc[:, 'flagged'] = flagged_backfill
