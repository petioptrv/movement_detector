import numpy as np

from src.video.video import AbstractVideo


class PixelChangeDetector:
    def __init__(self, video: AbstractVideo):
        self._vid = video
        self._mean_frame = self._vid.mean()
        self._frame_buffer = []
        self._frame_buffer_indices = []

    def get_frame(self, i: int) -> np.ndarray:
        self._frame_buffer = self._vid.get_frame
