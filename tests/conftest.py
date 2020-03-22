import os
from pathlib import Path

import numpy as np
from typing import Sequence
from moviepy.editor import *

test_dir = curr_dir = Path(os.path.dirname(os.path.realpath(__file__)))


def create_video(
        path: Path,
        uniform_frame_values: Sequence,
        frame_rate: float = 30,
        resolution: tuple = (250, 250),
):
    clips = []
    for val in uniform_frame_values:
        frame = np.full(shape=resolution + (3,), fill_value=val, dtype='uint8')
        clips.append(ImageClip(frame).set_duration(1 / frame_rate))
    video = concatenate(clips, method='compose')
    video.write_videofile(str(path), fps=frame_rate)


def extract_frames(path: Path):
    vid = VideoFileClip(str(path))
    frames = np.array([f for f in vid.iter_frames()])
    return frames
