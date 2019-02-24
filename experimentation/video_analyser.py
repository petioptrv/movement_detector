import cv2
import logging
import numpy as np
import imutils

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
    """
    Skips X frames
    :param x: number of frames to skip
    """
    for i in range(0, x):
        cam.read()


def frame_preprocessing(frame: np.ndarray) -> np.ndarray:
    """
    Applies preprocessing to a frame. Converts to greyscale and applies a blur.
    :param frame: frame to process
    :return: the processed frame
    """

    # TODO: Add flicker reduction (see comments below)
    # find the location of the brightest area
    # high_loc = base_frame.argmax()
    # low_loc = base_frame.argmin()
    # cv2.BackgroundSubtractorMOG2()
    # find the location of the darkest area
    # check over multiple frames to make sure the rat isn't in the target areas
    #
    # for each following frame, make sure the colour intensities in the target areas
    # match the target areas in the base frames
    #
    # If the intensities don't match, compute the appropriate logarithmic scale to
    # remap the image's colour intensity.

    output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to GreyScale
    output = cv2.GaussianBlur(output, (21, 21), 0)  # blur the image to remove high freq noise
    return output


def frame_postprocessing(frame: np.ndarray) -> np.ndarray:
    """
    Applies postprocessing to frame. Applies a threshold and then dilates the result.
    :param frame: the to process
    :return: the processed frame
    """
    output = cv2.threshold(frame, 15, 255, cv2.THRESH_BINARY)[1]
    output = cv2.dilate(output, None, iterations=2)
    return output


def find_contours(frame: np.ndarray):
    """
    Finds contours in a frame
    :param frame: frame to search for contours
    :rtype: object
    """
    output = cv2.findContours(frame.copy(), cv2.RETR_EXTERNAL,
                              cv2.CHAIN_APPROX_SIMPLE)
    output = imutils.grab_contours(output)
    return output


video_path = 'videos/demo_video.mp4'
cam = cv2.VideoCapture(video_path)
frames = []
frame_id = -1

# skip to the part of the video with flickering
skip_frames(1000)  # 4005 for the light flickering video

# initialise the array (we will be reading at least 4 frames at a time so they need to be in the array)
frames_to_analyse = 4
for i in range(0, frames_to_analyse):
    frame_id += 1
    ret, frame = cam.read()
    frame = frame_preprocessing(frame)
    frames += [frame]

# TODO: allow user to select the base frame
base_frame = frames[0]  # This frame as a reference frame, it should contain the static background

while True:  # while there are frames
    text = "Still"
    frame_id += 1
    ret, frame = cam.read()  # read the current frame
    display_frame = frame
    frame = frame_preprocessing(frame)
    frames += [frame]
    if not ret:  # break if there is no frame left
        break

    # frame diff results
    diff = frame_diff_2(frames[frame_id - 1], frame)
    diff = frame_postprocessing(diff)


    cnts = find_contours(diff)  # get the contours

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 100:  # 250 is the min area
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Moving"

    # colour of the text is red when the rat is moving and green when the rat is still
    colour = (0, 0, 255)
    if text == 'Still':
        colour = (0, 255, 0)

    # add the rat's status in text into the frame
    cv2.putText(display_frame, "Rat Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 2)

    # cv2.imshow displays the images
    cv2.imshow('input frame', display_frame)
    cv2.imshow('frame_diff_3', diff)

    #cv2.waitKey()  # waits until the user presses a key (quit's on 'q' press)
    key = cv2.waitKey(133) & 0xFF
    if key == ord("q"):
        break

# cleanup
cv2.destroyAllWindows()