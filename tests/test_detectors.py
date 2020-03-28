import os

import pytest
import numpy as np

from movement_detector import PixelChangeFD

# =============================== BASE =========================================

classes_and_kwargs = [
    (PixelChangeFD, {'outlier_change_threshold': .2,
                     'flag_outliers_buffer': 1,
                     'movement_threshold': .2,
                     'freezing_buffer': 1,
                     'blur_ksize': 5})
]


@pytest.mark.parametrize('cls_and_kwargs', classes_and_kwargs)
def test_build_meta(cls_and_kwargs, uniform_frame_values_video):
    video = uniform_frame_values_video
    cls, kwargs = cls_and_kwargs
    detector = cls(video=video, **kwargs)

    assert not detector.meta_built

    detector.run()

    assert detector.meta_built

    os.remove(detector.meta_path)


@pytest.mark.parametrize('cls_and_kwargs', classes_and_kwargs)
def test_meta_never_rebuilt(cls_and_kwargs, uniform_frame_values_video):
    video = uniform_frame_values_video
    cls, kwargs = cls_and_kwargs
    detector = cls(video=video, **kwargs)
    detector.run()

    creation_time = os.path.getctime(detector.meta_path)

    detector.run()

    last_mod_time = os.path.getmtime(detector.meta_path)

    assert creation_time == last_mod_time

    del detector
    detector = cls(video=video, **kwargs)
    detector.run()

    last_mod_time = os.path.getmtime(detector.meta_path)

    assert creation_time == last_mod_time

    os.remove(detector.meta_path)


class Detector:
    def __init__(self, cls, video, **kwargs):
        self.detector = cls(video=video, **kwargs)

    def __enter__(self):
        self.detector.run()
        return self.detector

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.detector.meta_path)


@pytest.mark.parametrize('cls_and_kwargs', classes_and_kwargs)
def test_meta_integrity(cls_and_kwargs, uniform_frame_values_video):
    video = uniform_frame_values_video
    cls, kwargs = cls_and_kwargs
    frame_count = int(video.vid_duration * video.frame_rate)

    with Detector(cls=cls, video=video, **kwargs) as detector:
        meta = detector.meta(start=0, stop=frame_count)

        assert len(meta) == frame_count
        assert np.array_equal(meta.columns, detector.meta_fields)


@pytest.mark.parametrize('cls_and_kwargs', classes_and_kwargs)
def test_time(cls_and_kwargs, uniform_frame_values_video):
    video = uniform_frame_values_video
    cls, kwargs = cls_and_kwargs
    frame_count = int(video.vid_duration * video.frame_rate)

    with Detector(cls=cls, video=video, **kwargs) as detector:
        meta = detector.meta(start=0, stop=frame_count)

        for i in range(len(meta)):
            assert meta.loc[i, 'time'] == video.get_frame_time(i=i)


@pytest.mark.parametrize('cls_and_kwargs', classes_and_kwargs)
def test_manual_set(cls_and_kwargs, uniform_frame_values_video):
    video = uniform_frame_values_video
    cls, kwargs = cls_and_kwargs
    frame_count = int(video.vid_duration * video.frame_rate)

    with Detector(cls=cls, video=video, **kwargs) as detector:
        detector.set_freezing(10)
        detector.set_moving(20)
        meta = detector.meta(start=0, stop=frame_count)

    assert sum(meta['manual_set']) == 2
    assert meta.loc[10, 'manual_set']
    assert not meta.loc[10, 'moving']
    assert meta.loc[20, 'manual_set']
    assert meta.loc[20, 'moving']


# =========================== PixelChangeFD ====================================

class PixelChangeDetector:
    def __init__(self, video, **kwargs):
        self.detector = PixelChangeFD(video=video, **kwargs)

    def __enter__(self):
        self.detector.run()
        return self.detector

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.detector.meta_path)


frame_shape = (250, 250, 3)
white_frame = np.full(shape=frame_shape, fill_value=0, dtype='uint8')
black_frame = np.full(shape=frame_shape, fill_value=255, dtype='uint8')
half_frame = np.full(shape=frame_shape, fill_value=0, dtype='uint8')
half_frame[:125, :] = 255


@pytest.mark.parametrize(
    'video_from_frames',
    (np.array(
        [white_frame]
        + [half_frame]
        + [white_frame] * 2
    ),),
    indirect=True,
)
def test_change_ratio(video_from_frames):
    video = video_from_frames
    kwargs = {
        'outlier_change_threshold': .2,
        'flag_outliers_buffer': 2,
        'movement_threshold': .2,
        'freezing_buffer': 2,
        'blur_ksize': 5,
    }
    with PixelChangeDetector(video=video, **kwargs) as detector:
        meta = detector.meta(start=0, stop=len(detector.video))

    assert np.isclose(meta.loc[0, 'change_ratio'], 0, atol=.01)
    assert np.isclose(meta.loc[1, 'change_ratio'], .5, atol=.01)
    assert np.isclose(meta.loc[2, 'change_ratio'], .5, atol=.01)
    assert np.isclose(meta.loc[3, 'change_ratio'], 0, atol=.01)


@pytest.mark.parametrize(
    'video_from_frames',
    (np.array(
        [white_frame, black_frame]
        + [white_frame, half_frame]
        + [white_frame, black_frame]
        + [half_frame, white_frame, half_frame]
    ),),
    indirect=True,
)
def test_movement_detection(video_from_frames):
    video = video_from_frames
    kwargs = {
        'outlier_change_threshold': .2,
        'flag_outliers_buffer': 2,
        'movement_threshold': .6,
        'freezing_buffer': 3,
        'blur_ksize': 5,
    }
    with PixelChangeDetector(video=video, **kwargs) as detector:
        meta = detector.meta(start=0, stop=len(detector.video))

    assert np.all(meta.iloc[:-3]['moving'])
    assert not np.any(meta.iloc[-3:]['moving'])


@pytest.mark.parametrize(
    'video_from_frames',
    (np.array(
        [white_frame] * 10
        + [half_frame]
        + [white_frame] * 10
    ),),
    indirect=True,
)
def test_outlier_detection(video_from_frames):
    video = video_from_frames
    kwargs = {
        'outlier_change_threshold': 1,
        'flag_outliers_buffer': 2,
        'movement_threshold': .2,
        'freezing_buffer': 2,
        'blur_ksize': 5,
    }
    with PixelChangeDetector(video=video, **kwargs) as detector:
        meta = detector.meta(start=0, stop=len(detector.video))

    assert not meta.loc[0, 'outlier']
    assert not meta.loc[9, 'outlier']
    assert meta.loc[10, 'outlier']
    assert meta.loc[11, 'outlier']
    assert not meta.loc[12, 'outlier']
    assert not meta.loc[20, 'outlier']


@pytest.mark.parametrize(
    'video_from_frames',
    (np.array(
        [white_frame] * 10
        + [half_frame]
        + [white_frame] * 10
        + [half_frame]
        + [black_frame]
        + [white_frame]
    ),),
    indirect=True,
)
def test_outlier_flagging_buffer(video_from_frames):
    video = video_from_frames
    kwargs = {
        'outlier_change_threshold': 1,
        'flag_outliers_buffer': 3,
        'movement_threshold': .2,
        'freezing_buffer': 2,
        'blur_ksize': 5,
    }
    with PixelChangeDetector(video=video, **kwargs) as detector:
        meta = detector.meta(start=0, stop=len(detector.video))

    assert not meta.loc[10, 'flagged']
    assert not meta.loc[11, 'flagged']
    assert np.all(meta.loc[21:, 'flagged'])


@pytest.mark.parametrize(
    'video_from_frames',
    (np.array(
        [white_frame, black_frame]
        + [white_frame, half_frame]
        + [white_frame, black_frame]
        + [half_frame, white_frame, half_frame]
    ),),
    indirect=True,
)
def test_manual_set(video_from_frames):
    video = video_from_frames
    kwargs = {
        'outlier_change_threshold': .2,
        'flag_outliers_buffer': 2,
        'movement_threshold': .6,
        'freezing_buffer': 3,
        'blur_ksize': 5,
    }
    with PixelChangeDetector(video=video, **kwargs) as detector:
        detector.set_freezing(1)
        detector.set_moving(len(video) - 2)
        meta = detector.meta(start=0, stop=len(detector.video))

    assert not meta.loc[0, 'manual_set']
    assert not meta.loc[1, 'moving']
    assert meta.loc[1, 'manual_set']
    assert meta.loc[len(video) - 2, 'moving']
    assert meta.loc[len(video) - 2, 'manual_set']
