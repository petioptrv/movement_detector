import os
from pathlib import Path

import numpy as np
from typing import Sequence

import pytest
from moviepy.editor import *

from movement_detector import CvVideo
from movement_detector.utils import get_project_path

test_dir = curr_dir = Path(os.path.dirname(os.path.realpath(__file__)))


def get_video_path():
    vid_folder_path = get_project_path() / 'videos'
    if not os.path.exists(str(vid_folder_path)):
        os.makedirs(str(vid_folder_path))
    vid_path = vid_folder_path / 'test.mp4'
    return vid_path


def create_uniform_frames_video(
        path: Path,
        uniform_frame_values: Sequence,
        frame_rate: float = 30,
        resolution: tuple = (250, 250),
):
    frames = []
    for val in uniform_frame_values:
        frame = np.full(shape=resolution + (3,), fill_value=val, dtype='uint8')
        frames.append(frame)
    create_video(path=path, frames=frames, frame_rate=frame_rate)


def create_video(
        path: Path,
        frames: Sequence,
        frame_rate: float = 30,
):
    clips = []
    for frame in frames:
        clips.append(ImageClip(frame).set_duration(1 / frame_rate))
    video = concatenate(clips, method='compose')
    video.write_videofile(str(path), fps=frame_rate)


def extract_frames(path: Path):
    vid = VideoFileClip(str(path))
    frames = np.array([f for f in vid.iter_frames()])
    return frames


@pytest.fixture
def uniform_frame_values_video(request):
    if hasattr(request, 'param'):
        frame_vals = request.param
    else:
        frame_vals = None
    vid_path = get_video_path()

    frame_rate = 30
    resolution = (250, 250)
    if frame_vals is None:
        duration = 2
        frame_count = frame_rate * duration
        np.random.seed(42)
        frame_vals = np.random.randint(0, 255, (frame_count,))
    create_uniform_frames_video(
        path=vid_path,
        uniform_frame_values=frame_vals,
        frame_rate=frame_rate,
        resolution=resolution,
    )

    vid = CvVideo(file_path=vid_path)
    yield vid

    os.remove(str(vid_path))


@pytest.fixture
def video_from_frames(request):
    frames = request.param
    vid_path = get_video_path()

    frame_rate = 30
    create_video(
        path=vid_path,
        frames=frames,
        frame_rate=frame_rate,
    )

    vid = CvVideo(file_path=vid_path)
    yield vid

    os.remove(str(vid_path))