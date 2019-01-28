from abc import ABC, abstractmethod

import numpy as np
import cv2


class AbstractVideo(ABC):
    def __init__(self, file_path: str = None):
        super().__init__()
        self.file_path = file_path
        pass

    @abstractmethod
    def next_frame(self) -> np.ndarray:
        pass

    @abstractmethod
    def reset_frames(self):
        pass


class OpenCvVideo(AbstractVideo):
    def __init__(self, file_path: str, buffer_at_load: bool = True):
        super().__init__(file_path)
        self.video = cv2.VideoCapture(self.file_path)
        self.frames_bgr = None
        self.frames_grey = None
        self.buffered = False
        self.buff_idx = 0

        if buffer_at_load:
            self._buffer_video()

    def _buffer_video(self):
        frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

        first_frame_bgr, first_frame_grey = self.next_frame()

        # initialize the BGR frames array
        bgr_array_shape = [frame_count] + list(first_frame_bgr.shape)
        self.frames_bgr = np.ndarray(bgr_array_shape)

        # initialize the Grey-scale array
        grey_array_shape = [frame_count] + list(first_frame_grey.shape)
        self.frames_grey = np.ndarray(grey_array_shape)

        next_frame_bgr, next_frame_grey = self.next_frame()

        while next_frame_bgr:
            self.frames_bgr[len(self.frames_bgr)] = next_frame_bgr
            self.frames_grey[len(self.frames_grey)] = next_frame_grey
            next_frame_bgr, next_frame_grey = self.next_frame()

        self.buffered = True

    def next_frame(self):
        if not self.buffered:
            ret, frame_bgr = self.video.read()
            if ret:
                frame_grey = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
                return frame_bgr, frame_grey
            else:
                return None, None
        else:
            frames = (self.frames_bgr[self.buff_idx], self.frames_grey[self.buff_idx])
            self.buff_idx += 1
            return frames

    def reset_frames(self):
        self.buff_idx = 0
