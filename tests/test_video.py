import pytest
import numpy as np

from movement_detector.video import CvVideo

from tests.conftest import create_video, extract_frames

# =============================== BASE =========================================

classes = [CvVideo]


@pytest.mark.parametrize('cls', classes)
def test_base_video_methods(cls, tmp_path):
    vid_path = tmp_path / 'test.mp4'
    np.random.seed(42)
    frame_rate = 30
    duration = 5
    frame_count = frame_rate * duration
    frame_vals = np.random.randint(0, 255, (frame_count,))
    resolution = (250, 250)
    create_video(
        path=vid_path,
        uniform_frame_values=frame_vals,
        frame_rate=frame_rate,
        resolution=resolution,
    )

    frames = extract_frames(path=vid_path)
    vid = cls(file_path=vid_path)

    # properties
    assert vid.vid_duration == duration
    assert vid.frame_shape == resolution + (3,)
    assert vid.frame_rate == frame_rate

    # magic methods
    for i, f in enumerate(vid):
        assert np.all(f == frames[i])
    assert len(vid) == frame_count
    assert np.all(vid[:2] == frames[:2])

    # other
    assert np.all(vid.sum() == frames.astype('float32').sum(axis=0))
    assert np.allclose(vid.mean(), frames.astype('float32').mean(axis=0))
    assert np.allclose(vid.std(), frames.astype('float32').std(axis=0))
    assert np.all(vid.get_frame(0) == vid[0])
    assert np.all(vid.get_frame(frame_count - 1) == vid[frame_count - 1])
    assert vid.get_frame_time(frame_rate - 1) == 1
