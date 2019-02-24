import cv2
import numpy as np


class fileLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.cam = cv2.VideoCapture(self.file_path)
        self.frames = np.array([self.cam.read()[1]])
        self.frame_id = -1

    def load(self):
        while 1:
            self.frame_id += 1
            ret, frame = self.cam.read()
            if not ret:
                break
            self.frames = np.vstack((self.frames, [frame]))
