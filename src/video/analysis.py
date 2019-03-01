from abc import ABC, abstractmethod
from math import sqrt

import numpy as np
import pandas as pd

from src.video.video import AbstractVideo


class AbstractAnalyzer(AbstractVideo, ABC):
    @property
    @abstractmethod
    def meta_fields(self) -> list:
        pass

    @abstractmethod
    def meta(self, start: int, end: int = None, field: str = None) -> pd.DataFrame:
        """
        Returns the analysis metadata.
        Returns the analysis metadata under the field column for the frames between indexes start
        (inclusive) and end (exclusive).
        :param start: Start index (inclusive).
        :param end: End index (exclusive).
        :param field: Name of field data.
        :return: Pandas data frame of the metadata.
        """
        pass


class PixelChangeDetector(AbstractAnalyzer):
    def __init__(self, video: AbstractVideo):
        self.comparison_count = 1  # TODO: make this a setting when Settings class is implemented
        self._vid = video
        self._meta_data = pd.DataFrame(
            columns=['mean_diff', 'outlier', 'ref_frame', 'delta', 'flagged'],
            index=range(len(self._vid))
        )
        self._generate_meta()

    def _generate_meta(self):
        # TODO: re-write using apply once the resources object is implemented
        mean_frame = self._vid.mean()
        i = 0
        for frame in self._vid:
            self._meta_data.loc[i, 'mean_diff'] = np.mean(mean_frame - frame)
            i += 1
        std2 = sqrt((self._meta_data['mean_diff'] * self._meta_data['mean_diff']).sum() / len(self._vid)) * 2
        self._meta_data.loc[:, 'outlier'] = self._meta_data['mean_diff'].abs() > std2



    @property
    def meta_fields(self) -> list:
        return self._meta_data.columns

    def meta(self, start: int, end: int = None, field: str = None) -> pd.DataFrame:
        return self._meta_data.loc[start: end, field]

    @property
    def frame_shape(self) -> tuple:
        return self._vid.frame_shape

    @property
    def frame_rate(self) -> float:
        return self._vid.frame_rate

    def __iter__(self) -> iter:
        return self._vid.__iter__()

    def __next__(self) -> np.ndarray:
        return self._vid.__next__()

    def __len__(self) -> int:
        return self._vid.__len__()

    def __getitem__(self, item):
        return self._vid.__getitem__(item)

    def apply(self, func, *args, **kwargs) -> object:
        return self._vid.apply(func, *args, **kwargs)

    def get_frame(self, i: int) -> np.ndarray:
        return self._vid.get_frame(i)

    def mean(self) -> np.ndarray:
        return self._vid.mean()

    def std(self) -> np.ndarray:
        return self._vid.std()

    def sum(self) -> np.ndarray:
        return self._vid.sum()
