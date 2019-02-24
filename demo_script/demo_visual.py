import os

import numpy as np
import pims

from src.video.video import CvVideo, PimsVideo


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(CURRENT_DIR, 'settings.txt')


frame_buffer = []
frame_idxs = []
frame_idx = 0


def process_frame(frame_idx: int):
    return 0


def annotate_frame(frame: np.ndarray):
    return 0


def get_previous_frame():
    return 0


def main():
    settings = {}
    with open(SETTINGS_PATH) as settings_file:
        for line in settings_file:
            setting_name, setting_value = line.split('=')
            settings[setting_name] = int(setting_value)
    video_path = input('Path to video: ')
    vid = CvVideo(video_path)


if __name__ == '__main__':
    vid = PimsVideo('/Users/petioptrv/Documents/Programming/Python/movement_detector/videos/flashing_light.mp4')
    main()
