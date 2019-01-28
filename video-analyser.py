import cv2
import logging
import numpy as np

# create the logger object
logger = logging.getLogger('main')


def frame_diff_4(img_vvold: np.ndarray, img_vold: np.ndarray, img_old: np.ndarray, img_new: np.ndarray) \
        -> np.ndarray:
    """
    Computes the average difference between 4 frames
    :param img_vvold:
    :param img_vold:
    :param img_old:
    :param img_new:
    :return:
    """
    img_diff0 = cv2.absdiff(img_new, img_old)
    img_diff1 = cv2.absdiff(img_old, img_vold)
    img_diff2 = cv2.absdiff(img_vold, img_vvold)

    img_combination = cv2.bitwise_or(img_diff0, img_diff1)
    return cv2.bitwise_or(img_combination, img_diff2)


def frame_diff_3(img_vold: np.ndarray, img_old: np.ndarray, img_new: np.ndarray) -> np.ndarray:
    """
    computes the difference between 3 frames
    :param img_vold: the oldest frame
    :param img_old: the previous frame
    :param img_new: the newest frame
    :return: the sum of the computed differences
    """
    img_diff0 = cv2.absdiff(img_new, img_old)
    img_diff1 = cv2.absdiff(img_old, img_vold)
    return cv2.bitwise_or(img_diff0, img_diff1)


def frame_diff_2(img_old: np.ndarray, img_new: np.ndarray) -> np.ndarray:
    """
    Computes the difference between two frames
    :param img_old: the old frame
    :param img_new: the new frame
    :return: the difference between the two
    """
    return cv2.absdiff(img_new, img_old)


def skip_frames(x: int) -> None:
    for i in range(0, x):
        cam.read()


video_path = 'videos/Rat Flashing light.wmv'
cam = cv2.VideoCapture(video_path)
frames = []
frame_id = -1

# skip to the part of the video with flickering
skip_frames(4005)

# initialise the array (we will be reading at least 4 frames at a time so they need to be in the array)
frames_to_analyse = 4
for i in range(0, frames_to_analyse):
    frame_id += 1
    ret, frame = cam.read()
    frames += [frame]

base_frame = frames[0]  # This frame serves as a reference for the overall lighting

# TODO: Add flicker reduction (see comments below)
# find the location of the brightest area
# find the location of the darkest area
# check over multiple frames to make sure the rat isn't in the target areas
#
# for each following frame, make sure the colour intensities in the target areas
# match the target areas in the base frames
#
# If the intensities don't match, compute the appropriate logarithmic scale to
# remap the image's colour intensity.

while True:  # while there are frames
    frame_id += 1
    ret, frame = cam.read()  # read the current frame
    frames += [frame]
    if not ret:  # break if there is no frame left
        break

    # frame diff results
    diff4 = frame_diff_4(frames[frame_id-3], frames[frame_id-2], frames[frame_id-1], frame)
    diff3 = frame_diff_3(frames[frame_id-2], frames[frame_id-1], frame)
    diff2 = frame_diff_2(frames[frame_id-1], frame)

    # cv2.imshow displays the images
    cv2.imshow('input frame', frame)
    cv2.imshow('frame_diff_2', diff2)
    cv2.imshow('frame_diff_3', diff3)
    cv2.imshow('frame_diff_4', diff4)
    cv2.waitKey()  # waits until the user presses a key
