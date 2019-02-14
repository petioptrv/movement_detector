from abc import ABC, abstractmethod

import numpy as np
import cv2


class AbstractVideo(ABC):
    def __init__(self, file_path: str = None):
        super().__init__()
        self.file_path = file_path
        self.frame_count: int = None
        pass

    @abstractmethod
    def current_frame(self):
        pass

    @abstractmethod
    def next_frame(self):
        pass

    @abstractmethod
    def reset_frames(self):
        pass


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


class OpenCvVideo(AbstractVideo):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.video = cv2.VideoCapture(self.file_path)
        self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frames_bgr: np.ndarray = None
        self.frames_grey: np.ndarray = None
        self._frame_idx = 0

        self._buffer_video()

    def _buffer_video(self):
        ret, frame_bgr = self.video.read()
        bgr_array_shape = [self.frame_count] + list(frame_bgr.shape)
        grey_array_shape = bgr_array_shape[:-1]  # remove last dimension for BGR elements
        self.frames_bgr = np.ndarray(bgr_array_shape)
        self.frames_grey = np.ndarray(grey_array_shape)

        for idx in range(1, self.frame_count):
            ret, frame_bgr = self.video.read()
            frame_grey = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            self.frames_bgr[idx] = frame_bgr
            self.frames_grey[idx] = frame_grey

    def current_frame(self) -> (np.ndarray, np.ndarray):
        return self.frames_bgr[self._frame_idx], self.frames_grey[self._frame_idx]

    def next_frame(self) -> (np.ndarray, np.ndarray):
        self._frame_idx = (self._frame_idx + 1) % self.frame_count
        return self.current_frame()

    def reset_frames(self):
        self._frame_idx = 0


