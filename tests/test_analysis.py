import os

import pytest
import numpy as np

from movement_detector import PixelChangeFD, IntervalAggregatorMA


# ======================== IntervalAggregatorMA ================================

class IntervalAggregator:
    def __init__(self, video, detector_kwargs, analyzer_kwargs):
        self.detector = PixelChangeFD(video=video, **detector_kwargs)
        self.analyzer = IntervalAggregatorMA(
            detector=self.detector,
            **analyzer_kwargs
        )

    def __enter__(self):
        self.analyzer.run()
        return self.analyzer

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(str(self.analyzer.analysis_path))
        os.remove(str(self.detector.meta_path))


@pytest.fixture
def detector_kwargs():
    kwargs = {
        'outlier_change_threshold': .2,
        'flag_outliers_buffer': 2,
        'movement_threshold': .6,
        'freezing_buffer': 3,
        'blur_ksize': 5,
    }
    return kwargs


@pytest.mark.parametrize(
    'uniform_frame_values_video',
    ([0] * 120,),  # 4 seconds
    indirect=True
)
def test_interval_splits(
        uniform_frame_values_video,
        detector_kwargs,
):
    # todo: improve the assertions
    video = uniform_frame_values_video
    analyzer_kwargs = {
        'intervals': [1, 3],
        'aggregation': np.mean,
        'include_start': True,
        'include_end': True,
    }
    all_kwargs = {
        'video': video,
        'detector_kwargs': detector_kwargs,
        'analyzer_kwargs': analyzer_kwargs,
    }

    with IntervalAggregator(**all_kwargs) as analyzer:
        analysis = analyzer.run()

    assert len(analysis) == 3
    assert analysis.loc[0, 'time'] == '(0.0, 1.0]'
    assert analysis.loc[1, 'time'] == '(1.0, 3.0]'
    assert analysis.loc[2, 'time'] == '(3.0, 4.0]'

    analyzer_kwargs['intervals'] = [1, 3]  # reset the list
    analyzer_kwargs['include_start'] = False

    with IntervalAggregator(**all_kwargs) as analyzer:
        analysis = analyzer.run()

    assert len(analysis) == 2
    assert analysis.loc[0, 'time'] == '(1.0, 3.0]'
    assert analysis.loc[1, 'time'] == '(3.0, 4.0]'

    analyzer_kwargs['intervals'] = [1, 3]  # reset the list
    analyzer_kwargs['include_start'] = True
    analyzer_kwargs['include_end'] = False

    with IntervalAggregator(**all_kwargs) as analyzer:
        analysis = analyzer.run()

    assert len(analysis) == 2
    assert analysis.loc[0, 'time'] == '(0, 1]'
    assert analysis.loc[1, 'time'] == '(1, 3]'


@pytest.mark.parametrize(
    'uniform_frame_values_video',
    (
            [255, 0] * 45       # 3 seconds movement
            + [0] * 60          # 2 seconds freezing
            + [255, 0] * 30,    # 2 second movement
    ),
    indirect=True
)
def test_interval_aggregation_functions(
        uniform_frame_values_video,
        detector_kwargs,
):
    video = uniform_frame_values_video
    analyzer_kwargs = {
        'intervals': [2, 4],
        'aggregation': np.mean,
        'include_start': True,
        'include_end': True,
    }

    with IntervalAggregator(
            video=video,
            detector_kwargs=detector_kwargs,
            analyzer_kwargs=analyzer_kwargs,
    ) as analyzer:
        analysis = analyzer.run()

    assert analysis.loc[0, 'moving'] == 1
    assert analysis.loc[1, 'moving'] == .5
    assert np.isclose(analysis.loc[2, 'moving'], .66, atol=.01)

    analyzer_kwargs['aggregation'] = np.sum

    with IntervalAggregator(
            video=video,
            detector_kwargs=detector_kwargs,
            analyzer_kwargs=analyzer_kwargs,
    ) as analyzer:
        analysis = analyzer.run()

    assert analysis.loc[0, 'moving'] == 60
    assert analysis.loc[1, 'moving'] == 30
    assert analysis.loc[2, 'moving'] == 60
