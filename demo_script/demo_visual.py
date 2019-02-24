import os
import math

import pims
import cv2
import numpy as np


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
    pims_vid = pims.open(video_path)
    cv2_vid = cv2.VideoCapture(video_path)
    f_sum = np.zeros(pims_vid.frame_shape, dtype=np.int32)
    f_count = 0
    while True:
        ret, frame = cv2_vid.read()
        if ret:
            f_sum += frame
            f_count += 1
        else:
            break
    f_mean = f_sum / f_count
    cv2_vid = cv2.VideoCapture(video_path)
    f_squared_diff_sum = 0
    f_count = 0
    while True:
        ret, frame = cv2_vid.read()
        if ret:
            f_squared_diff_sum += np.mean(frame - f_mean) ** 2
            f_count += 1
        else:
            break
    f_sd = math.sqrt(f_squared_diff_sum / f_count)
    while True:
        frame = get_frame(frame_idx)
        cv2.imshow('Frame', frame)
        usr_input = cv2.waitKey(0)
        if usr_input == 2424832:  # left key
            if frame_idx != 1:
                frame_idx -= 1
        if usr_input == 2555904 or usr_input == 32:
            if frame_idx != len(pims_vid) - 1:
                frame_idx += 1


if __name__ == '__main__':
    main()
