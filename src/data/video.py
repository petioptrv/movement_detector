from abc import ABC, abstractmethod

import numpy as np
import cv2


class AbstractVideo(ABC):
    def __init__(self, file_path: str = None):
        super().__init__()
        self.file_path = file_path
        self.frame_count = None
        pass

    @abstractmethod
    def next_frame(self) -> (np.array, np.array):
        """Returns two numpy array representation of the next frame in the video.
        The first array holds the BGR representation, the second contains the
        grey-scale.
        :return:
        """
        pass

    @abstractmethod
    def reset_frames(self):
        pass


class OpenCvVideo(AbstractVideo):
    """OpenCV-based implementation of the AbstractVideo class.

    Implements the AbstractVideo interface. The video is buffered on
    class creation. The video frames are stored in a numpy array.
    """
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.video = cv2.VideoCapture(self.file_path)
        self.frames_bgr = None
        self.frames_grey = None
        self._buffered = False
        self._buff_idx = -1

        self._buffer_video()

    def next_frame(self) -> (np.array, np.array):
        if not self._buffered:
            ret, frame_bgr = self.video.read()
            if ret:
                frame_grey = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
                return frame_bgr, frame_grey
            else:
                return None, None
        else:
            self._increment_buff_index()
            return self.frames_bgr[self._buff_idx], self.frames_grey[self._buff_idx]

    def reset_frames(self):
        self._buff_idx = -1

    def _buffer_video(self):
        self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

        first_frame_bgr, first_frame_grey = self.next_frame()

        # initialize the BGR frames array
        bgr_array_shape = [self.frame_count] + list(first_frame_bgr.shape)
        self.frames_bgr = np.ndarray(bgr_array_shape)

        # initialize the Grey-scale array
        grey_array_shape = [self.frame_count] + list(first_frame_grey.shape)
        self.frames_grey = np.ndarray(grey_array_shape)

        next_frame_bgr, next_frame_grey = self.next_frame()

        while next_frame_bgr:
            self.frames_bgr[len(self.frames_bgr)] = next_frame_bgr
            self.frames_grey[len(self.frames_grey)] = next_frame_grey
            next_frame_bgr, next_frame_grey = self.next_frame()

        self._buffered = True

    def _increment_buff_index(self):
        self._buff_idx = (self._buff_idx + 1) % self.frame_count
