from abc import ABC, abstractmethod

import numpy as np


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
