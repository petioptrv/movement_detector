import pandas as pd
import numpy as np
import cv2
import imutils
from scipy import stats

from src.video.video import CvVideo


def main():
    # settings.txt = Settings()
    vid = CvVideo('/Users/petioptrv/Documents/Programming/Python/movement_detector/videos/flashing_light.mp4')
    meta_data = pd.DataFrame(columns=['contours_area', 'outlier'], index=range(len(vid)))
    prev_frame = None
    i = 0
    for frame in vid:
        if prev_frame is None:
            meta_data['contours_area'] = 0
        else:
            diff = get_diff(prev_frame, frame)
            meta_data.loc[i, 'contours_area'] = get_contours_area(diff)
        prev_frame = frame
        i += 1
    meta_data.loc[:, 'outlier'] = False
    meta_data.loc[:, 'outlier'] = meta_data['outlier'].where(stats.zscore(meta_data['contours_area']) < 2, True)
    i = 2400
    while i != len(vid):
        print('Area: {} | Outlier: {}'.format(*meta_data.iloc[i]))
        show(vid[i])
        i += 1


def get_diff(reference, compared):
    reference = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    reference = cv2.GaussianBlur(reference, (21, 21), 0)
    compared = cv2.cvtColor(compared, cv2.COLOR_BGR2GRAY)
    compared = cv2.GaussianBlur(compared, (21, 21), 0)
    diff = cv2.absdiff(reference, compared)
    diff = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)[1]
    return cv2.dilate(diff, None, iterations=2)


def get_contours_area(frame):
    contours = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    area = 0
    for contour in contours:
        area += cv2.contourArea(contour)
    return area


def show(frame):
    cv2.imshow('frame', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
