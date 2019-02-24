from abc import ABC, abstractmethod
import math

import cv2
import pims
import numpy as np

from src.common.numpy_fns import get_dtype


class AbstractVideo(ABC):
    def __init__(self):
        super().__init__()
        self.frame_shape = None
        self.frame_rate = None

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, idx):
        pass

    @abstractmethod
    def mean(self):
        pass

    @abstractmethod
    def std(self):
        pass


class CvVideo(AbstractVideo):
    def __init__(self, file_path: str):
        super().__init__()
        self._vid = cv2.VideoCapture(file_path)
        vid_height = int(self._vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        vid_width = int(self._vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_shape = (vid_height, vid_width, 3)
        self.frame_rate = self._vid.get(cv2.CAP_PROP_FPS)
        self._frame_count = len(pims.open(file_path))  # TODO: fix
        self._sum = None
        self._mean = None
        self._std = None

    def __iter__(self):
        yield self._sum()

    def __len__(self):
        return self._frame_count

    def __getitem__(self, key):
        if type(key) is slice:
            indices = range(*key.indices(self._frame_count))
            frames = np.ndarray((len(indices),) + self.frame_shape, dtype=np.uint8)
            for i in range(len(indices)):
                frames[i] = self._get_frame(indices[i])
            return frames
        elif key >= self._frame_count:
            raise IndexError('Index out of range')
        else:
            return self._get_frame(key)

    def mean(self):
        if self._mean is None:
            self._mean = self._sum() / self._frame_count
        return self._mean

    def std(self):
        if self._std is None:
            mean_dtype = get_dtype(-255)  # to make sure that 0 - 255 can be represented
            mean = self.mean().astype(mean_dtype)
            squares_sum = 0
            self._vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for index in range(self._frame_count):
                _, frame = self._vid.read()
                mean_diff = (frame - mean).mean()
                squares_sum += mean_diff * mean_diff
            self._std = math.sqrt(squares_sum / self._frame_count)
        return self._std

    def _get_frame(self, index):
        self._vid.set(cv2.CAP_PROP_POS_FRAMES, index)
        _, frame = self._vid.read()
        return frame

    def _sum(self):
        if self._sum is None:
            max_pixel_value = 255 * self._frame_count
            dtype = get_dtype(max_pixel_value)
            f_sum = np.zeros(self.frame_shape, dtype=dtype)
            self._vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for index in range(self._frame_count):
                _, frame = self._vid.read()
                f_sum += frame
            self._sum = f_sum
        return self._sum


class AbstractVideoPlayer(ABC):
    def __init__(self):
        super().__init__()
        self.playing = False

    @abstractmethod
    def load_video(self, video: AbstractVideo):
        pass

    @abstractmethod
    def play_video(self):
        pass

    @abstractmethod
    def stop_video(self):
        pass

    def trigger_video(self):
        if self.playing:
            self.stop_video()
        else:
            self.play_video()

    @abstractmethod
    def reset_video(self):
        pass
