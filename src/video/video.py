from abc import ABC, abstractmethod

import cv2
import pims
import numpy as np

from src.common.numpy_fns import get_dtype


class AbstractVideo(ABC):
    @property
    @abstractmethod
    def frame_shape(self) -> tuple:
        pass

    @property
    @abstractmethod
    def frame_rate(self) -> float:
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, idx: int) -> np.ndarray:
        pass

    @abstractmethod
    def apply(self, func, *args, **kwargs):
        """
        Invoke function on each frame.
        :param func: Python function to apply.
        :param args: Positional arguments passed to func after the frame.
        :param kwargs: Additional keyword arguments passed to func.
        :return: Returns result of func after last execution.
        """
        pass

    @abstractmethod
    def get_frame(self, i: int) -> np.ndarray:
        """
        Returns the frame at index i.
        :param i: Index of desired frame.
        :return: Numpy array of frame.
        """
        pass

    @abstractmethod
    def mean(self) -> np.ndarray:
        """
        Computes the pixel-wise mean for the frames in the video.
        :return: Numpy array with the pixel-wise mean values.
        """
        pass

    @abstractmethod
    def std(self) -> np.ndarray:
        """
        Computes the pixel-wise standard deviation the video frames.
        :return: Numpy array with the pixel-wise standard deviations values.
        """
        pass

    @abstractmethod
    def sum(self) -> np.ndarray:
        """
        Computes the pixel-wise sum of the frames in the video.
        :return: Numpy array with the pixel-wise sum values.
        """
        pass


class PimsVideo(AbstractVideo):
    # TODO: Make PimsVideo subclass pims.ImageIOReader
    def __init__(self, file_path: str):
        AbstractVideo.__init__(self)
        self._frames = pims.open(file_path)
        self._frame_count = len(self._frames)
        self._sum: np.ndarray = None
        self._mean: np.ndarray = None
        self._std: np.ndarray = None

    def __iter__(self):
        self.__iter__()

    def __len__(self):
        self.__len__()

    def __getitem__(self, idx: int) -> np.ndarray:
        return self.__getitem__(idx)

    @property
    def frame_shape(self) -> tuple:
        return self._frames.frame_shape

    @property
    def frame_rate(self) -> float:
        return self._frames.frame_rate

    def apply(self, func, *args, **kwargs):
        self._frames.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for frame in self[:-1]:
            func(frame, *args, **kwargs)
        return func(self[-1], *args, **kwargs)

    def get_frame(self, i: int) -> np.ndarray:
        return self._frames.get_frame(i)

    def sum(self) -> np.ndarray:
        if self._sum is None:
            max_pixel_value = 255 * self._frame_count
            dtype = get_dtype(max_pixel_value)
            self._sum = np.zeros(self.frame_shape, dtype=dtype)
            for frame in self:
                self._sum += frame
        return self._sum

    def mean(self) -> np.ndarray:
        if self._sum is None:
            self._mean = self.sum() / self._frame_count
        return self._mean

    def std(self) -> np.ndarray:
        if self._std is None:
            mean_dtype = get_dtype(-255)  # to make sure that 0 - 255 can be represented
            mean = self.mean().astype(mean_dtype)
            squares_sum = np.zeros(self.frame_shape, dtype=get_dtype(255 * 255 * self._frame_count))
            self._frames.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for frame in self:
                mean_diff = frame - mean
                squares_sum += mean_diff * mean_diff
            self._std = np.sqrt(squares_sum / self._frame_count)
        return self._std


class CvVideo(AbstractVideo):
    def __init__(self, file_path: str):
        super().__init__()
        self._frames = cv2.VideoCapture(file_path)
        vid_height = int(self._frames.get(cv2.CAP_PROP_FRAME_HEIGHT))
        vid_width = int(self._frames.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._frame_shape = (vid_height, vid_width, 3)
        self._frame_rate = self._frames.get(cv2.CAP_PROP_FPS)
        self._frame_count = len(pims.open(file_path))  # TODO: fix; Note: cv2 gives me len + 1 frames for mp4 -- why?
        self._current_frame = 0
        self._sum: np.ndarray = None
        self._mean: np.ndarray = None
        self._std: np.ndarray = None

    @property
    def frame_shape(self):
        return self._frame_shape

    @property
    def frame_rate(self):
        return self._frame_rate

    def __iter__(self):
        yield self.sum()

    def __len__(self):
        return self._frame_count

    def __getitem__(self, key) -> np.ndarray:
        if type(key) is slice:
            indices = range(*key.indices(self._frame_count))
            frames = np.ndarray((len(indices),) + self.frame_shape, dtype=np.uint8)
            for i in range(len(indices)):
                frames[i] = self.get_frame(indices[i])
            return frames
        elif key >= self._frame_count:
            raise IndexError('Index out of range')
        else:
            return self.get_frame(key)

    def apply(self, func, *args, **kwargs):
        self._frames.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for index in range(self._frame_count - 1):
            _, frame = self._frames.read()
            func(frame, *args, **kwargs)
        _, frame = self._frames.read()
        self._current_frame = self._frame_count
        return func(frame, *args, **kwargs)

    def sum(self) -> np.ndarray:
        if self._sum is None:
            max_pixel_value = 255 * self._frame_count
            dtype = get_dtype(max_pixel_value)
            self._sum = np.zeros(self.frame_shape, dtype=dtype)
            self._frames.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for index in range(self._frame_count):
                _, frame = self._frames.read()
                self._sum += frame
            self._current_frame = self._frame_count
        return self._sum

    def mean(self) -> np.ndarray:
        if self._mean is None:
            self._mean = self.sum() / self._frame_count
            self._current_frame = self._frame_count
        return self._mean

    def std(self) -> np.ndarray:
        if self._std is None:
            mean_dtype = get_dtype(-255)  # to make sure that 0 - 255 can be represented
            mean = self.mean().astype(mean_dtype)
            squares_sum = np.zeros(self.frame_shape, dtype=get_dtype(255 * 255 * self._frame_count))
            self._frames.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for index in range(self._frame_count):
                _, frame = self._frames.read()
                mean_diff = frame - mean
                squares_sum += mean_diff * mean_diff
            self._std = np.sqrt(squares_sum / self._frame_count)
            self._current_frame = self._frame_count
        return self._std

    def get_frame(self, i: int) -> np.ndarray:
        if self._current_frame != i:
            self._frames.set(cv2.CAP_PROP_POS_FRAMES, i)
        _, frame = self._frames.read()
        self._current_frame = i + 1
        return frame
