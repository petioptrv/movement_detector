from abc import ABC, abstractmethod
import os
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from movement_detector.np_utils import get_dtype


class AbstractVideo(ABC):
    """Interface definition for the video classes.

    This class defines the public methods that a video class must expose to
    be compatible with the movement detectors.

    Parameters
    ----------
    file_path : Path
        The path to the video file.
    """

    def __init__(self, file_path: Path):
        self.vid_path = os.path.realpath(file_path)
        self.vid_name = os.path.basename(self.vid_path)

    @property
    @abstractmethod
    def vid_duration(self) -> float:
        """The duration of the video in seconds.

        Returns
        -------
        float
        """
        pass

    @property
    @abstractmethod
    def frame_shape(self) -> tuple:
        """The shape of a single frame.

        Returns
        -------
        tuple
        """
        pass

    @property
    @abstractmethod
    def frame_rate(self) -> float:
        """The video's frame rate.

        Returns
        -------
        float
        """
        pass

    @abstractmethod
    def __iter__(self) -> iter:
        pass

    @abstractmethod
    def __next__(self) -> np.ndarray:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __getitem__(self, item) -> np.ndarray:
        pass

    @abstractmethod
    def get_frame(self, i: int) -> np.ndarray:
        """Returns the frame at index i.

        Parameters
        ----------
        i : int
            Index of desired frame.

        Returns
        -------
        NumPy array
            The frame as a NumPy array.
        """
        pass

    @abstractmethod
    def get_frame_time(self, i: Optional[int] = None) -> float:
        """Returns the video-time for the frame i in seconds.

        Parameters
        ----------
        i : int
            Index of desired frame time.

        Returns
        -------
        float
            The time in seconds since start of video.
        """
        pass

    @abstractmethod
    def mean(self) -> np.ndarray:
        """Computes the pixel-wise mean for the frames in the video.

        Returns
        -------
        NumPy array
            Numpy array with the pixel-wise mean values.
        """
        pass

    @abstractmethod
    def std(self) -> np.ndarray:
        """Computes the pixel-wise standard deviation of the video frames.

        Returns
        -------
        NumPy
            Numpy array with the pixel-wise standard deviation values.
        """
        pass

    @abstractmethod
    def sum(self) -> np.ndarray:
        """Computes the pixel-wise sum of the frames in the video.

        Returns
        -------
        NumPy array
            Numpy array with the pixel-wise sum values.
        """
        pass


class CvVideo(AbstractVideo):
    """OpenCV implementation of the video class interface.

    OpenCV provides the most optimized algorithms for video processing.
    For efficiency, the implementation resorts to lazy evaluation and caching
    of the compute-intensive operations.
    """
    _precision_dtype = np.dtype('float32')

    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self._frames = cv2.VideoCapture(self.vid_path)
        self._frame_count = int(self._frames.get(cv2.CAP_PROP_FRAME_COUNT))
        if self._frame_count <= 0:
            raise ValueError(
                f'The video appears to be empty. Path: {self.vid_path}.'
            )
        vid_height = int(self._frames.get(cv2.CAP_PROP_FRAME_HEIGHT))
        vid_width = int(self._frames.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._frame_shape = (vid_height, vid_width, 3)
        self._frame_rate = self._frames.get(cv2.CAP_PROP_FPS)
        self._vid_duration = self._frame_count / self._frame_rate
        self._current_frame = 0
        self._sum: np.ndarray = None
        self._mean: np.ndarray = None
        self._std: np.ndarray = None
        # fix the problem where open CV returns one more than
        # the actual video length
        while self.get_frame(self._frame_count-1) is None:
            self._frame_count -= 1
        self.size = int(np.prod(self._frame_shape + (self._frame_count, 8)))

    @property
    def vid_duration(self) -> float:
        return self._vid_duration

    @property
    def frame_shape(self) -> tuple:
        return self._frame_shape

    @property
    def frame_rate(self) -> float:
        return self._frame_rate

    def __iter__(self) -> iter:
        self._frames.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return self

    def __next__(self) -> np.ndarray:
        ret, frame = self._frames.read()
        if ret:
            return frame
        else:
            self._current_frame = self._frame_count
            raise StopIteration

    def __len__(self) -> int:
        return self._frame_count

    def __getitem__(self, item) -> np.ndarray:
        if type(item) is slice:
            indices = range(*item.indices(self._frame_count))
            frames = np.empty(
                shape=(len(indices),) + self.frame_shape,
                dtype=np.uint8
            )
            # if the indices are sequential, use optimized retrieval
            if item.step in [None, 1]:
                self._frames.set(cv2.CAP_PROP_POS_FRAMES, indices[0])
                frames = np.array([self._frames.read()[1] for _ in indices])
                self._current_frame = indices[-1]
            else:
                for i in range(len(indices)):
                    frames[i] = self.get_frame(indices[i])
            return frames
        elif item >= self._frame_count:
            raise IndexError('Index out of range')
        else:
            return self.get_frame(item)

    def sum(self) -> np.ndarray:
        if self._sum is None:
            max_pixel_value = 255 * self._frame_count
            dtype = get_dtype(max_pixel_value)
            self._sum = np.zeros(self.frame_shape, dtype=dtype)
            self._frames.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for index in range(self._frame_count):
                self._sum += self._frames.read()[1]
            self._current_frame = self._frame_count
        return self._sum

    def mean(self) -> np.ndarray:
        if self._mean is None:
            mean = self.sum() / self._frame_count
            self._mean = mean.astype(self._precision_dtype)
        return self._mean

    def std(self) -> np.ndarray:
        if self._std is None:
            squares_sum = np.zeros(
                shape=self.frame_shape,
                dtype=self._precision_dtype,
            )
            self._frames.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for index in range(self._frame_count):
                frame = self._frames.read()[1]
                mean_diff = frame - self.mean()
                squares_sum += np.square(mean_diff)
            self._std = np.sqrt(squares_sum / self._frame_count)
            self._current_frame = self._frame_count
        return self._std

    def get_frame(self, i: Optional[int] = None) -> np.ndarray:
        if i is not None and self._current_frame != i:
            self._frames.set(cv2.CAP_PROP_POS_FRAMES, i)
            self._current_frame = i
        _, frame = self._frames.read()
        self._current_frame += 1
        return frame

    def get_frame_time(self, i: Optional[int] = None) -> float:
        if i is not None:
            self.get_frame(i=i)
        frame_time = self._frames.get(cv2.CAP_PROP_POS_MSEC) / 1000
        return frame_time
